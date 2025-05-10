from typing import List
from fastembed import SparseEmbedding, SparseTextEmbedding


def init_sparse_model():
    sparse_model_name = "prithivida/Splade_PP_en_v1"
    sparse_model = SparseTextEmbedding(model_name=sparse_model_name, batch_size=32)
    print("Initialized sparse model.")
    return sparse_model


def get_sparse_embeddings(
    text: List[str], sparse_model: SparseTextEmbedding, batch_size: int = 32
) -> List[SparseEmbedding]:
    return list(sparse_model.embed(text, batch_size=batch_size))
