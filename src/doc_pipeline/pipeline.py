import os
import json
import asyncio
from pathlib import Path
from src.doc_pipeline.parser.pdf_parser import PdfParser
from src.doc_pipeline.llms import MetadataExtractor, DocumentMetadata
from src.doc_pipeline.utils import get_first_page_content
from docling_core.types.doc import DoclingDocument


class DocumentExtractionPipeline:
    def __init__(
        self,
        input_root: str = "./database",
        output_root: str = "./extracted_data",
    ):
        self.input_root = Path(input_root)
        self.output_root = Path(output_root)
        self.parser = PdfParser()
        self.metadata_extractor = MetadataExtractor()

    def chunk_document(self, dir_path: Path):
        """
        Chunk a document using ChunkingManager and save the chunks to chunks.json in the same directory.
        """
        from src.doc_pipeline.chunking.manager import ChunkingManager

        chunk_manager = ChunkingManager(output_root=self.output_root)
        chunks = chunk_manager.chunk_document(dir_path)
        # Save chunks to chunks.json in dir_path
        from src.doc_pipeline.utils import save_chunks

        output_path = dir_path / "chunks.json"
        save_chunks(chunks, str(output_path))
        return len(chunks)

    def process_pdf(self, pdf_path: Path, rel_path: Path):
        """
        Process a single PDF: parse, save document.json, images, tables, pages, and chunks.json (placeholder).
        rel_path: relative path from input_root to the PDF (e.g., harms/file_name.pdf)
        """
        output_dir = self.output_root / rel_path.parent / rel_path.stem
        output_dir.mkdir(parents=True, exist_ok=True)

        doc_json_path = output_dir / "document.json"
        if doc_json_path.exists():
            print(f"[SKIP] File already processed: {pdf_path}")
            return

        print(f"[START] Processing file: {pdf_path} (relative: {rel_path})")
        # 1. Parse PDF
        print("\t[1/3] Parsing PDF ...")
        doc = self.parser.convert_document(str(pdf_path))

        # 2. Save document as JSON
        print(f"\t[2/3] Saving JSON to: {doc_json_path}")
        self.parser.save_to_json(doc, str(doc_json_path))

        # 3. Save images, tables, and page images using the new method
        print(f"\t[3/3] Saving multimodal assets to: {output_dir}")
        self.parser.save_multimodal_assets_to_folders(doc, output_dir)
        print(f"[DONE] Finished processing: {pdf_path}\n")

    def process_pdfs(self):
        """Process all PDFs: parse, save document.json, images, tables, pages."""
        for dirpath, _, filenames in os.walk(self.input_root):
            for filename in filenames:
                if filename.lower().endswith(".pdf"):
                    pdf_path = Path(dirpath) / filename
                    rel_path = pdf_path.relative_to(self.input_root)
                    print(f"\n{'=' * 60}\n")
                    self.process_pdf(pdf_path, rel_path)

    async def generate_metadata(self, doc_json_path, output_dir: Path):
        print(f"[INFO] Generating metadata for: {doc_json_path} ...")
        doc = DoclingDocument.load_from_json(str(doc_json_path))
        first_page_content = get_first_page_content(doc)
        output = await self.metadata_extractor.run(first_page_text=first_page_content)
        document_metadata: DocumentMetadata = output.output
        metadata = {
            "title": document_metadata.title,
            "summary": document_metadata.summary,
        }
        with open(output_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

    async def batch_generate_metadata(
        self, max_concurrent_requests: int = 3, max_requests_per_minute: int = 30
    ):
        print("\n[INFO] Starting batch metadata extraction...")
        output_dirs = []
        for dirpath, _, filenames in os.walk(self.output_root):
            if "document.json" in filenames:
                output_dirs.append(Path(dirpath))
        semaphore = asyncio.Semaphore(max_concurrent_requests)

        # Rate limiting state
        request_count = 0
        window_start = asyncio.get_event_loop().time()
        lock = asyncio.Lock()

        async def rate_limited_generate_metadata(doc_json_path, output_dir):
            nonlocal request_count, window_start
            async with semaphore:
                while True:
                    async with lock:
                        now = asyncio.get_event_loop().time()
                        elapsed = now - window_start
                        if elapsed >= 60:
                            # Reset window
                            window_start = now
                            request_count = 0
                        if request_count < max_requests_per_minute:
                            request_count += 1
                            break
                        else:
                            # Wait for the remainder of the minute
                            wait_time = 60 - elapsed
                            if wait_time > 0:
                                print(
                                    f"[RATE LIMIT] Reached {max_requests_per_minute} requests/min. Waiting {wait_time:.2f} seconds..."
                                )
                            else:
                                wait_time = 1  # fallback
                    await asyncio.sleep(wait_time)
                await self.generate_metadata(doc_json_path, output_dir)

        tasks = []
        for output_dir in output_dirs:
            doc_json_path = output_dir / "document.json"
            tasks.append(rate_limited_generate_metadata(str(doc_json_path), output_dir))
        await asyncio.gather(*tasks)
        print("[INFO] Batch metadata extraction complete.\n")

    def batch_chunk_documents(self):
        print("\n[INFO] Starting batch chunking of documents...")
        output_dirs = []
        for dirpath, _, filenames in os.walk(self.output_root):
            if "chunks.json" in filenames:
                continue
            if "document.json" in filenames:
                output_dirs.append(Path(dirpath))
        for output_dir in output_dirs:
            print(f"[CHUNK] Chunking document: {output_dir}")
            chunk_count = self.chunk_document(output_dir)
            print(f"[CHUNK] Saved {chunk_count} chunks for: {output_dir}")
        print("[INFO] Batch chunking complete.\n")
