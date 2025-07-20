from typing import Union
from pathlib import Path
from docling_core.types.doc.document import DoclingDocument
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.layout_model_specs import DOCLING_LAYOUT_EGRET_XLARGE
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    PictureDescriptionApiOptions,
    PictureDescriptionVlmOptions,
    LayoutOptions,
)
from docling_core.types.doc import PictureItem, TableItem
from src.doc_pipeline.config import document_pipeline_config


class PdfParser:
    def __init__(self):
        self.parser = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=self._get_pdf_pipeline_options(),
                )
            }
        )

    def _get_picture_description_options(
        self, model: str, prompt: str, use_api: bool = True
    ) -> PictureDescriptionApiOptions | PictureDescriptionVlmOptions:
        if use_api:
            return PictureDescriptionApiOptions(
                url="http://localhost:1234/v1/chat/completions",
                params=dict(model=model, max_completion_tokens=500, temperature=0),
                prompt=prompt,
                timeout=90,
            )
        else:
            return PictureDescriptionVlmOptions(
                repo_id=model,
                prompt=prompt,
                generation_config=dict(max_new_tokens=500, temperature=0),
            )

    def _get_pdf_pipeline_options(
        self,
        vision_model_name: str = document_pipeline_config.vision_model_name,
        prompt: str = document_pipeline_config.image_description_prompt,
    ) -> PdfPipelineOptions:
        return PdfPipelineOptions(
            do_picture_description=True,
            enable_remote_services=document_pipeline_config.use_remote_services,
            generate_picture_images=True,
            generate_page_images=True,
            images_scale=2,
            picture_description_options=self._get_picture_description_options(
                model=vision_model_name,
                prompt=prompt,
                use_api=document_pipeline_config.use_remote_services,
            ),
            layout_options=LayoutOptions(
                model_spec=DOCLING_LAYOUT_EGRET_XLARGE,
            ),
        )

    def convert_document(self, pdf_path: str) -> DoclingDocument:
        return self.parser.convert(pdf_path).document

    def save_to_json(self, document: Union[DoclingDocument, str], output_path: str):
        if isinstance(document, str):
            doc = self.convert_document(document)
        else:
            doc = document
        doc.save_as_json(output_path)

    def save_multimodal_assets_to_folders(self, doc: DoclingDocument, output_dir: Path):
        """
        Save page images, tables, and pictures into 'pages', 'tables', and 'images' subfolders under output_dir.
        """
        (output_dir / "images").mkdir(exist_ok=True)
        (output_dir / "tables").mkdir(exist_ok=True)
        (output_dir / "pages").mkdir(exist_ok=True)

        table_counter = 0
        picture_counter = 0
        # Save page images
        for page_no, page in doc.pages.items():
            page_no = page.page_no
            page_image_filename = output_dir / "pages" / f"page_{page_no}.png"
            with page_image_filename.open("wb") as f:
                page.image.pil_image.save(f, "PNG")
        # Save tables and pictures
        for element, _ in doc.iterate_items():
            if isinstance(element, TableItem):
                table_counter += 1
                element_image_filename = (
                    output_dir / "tables" / f"table_{table_counter}.png"
                )
                with element_image_filename.open("wb") as f:
                    element.get_image(doc).save(f, "PNG")
            if isinstance(element, PictureItem):
                picture_counter += 1
                element_image_filename = (
                    output_dir / "images" / f"picture_{picture_counter}.png"
                )
                with element_image_filename.open("wb") as f:
                    element.get_image(doc).save(f, "PNG")
