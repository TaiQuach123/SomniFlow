import os
import json
from typing import Any
from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from docling_core.types.doc.document import DoclingDocument
from transformers import AutoTokenizer
from src.data_pipeline.serializers import MarkdownChunkingSerializerProvider
from src.data_pipeline.config import data_pipeline_config


def chunk_document(
    json_path: str,
    metadata: dict[str, Any],
    model_name: str = data_pipeline_config.embedding_model_name,
    max_tokens: int = data_pipeline_config.max_tokens,
):
    """Load a JSON document and yield its chunks."""
    final_chunks = []

    doc = DoclingDocument.load_from_json(json_path)
    huggingface_tokenizer = HuggingFaceTokenizer(
        tokenizer=AutoTokenizer.from_pretrained(model_name, padding_side="left"),
        max_tokens=max_tokens,
    )
    chunker = HybridChunker(
        tokenizer=huggingface_tokenizer,
        serializer_provider=MarkdownChunkingSerializerProvider(),
    )
    chunk_iter = chunker.chunk(doc)
    chunks = list(chunk_iter)
    for i, chunk in enumerate(chunks):
        # Construct the source path in the ./database/ directory, replacing the root folder
        norm_path = os.path.normpath(json_path)
        parts = norm_path.split(os.sep)
        # Remove the first folder (root), keep the rest
        sub_path = os.path.join(*parts[1:]) if len(parts) > 1 else parts[0]
        sub_path_no_ext = os.path.splitext(sub_path)[0]
        source_pdf_path = os.path.join("./database", sub_path_no_ext + ".pdf")
        final_chunks.append(
            {
                "metadata": {
                    "title": metadata.get("title", ""),
                    "summary": metadata.get("summary", ""),
                    "source": source_pdf_path,
                    "chunk_no": i + 1,
                    "num_chunks": len(chunks),
                    "contextualized_content": chunker.contextualize(chunk),
                },
                "content": chunk.text,
            }
        )
    return final_chunks


def chunk_and_save(json_path: str):
    """
    Chunk a document and save the result in the same folder as the input JSON, using the _chunks.json suffix.
    Args:
        json_path: Path to the input JSON file.
    """
    if not json_path.endswith(".json"):
        raise ValueError("Invalid JSON path")
    metadata_path = json_path.replace(".json", "_metadata.json")
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    # Create chunks
    chunks = chunk_document(json_path, metadata)
    # Prepare output path in the same folder
    base = os.path.splitext(os.path.basename(json_path))[0]
    output_dir = os.path.dirname(json_path)
    output_path = os.path.join(output_dir, f"{base}_chunks.json")
    # Save chunks
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(chunks)} chunks to {output_path}")
