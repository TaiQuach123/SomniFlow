from typing import List
from transformers import AutoModel
from fastembed import SparseTextEmbedding
from qdrant_client import AsyncQdrantClient, models
from src.tools.utils.embeddings import get_query_embeddings, get_sparse_embeddings
from src.tools.utils.resource_manager import get_resource_manager


async def retrieve_batch(
    queries: List[str],
    collection_name: str,
    client: AsyncQdrantClient | None = None,
    model: AutoModel | None = None,
    sparse_model: SparseTextEmbedding | None = None,
):
    manager = get_resource_manager()
    if client is None:
        manager.initialize_client()
        client = manager.qdrant_client

    if model is None or sparse_model is None:
        manager.initialize_models()
        model = manager.dense_model
        sparse_model = manager.sparse_model

    query_dense_vectors = get_query_embeddings(queries, model)
    query_sparse_vectors = get_sparse_embeddings(queries, sparse_model)

    requests = []

    for i in range(len(queries)):
        request = models.QueryRequest(
            prefetch=[
                models.Prefetch(
                    query=query_dense_vectors[i],
                    using="dense",
                    limit=10,
                ),
                models.Prefetch(
                    query=models.SparseVector(
                        indices=query_sparse_vectors[i].indices.tolist(),
                        values=query_sparse_vectors[i].values.tolist(),
                    ),
                    using="sparse",
                    limit=10,
                ),
            ],
            query=models.FusionQuery(fusion=models.Fusion.DBSF),
            with_payload=True,
            limit=3,
        )

        requests.append(request)

    search_results = await client.query_batch_points(
        collection_name=collection_name, requests=requests
    )

    # final_results = []
    # for result in search_results:
    #     final_results.append(format_points(result.points))

    return search_results
