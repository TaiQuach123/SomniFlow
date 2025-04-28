import os
import asyncio
from typing import Literal
from qdrant_client import AsyncQdrantClient
from src.tools.rag.utils import create_vector_store


async def main(
    collection_name: Literal["suggestion", "harm", "factor"], data_path: str
):
    assert collection_name in ["suggestion", "harm", "factor"], (
        "Invalid collection name"
    )

    client = AsyncQdrantClient("http://localhost:6333")
    await create_vector_store(client, "suggestion")
    await create_vector_store(client, "harm")
    await create_vector_store(client, "factor")


if __name__ == "__main__":
    asyncio.run(main())
