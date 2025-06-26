from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from src.data_pipeline.converters.base import BaseConverter
from src.data_pipeline.converters.pdf_config import get_pdf_pipeline_options


class PdfToJsonConverter(BaseConverter):
    def __init__(self):
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=get_pdf_pipeline_options(),
                )
            }
        )

    def convert_and_save(self, input_path: str, output_path: str) -> None:
        print(f"Converting {input_path} to JSON...")
        doc = self.converter.convert(input_path).document
        doc.save_as_json(output_path)
