import os
import asyncio
import argparse
from typing import List
from qdrant_client import AsyncQdrantClient
from src.tools.rag.utils import create_vector_store, upload_points_per_doc
from src.tools.utils.embeddings import init_sparse_model, init_dense_model
from src.tools.rag.chunking import create_perplexity_chunks
from src.tools.utils.chunking import initialize_perplexity_model


async def create_collections(client: AsyncQdrantClient, collections: List[str]):
    """Create multiple vector store collections."""
    for collection in collections:
        await create_vector_store(client, collection)


async def process_and_upload(
    client: AsyncQdrantClient,
    collection_name: str,
    data_path: str,
):
    """Process documents and upload to vector store."""
    # Initialize models
    model, tokenizer, passage_adapter_mask = init_dense_model()
    sparse_model = init_sparse_model()
    small_model, small_tokenizer = initialize_perplexity_model()

    # Process documents
    if os.path.isfile(data_path):
        files = [data_path]
    else:
        files = [
            os.path.join(data_path, f)
            for f in os.listdir(data_path)
            if f.endswith((".txt", ".md"))
        ]

    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        title = ""  ## Add logic here

        print(f"Creating chunks for {file_path} ...")
        doc_chunks = create_perplexity_chunks(content, small_model, small_tokenizer)

        doc_metadata = {
            "source": file_path,
            "title": title,
            "num_chunks": len(doc_chunks),
        }

        await upload_points_per_doc(
            chunks=doc_chunks,
            doc_metadata=doc_metadata,
            client=client,
            collection_name=collection_name,
            model=model,
            tokenizer=tokenizer,
            passage_adapter_mask=passage_adapter_mask,
            sparse_model=sparse_model,
        )


async def main():
    parser = argparse.ArgumentParser(description="Vector store operations")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Create collections command
    create_parser = subparsers.add_parser(
        "create", help="Create vector store collections"
    )
    create_parser.add_argument(
        "--collections",
        nargs="+",
        default=["suggestion", "harm", "factor"],
        help="Collections to create",
    )

    # Upload command
    upload_parser = subparsers.add_parser(
        "upload", help="Upload documents to vector store"
    )
    upload_parser.add_argument(
        "--collection", required=True, help="Collection name to upload to"
    )
    upload_parser.add_argument(
        "--data-path", required=True, help="Path to data directory or file"
    )

    args = parser.parse_args()
    client = AsyncQdrantClient("http://localhost:6333")

    if args.command == "create":
        await create_collections(client, args.collections)
    elif args.command == "upload":
        await process_and_upload(client, args.collection, args.data_path)
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
