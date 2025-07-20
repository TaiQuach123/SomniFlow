from typing import List
import torch
from transformers import AutoTokenizer, AutoModel
from qdrant_client import AsyncQdrantClient, models
from fastembed import SparseTextEmbedding
from src.tools.utils.embeddings import (
    get_passage_embeddings,
    get_sparse_embeddings,
)
from langchain_core.documents import Document
import uuid


async def upload_points_per_doc(
    chunks: List[Document],
    client: AsyncQdrantClient,
    collection_name: str,
    model: AutoModel,
    tokenizer: AutoTokenizer,
    sparse_model: SparseTextEmbedding,
):
    text_contents = [chunk.page_content for chunk in chunks]
    dense_embeddings = get_passage_embeddings(
        text_contents,
        model,
        tokenizer,
        max_tokens=8192,
        overlap_size=1024,
    )
    sparse_embeddings = get_sparse_embeddings(text_contents, sparse_model)

    for i in range(len(chunks)):
        metadata = chunks[i].metadata
        metadata["chunk_no"] = i

        sparse_vector = models.SparseVector(
            indices=sparse_embeddings[i].indices.tolist(),
            values=sparse_embeddings[i].values.tolist(),
        )
        dense_vector = dense_embeddings[i].tolist()

        try:
            await client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=str(uuid.uuid4()),
                        vector={"dense": dense_vector, "sparse": sparse_vector},
                        payload={
                            "content": chunks[i].page_content,
                            "metadata": metadata,
                        },
                    )
                ],
            )
        except Exception as e:
            print(f"Error uploading point {i}: {e}")


async def create_vector_store(client: AsyncQdrantClient, collection_name: str):
    if not await client.collection_exists(collection_name=collection_name):
        await client.create_collection(
            collection_name,
            vectors_config={
                "dense": models.VectorParams(size=2048, distance=models.Distance.DOT),
            },
            sparse_vectors_config={"sparse": models.SparseVectorParams()},
        )
        print(f"Collection {collection_name} created successfully.")
    else:
        print(f"Collection {collection_name} already exists.")
