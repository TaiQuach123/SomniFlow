from typing import List, Tuple
from transformers import AutoTokenizer
from pathlib import Path
import json
from docling_core.types.doc import DoclingDocument
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from src.doc_pipeline.serializers import MarkdownChunkingSerializerProvider
from src.doc_pipeline.chunking.chunker import CustomHybridChunker
from src.doc_pipeline.config import document_pipeline_config

from src.doc_pipeline.chunking.models import Chunk, ChunkMetadata


class ChunkingManager:
    def __init__(
        self,
        model_name: str = document_pipeline_config.embedding_model_name,
        max_tokens: int = document_pipeline_config.max_tokens,
        serializer_provider: MarkdownChunkingSerializerProvider = MarkdownChunkingSerializerProvider(),
        output_root: Path = Path("./extracted_data"),
    ):
        self.chunker = CustomHybridChunker(
            tokenizer=HuggingFaceTokenizer(
                tokenizer=AutoTokenizer.from_pretrained(model_name),
                max_tokens=max_tokens,
            ),
            serializer_provider=serializer_provider,
        )
        self.output_root = Path(output_root)

    def _load_doc_and_metadata(self, dir_path: Path) -> Tuple[DoclingDocument, dict]:
        """
        Given a directory path, loads document.json as a DoclingDocument and metadata.json as a dict.
        """
        doc_path = dir_path / "document.json"
        metadata_path = dir_path / "metadata.json"
        doc = DoclingDocument.load_from_json(str(doc_path))
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        return doc, metadata

    def chunk_document(self, dir_path: Path):
        """Chunk a document and return the chunks."""
        init_chunks: List[Chunk] = []
        doc, metadata = self._load_doc_and_metadata(dir_path)
        chunks = list(self.chunker.chunk(doc))
        # Compute source_pdf_path
        # Example: dir_path = <output_root>/harms/filename -> './database/harms/filename.pdf'
        rel_path = dir_path.relative_to(self.output_root)
        source_pdf_path = Path("./database") / rel_path.with_suffix(".pdf")
        for i, chunk in enumerate(chunks):
            headings = "\n".join(chunk.meta.headings) if chunk.meta.headings else ""
            init_chunks.append(
                Chunk(
                    metadata=ChunkMetadata(
                        title=metadata.get("title", ""),
                        summary=metadata.get("summary", ""),
                        source=str(source_pdf_path),
                        chunk_no=i + 1,
                        num_chunks=len(chunks),
                        headings=headings,
                    ),
                    content=chunk.text,
                )
            )
        enriched_chunks, _ = self._enrich_chunks(init_chunks)
        return enriched_chunks

    def _enrich_chunks(self, chunks: List[Chunk]) -> Tuple[List[Chunk], List[str]]:
        """Enrich chunks with headings and return the enriched chunks and the prefix."""
        enriched_chunks = []
        prefix = []
        last_heading = None
        for chunk in chunks:
            heading = getattr(chunk.metadata, "headings", "")
            prefix_header = ""
            if heading and heading != last_heading:
                if len(prefix) > 0:
                    prefix.append("\n")
                else:
                    prefix.append("")
                prefix_header = f"## {heading}\n\n"
                last_heading = heading
            else:
                prefix.append("")
            enriched_content = f"{prefix_header}{chunk.content}"
            new_metadata = ChunkMetadata(
                title=chunk.metadata.title,
                summary=chunk.metadata.summary,
                source=chunk.metadata.source,
                chunk_no=chunk.metadata.chunk_no,
                num_chunks=chunk.metadata.num_chunks,
                headings="",
            )
            enriched_chunks.append(
                Chunk(metadata=new_metadata, content=enriched_content)
            )

        return enriched_chunks, prefix
