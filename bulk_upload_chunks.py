import os
import json
import argparse
import asyncio
from langchain_core.documents import Document
from src.tools.rag.utils import upload_points_per_doc, create_vector_store

from src.tools.utils.resource_manager import get_resource_manager


async def process_category(
    category_path, category_name, client, model, tokenizer, sparse_model
):
    await create_vector_store(client, category_name)
    for doc_folder in os.listdir(category_path):
        doc_path = os.path.join(category_path, doc_folder)
        if not os.path.isdir(doc_path):
            continue
        chunks_path = os.path.join(doc_path, "chunks.json")
        if not os.path.exists(chunks_path):
            print(f"No chunks.json in {doc_path}, skipping.")
            continue
        with open(chunks_path, "r") as f:
            chunks_data = json.load(f)
        chunks = [
            Document(page_content=chunk["content"], metadata=chunk.get("metadata", {}))
            for chunk in chunks_data
        ]
        print(
            f"Uploading {len(chunks)} chunks from {chunks_path} to collection {category_name}"
        )
        await upload_points_per_doc(
            chunks=chunks,
            client=client,
            collection_name=category_name,
            model=model,
            tokenizer=tokenizer,
            sparse_model=sparse_model,
        )


async def main(root_dir):
    resource_manager = get_resource_manager()
    resource_manager.initialize_models()
    resource_manager.initialize_client()

    client = resource_manager.qdrant_client
    tokenizer = resource_manager.tokenizer
    sparse_model = resource_manager.sparse_model
    model = resource_manager.dense_model

    for category in os.listdir(root_dir):
        category_path = os.path.join(root_dir, category)
        if not os.path.isdir(category_path):
            continue
        print(f"Processing category: {category}")
        await process_category(
            category_path, category, client, model, tokenizer, sparse_model
        )
    print("All done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Bulk upload document chunks to Qdrant vectorstores."
    )
    parser.add_argument(
        "root_dir", type=str, help="Root directory containing category subfolders."
    )
    args = parser.parse_args()
    asyncio.run(main(args.root_dir))
