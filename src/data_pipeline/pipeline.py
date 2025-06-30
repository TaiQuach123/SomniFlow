import os
import json
import asyncio
from math import ceil
from src.data_pipeline.chunking import chunk_document, chunk_and_save
from src.data_pipeline.converters.pdf_to_json import PdfToJsonConverter
from src.data_pipeline.agents.extractor.metadata_extractor import MetadataExtractor
from src.data_pipeline.converters.json_to_markdown import JsonToMarkdownConverter
from src.data_pipeline.config import data_pipeline_config
from src.data_pipeline.agents.enricher.context_enricher import ContextEnricher
from src.data_pipeline.agents.enricher.models import Context


class DataPipeline:
    def __init__(
        self,
        embedding_model_name: str = data_pipeline_config.embedding_model_name,
        max_tokens: int = data_pipeline_config.max_tokens,
    ):
        self.embedding_model_name = embedding_model_name
        self.max_tokens = max_tokens
        self.pdf_to_json_converter = PdfToJsonConverter()
        self.metadata_extractor = MetadataExtractor()
        self.json_to_markdown_converter = JsonToMarkdownConverter()

    def convert_folder_pdfs_to_json(
        self, input_folder: str, output_root: str = "extracted_data"
    ) -> None:
        """
        Recursively convert all PDFs in input_folder (and sub-folders) to JSON files,
        preserving the folder structure under output_root.
        """
        for dirpath, _, filenames in os.walk(input_folder):
            rel_dir = os.path.relpath(dirpath, input_folder)
            output_dir = (
                os.path.join(output_root, rel_dir) if rel_dir != "." else output_root
            )
            os.makedirs(output_dir, exist_ok=True)
            for filename in filenames:
                if filename.lower().endswith(".pdf"):
                    pdf_path = os.path.join(dirpath, filename)
                    json_filename = os.path.splitext(filename)[0] + ".json"
                    output_path = os.path.join(output_dir, json_filename)
                    self.pdf_to_json_converter.convert_and_save(pdf_path, output_path)

    async def extract_metadata_from_folder_jsons(self, input_folder: str) -> None:
        """
        Recursively extract metadata from all JSON files in input_folder (and sub-folders),
        saving the result as a new JSON file in the same folder with '_metadata' appended to the filename.
        Processes up to 15 files per minute to respect LLM API rate limits.
        """

        # Gather all JSON files to process
        json_files = []
        for dirpath, _, filenames in os.walk(input_folder):
            for filename in filenames:
                lower_filename = filename.lower()
                if lower_filename.endswith(".json") and not lower_filename.endswith(
                    "_metadata.json"
                ):
                    base_name = os.path.splitext(filename)[0]
                    metadata_filename = base_name + "_metadata.json"
                    metadata_path = os.path.join(dirpath, metadata_filename)
                    if not os.path.exists(metadata_path):
                        json_files.append(os.path.join(dirpath, filename))

        batch_size = 15
        total_batches = ceil(len(json_files) / batch_size)

        for batch_idx in range(total_batches):
            batch = json_files[batch_idx * batch_size : (batch_idx + 1) * batch_size]
            start_time = asyncio.get_event_loop().time()
            for json_path in batch:
                print(f"Extracting metadata for {json_path}")
                metadata = await self.metadata_extractor.extract(json_path)
                metadata_filename = (
                    os.path.splitext(os.path.basename(json_path))[0] + "_metadata.json"
                )
                metadata_path = os.path.join(
                    os.path.dirname(json_path), metadata_filename
                )
                with open(metadata_path, "w", encoding="utf-8") as f:
                    json.dump(metadata.dict(), f, ensure_ascii=False, indent=2)
            # Sleep for the remainder of the minute if not the last batch
            if batch_idx < total_batches - 1:
                elapsed = asyncio.get_event_loop().time() - start_time
                sleep_time = max(0, 60 - elapsed)
                if sleep_time > 0:
                    print(
                        f"Rate limit reached. Sleeping for {sleep_time:.1f} seconds..."
                    )
                    await asyncio.sleep(sleep_time)

    def chunk_folder_jsons(self, input_root: str):
        """
        Recursively chunk all JSON files in input_root (and subfolders),
        writing chunked output to the same folder with _chunks.json suffix.
        Skips files that already have a corresponding _chunks.json file.
        """
        for dirpath, _, filenames in os.walk(input_root):
            for filename in filenames:
                if filename.lower().endswith(".json"):
                    if filename.lower().endswith(
                        "_metadata.json"
                    ) or filename.lower().endswith("_chunks.json"):
                        continue
                    json_path = os.path.join(dirpath, filename)
                    base = os.path.splitext(filename)[0]
                    chunk_path = os.path.join(dirpath, f"{base}_chunks.json")
                    if os.path.exists(chunk_path):
                        continue
                    try:
                        chunk_and_save(json_path)
                    except Exception as e:
                        print(f"Failed to chunk {json_path}: {e}")

    async def enrich_folder_chunks(
        self, input_folder: str, chunk_rate_limit: int = 15
    ) -> None:
        """
        Recursively enrich all _chunks.json files in input_folder (and sub-folders),
        saving the result as a new file with '_enriched_chunks.json' suffix in the same folder.
        Processes up to chunk_rate_limit chunks per minute to respect LLM API rate limits.
        """
        # Gather all _chunks.json files to process
        chunk_files = []
        for dirpath, _, filenames in os.walk(input_folder):
            for filename in filenames:
                if filename.lower().endswith(
                    "_chunks.json"
                ) and not filename.lower().endswith("_enriched_chunks.json"):
                    base_name = os.path.splitext(filename)[0].replace("_chunks", "")
                    enriched_filename = base_name + "_enriched_chunks.json"
                    enriched_path = os.path.join(dirpath, enriched_filename)
                    if not os.path.exists(enriched_path):
                        chunk_files.append(os.path.join(dirpath, filename))

        print(chunk_files)

        enricher = ContextEnricher()
        chunk_counter = 0
        start_time = asyncio.get_event_loop().time()

        for chunk_path in chunk_files:
            print(f"Enriching chunks for {chunk_path}")
            with open(chunk_path, "r", encoding="utf-8") as f:
                chunks = json.load(f)
            enriched_chunks = []
            num_chunks = len(chunks)
            for i, chunk in enumerate(chunks):
                metadata = chunk.get("metadata", {})
                title = metadata.get("title", "")
                summary = metadata.get("summary", "")
                target_chunk = chunk.get("content", "")
                # Preceding and following context
                preceding_context = chunks[i - 1]["content"] if i > 0 else ""
                following_context = (
                    chunks[i + 1]["content"] if i < num_chunks - 1 else ""
                )
                context = Context(
                    title=title,
                    summary=summary,
                    target_chunk=target_chunk,
                    preceding_context=preceding_context,
                    following_context=following_context,
                )
                try:
                    enriched = await enricher.enrich(context)
                    chunk["context_lead_in"] = enriched.context_lead_in
                except Exception as e:
                    print(f"Failed to enrich chunk {i + 1} in {chunk_path}: {e}")
                    chunk["context_lead_in"] = ""
                enriched_chunks.append(chunk)
                chunk_counter += 1
                # Rate limiting per chunk
                if chunk_counter % chunk_rate_limit == 0:
                    elapsed = asyncio.get_event_loop().time() - start_time
                    sleep_time = max(0, 60 - elapsed)
                    if sleep_time > 0:
                        print(
                            f"Chunk rate limit reached. Sleeping for {sleep_time:.1f} seconds..."
                        )
                        await asyncio.sleep(sleep_time)
                    start_time = asyncio.get_event_loop().time()
            # Save enriched chunks
            base = os.path.splitext(os.path.basename(chunk_path))[0].replace(
                "_chunks", ""
            )
            output_path = os.path.join(
                os.path.dirname(chunk_path), f"{base}_enriched_chunks.json"
            )
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(enriched_chunks, f, ensure_ascii=False, indent=2)
            print(f"Saved {len(enriched_chunks)} enriched chunks to {output_path}")
