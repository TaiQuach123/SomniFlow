import argparse
import asyncio
from pathlib import Path
from src.doc_pipeline.pipeline import DocumentExtractionPipeline


def main():
    parser = argparse.ArgumentParser(
        description="Run the document extraction pipeline."
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        default="./database",
        help="Input directory containing PDF files",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./extracted_data",
        help="Output directory for extracted data",
    )
    parser.add_argument(
        "--step",
        type=str,
        choices=["parse-pdfs", "generate-metadata", "chunk-documents", "all"],
        default="all",
        help=(
            "Pipeline step to run:\n"
            "  parse-pdfs: Parse PDFs and extract document.json and assets\n"
            "  generate-metadata: Generate metadata (title, summary) for each document\n"
            "  chunk-documents: Create and save document chunks for each document\n"
            "  all: Run all steps in order"
        ),
    )
    args = parser.parse_args()

    pipeline = DocumentExtractionPipeline(
        input_root=Path(args.input_dir), output_root=Path(args.output_dir)
    )

    if args.step in ("parse-pdfs", "all"):
        print("[CLI] Parsing PDFs and extracting assets...")
        pipeline.process_pdfs()
    if args.step in ("generate-metadata", "all"):
        print("[CLI] Generating metadata asynchronously...")
        asyncio.run(pipeline.batch_generate_metadata())
    if args.step in ("chunk-documents", "all"):
        print("[CLI] Chunking documents...")
        pipeline.batch_chunk_documents()


if __name__ == "__main__":
    main()
