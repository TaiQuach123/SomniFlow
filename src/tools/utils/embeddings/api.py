import os
import httpx
import numpy as np
from typing import List
from dotenv import load_dotenv

load_dotenv()


async def get_api_query_embeddings(text: List[str]) -> np.ndarray:
    base_url = "https://api.jina.ai/v1/embeddings"
    api_key = os.getenv("JINA_API_KEY")

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    data = {
        "model": "jina-embeddings-v3",
        "task": "retrieval.query",
        "input": text,
    }
    try:
        async with httpx.AsyncClient() as client:
            data = await client.post(base_url, headers=headers, json=data)
            data = data.json()
            embeddings = np.array(
                [data["data"][i]["embedding"] for i in range(len(data["data"]))]
            )

            return embeddings
    except Exception as e:
        print(f"Error in get_api_query_embeddings: {e}")
        return None


async def get_api_passage_embeddings(chunks: List[str]) -> np.ndarray:
    base_url = "https://api.jina.ai/v1/embeddings"
    api_key = os.getenv("JINA_API_KEY")

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    data = {
        "model": "jina-embeddings-v3",
        "task": "retrieval.passage",
        "late_chunking": True,
        "input": chunks,
    }

    async with httpx.AsyncClient() as client:
        data = await client.post(base_url, headers=headers, json=data)
        data = data.json()
        embeddings = np.array(
            [data["data"][i]["embedding"] for i in range(len(data["data"]))]
        )
        return embeddings
