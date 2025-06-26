from docling_core.types.doc.document import DoclingDocument, ImageRefMode
from docling_core.transforms.serializer.markdown import (
    MarkdownParams,
    MarkdownDocSerializer,
)
from src.data_pipeline.config import data_pipeline_config
from src.data_pipeline.serializers import AnnotationImageSerializer
from src.data_pipeline.converters.base import BaseConverter


def convert_json_to_markdown(json_path: str) -> str:
    """Convert a JSON document to Markdown string."""
    if not json_path.endswith(".json"):
        raise ValueError("File must be a JSON file")

    doc = DoclingDocument.load_from_json(json_path)
    serializer = MarkdownDocSerializer(
        doc=doc,
        picture_serializer=AnnotationImageSerializer(),
        params=MarkdownParams(
            image_mode=ImageRefMode.PLACEHOLDER,
            image_placeholder="",
            include_annotations=False,
            page_break_placeholder=data_pipeline_config.page_break_placeholder,
        ),
    )
    ser_result = serializer.serialize()
    return ser_result.text


class JsonToMarkdownConverter(BaseConverter):
    @staticmethod
    def convert_and_save(input_path: str, output_path: str) -> None:
        markdown = convert_json_to_markdown(input_path)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown)

    @staticmethod
    def extract_first_page_content(json_path: str) -> str:
        ser_text = convert_json_to_markdown(json_path)
        return ser_text.split(data_pipeline_config.page_break_placeholder)[0]
