from typing import Iterable, Optional
from docling_core.transforms.chunker.base import BaseChunk
from docling_core.transforms.chunker.hierarchical_chunker import DocChunk
from docling_core.types.doc.labels import DocItemLabel


def find_chunk_by_label(
    chunks: Iterable[BaseChunk], n: int, label: DocItemLabel
) -> Optional[tuple[int, DocChunk]]:
    """Find the n-th chunk with a specific label."""
    num_found = -1
    for i, chunk in enumerate(chunks):
        doc_chunk = DocChunk.model_validate(chunk)
        for item in doc_chunk.meta.doc_items:
            if item.label == label:
                num_found += 1
                if num_found == n:
                    return i, chunk
    return None
