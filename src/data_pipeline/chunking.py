import os
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
        final_chunks.append(
            {
                "metadata": {
                    "title": metadata.get("title", ""),
                    "description": metadata.get("description", ""),
                    "source": os.path.splitext(json_path)[0] + ".pdf",
                    "chunk_no": i + 1,
                    "num_chunks": len(chunks),
                    "content": chunk.text,
                },
                "content": chunker.contextualize(chunk),
            }
        )
    return final_chunks
