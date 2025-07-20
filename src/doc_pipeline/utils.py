import json
from pathlib import Path
from typing import Tuple, List
from docling_core.types.doc import DoclingDocument
from src.doc_pipeline.chunking.models import Chunk
from src.doc_pipeline.config import document_pipeline_config
from src.doc_pipeline.serializers import AnnotationImageSerializer
from docling_core.transforms.serializer.markdown import (
    MarkdownDocSerializer,
    MarkdownTableSerializer,
    MarkdownParams,
)
from docling_core.types.doc.document import ImageRefMode


def reconstruct_document(
    chunks: List[Chunk], prefix: List[str], separator: str = "\n"
) -> str:
    return separator.join([p + chunk.content for p, chunk in zip(prefix, chunks)])


def save_chunks(chunks: List[Chunk], output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump([chunk.dict() for chunk in chunks], f, ensure_ascii=False, indent=2)


def get_first_page_content(doc: DoclingDocument) -> str:
    serializer = MarkdownDocSerializer(
        doc=doc,
        picture_serializer=AnnotationImageSerializer(),
        table_serializer=MarkdownTableSerializer(),
        params=MarkdownParams(
            image_mode=ImageRefMode.PLACEHOLDER,
            image_placeholder="",
            include_annotations=False,
            page_break_placeholder=document_pipeline_config.page_break_placeholder,
        ),
    )

    res = serializer.serialize()
    pages = res.text.split(document_pipeline_config.page_break_placeholder)
    return pages[0]
