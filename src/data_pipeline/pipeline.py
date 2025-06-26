import os
import json
from src.data_pipeline.chunking import chunk_document
from src.data_pipeline.converters.pdf_to_json import PdfToJsonConverter
from src.data_pipeline.extractors.llm_metadata import LlmMetadataExtractor
from src.data_pipeline.converters.json_to_markdown import JsonToMarkdownConverter
from src.data_pipeline.config import data_pipeline_config
import asyncio
from math import ceil


class DataPipeline:
    def __init__(
        self,
        embedding_model_name: str = data_pipeline_config.embedding_model_name,
        max_tokens: int = data_pipeline_config.max_tokens,
    ):
        self.embedding_model_name = embedding_model_name
        self.max_tokens = max_tokens
        self.pdf_to_json_converter = PdfToJsonConverter()
        self.llm_metadata_extractor = LlmMetadataExtractor()
        self.json_to_markdown_converter = JsonToMarkdownConverter()

    def create_chunks(self, json_path: str):
        """Create chunks for a document from its JSON representation."""
        return chunk_document(
            json_path,
            model_name=self.embedding_model_name,
            max_tokens=self.max_tokens,
        )

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
                if filename.lower().endswith(".json") and not filename.lower().endswith(
                    "_metadata.json"
                ):
                    json_files.append(os.path.join(dirpath, filename))

        batch_size = 15
        total_batches = ceil(len(json_files) / batch_size)

        for batch_idx in range(total_batches):
            batch = json_files[batch_idx * batch_size : (batch_idx + 1) * batch_size]
            start_time = asyncio.get_event_loop().time()
            for json_path in batch:
                metadata = await self.llm_metadata_extractor.extract(json_path)
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
