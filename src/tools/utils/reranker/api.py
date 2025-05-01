import os
import httpx
from typing import List, Dict


async def rerank_documents(
    query: str, documents: List[str], batch_size: int = 2000
) -> Dict:
    """Rerank documents using Jina API."""
    api_key = os.getenv("JINA_API_KEY")
    base_url = "https://api.jina.ai/v1/rerank"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    try:
        batches = [
            documents[i : i + batch_size] for i in range(0, len(documents), batch_size)
        ]
        all_results = []

        async with httpx.AsyncClient() as client:
            for batch_idx, batch_docs in enumerate(batches):
                request_data = {
                    "model": "jina-reranker-v2-base-multilingual",
                    "query": query,
                    "top_n": len(batch_docs),
                    "documents": batch_docs,
                }

                response = await client.post(
                    base_url, json=request_data, headers=headers
                )

                if response.status_code == 200:
                    data = response.json()
                    start_idx = batch_idx * batch_size
                    batch_results = [
                        {
                            "index": start_idx + result["index"],
                            "relevance_score": result["relevance_score"],
                        }
                        for result in data["results"]
                    ]
                    all_results.extend(batch_results)

        all_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return {"results": all_results}

    except Exception as e:
        print(f"Error in reranking documents: {e}")
        return {"results": []}
