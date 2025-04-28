from qdrant_client import AsyncQdrantClient, models


async def create_vector_store(client: AsyncQdrantClient, collection_name: str):
    if not await client.collection_exists(collection_name=collection_name):
        await client.create_collection(
            collection_name,
            vectors_config={
                "dense": models.VectorParams(
                    size=1024, distance=models.Distance.COSINE
                ),
            },
            sparse_vectors_config={"sparse": models.SparseVectorParams()},
        )
        print(f"Collection {collection_name} created successfully.")
    else:
        print(f"Collection {collection_name} already exists.")


async def add_data_to_vectorstore(
    client: AsyncQdrantClient, collection_name: str, data_path: str
):
    try:
        await client.upload_points(
            collection_name,
            points=[
                models.PointStruct(
                    id="",
                    vector={"dense": "", "sparse": ""},
                    payload={},
                )
            ],
            batch_size=1,
        )
    except:
        print("Error uploading data to vector store.")
