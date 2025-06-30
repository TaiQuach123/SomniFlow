import argparse
import asyncio
from src.data_pipeline.pipeline import DataPipeline


def main():
    parser = argparse.ArgumentParser(
        description="Data Pipeline CLI for PDF conversion, metadata extraction, and chunking."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # convert-pdfs command
    convert_parser = subparsers.add_parser(
        "convert-pdfs", help="Recursively convert PDFs in a folder to JSON."
    )
    convert_parser.add_argument(
        "input_folder", type=str, help="Input folder containing PDFs."
    )
    convert_parser.add_argument(
        "--output-root",
        type=str,
        default="extracted_data",
        help="Root output folder for JSON files.",
    )

    # extract-metadata command
    extract_parser = subparsers.add_parser(
        "extract-metadata",
        help="Recursively extract metadata from JSON files in a folder.",
    )
    extract_parser.add_argument(
        "input_folder", type=str, help="Input folder containing JSON files."
    )

    # create-chunks command
    chunk_parser = subparsers.add_parser(
        "create-chunks", help="Create chunks for a single JSON document."
    )
    chunk_parser.add_argument(
        "json_path", type=str, help="Path to the JSON file to chunk."
    )

    # enrich-chunks command
    enrich_parser = subparsers.add_parser(
        "enrich-chunks", help="Recursively enrich all _chunks.json files in a folder."
    )
    enrich_parser.add_argument(
        "input_folder", type=str, help="Input folder containing _chunks.json files."
    )
    enrich_parser.add_argument(
        "--chunk-rate-limit",
        type=int,
        default=15,
        help="Max number of chunk enrichments per minute.",
    )

    # chunk-folder command
    chunk_folder_parser = subparsers.add_parser(
        "chunk-folder", help="Recursively chunk all JSON files in a folder."
    )
    chunk_folder_parser.add_argument(
        "input_folder", type=str, help="Input folder containing JSON files."
    )

    args = parser.parse_args()
    pipeline = DataPipeline()

    if args.command == "convert-pdfs":
        pipeline.convert_folder_pdfs_to_json(args.input_folder, args.output_root)
        print(
            f"PDFs in '{args.input_folder}' converted to JSON in '{args.output_root}'."
        )
    elif args.command == "extract-metadata":
        asyncio.run(pipeline.extract_metadata_from_folder_jsons(args.input_folder))
        print(f"Metadata extracted for JSON files in '{args.input_folder}'.")
    elif args.command == "create-chunks":
        chunks = pipeline.create_chunks(args.json_path)
        print(f"Chunks created for '{args.json_path}':")
        print(chunks)
    elif args.command == "enrich-chunks":
        asyncio.run(
            pipeline.enrich_folder_chunks(
                args.input_folder, chunk_rate_limit=args.chunk_rate_limit
            )
        )
        print(f"Chunks enriched for JSON files in '{args.input_folder}'.")
    elif args.command == "chunk-folder":
        pipeline.chunk_folder_jsons(args.input_folder)
        print(f"All JSON files in '{args.input_folder}' have been chunked.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
