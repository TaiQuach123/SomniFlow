import torch
from typing import List
from transformers import AutoTokenizer, AutoModel
from src.tools.utils.embeddings.late_chunking import long_late_chunking


def init_dense_model(
    model_name: str = "jinaai/jina-embeddings-v4", device="mps"
) -> AutoModel:
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModel.from_pretrained(model_name, trust_remote_code=True).to(device)
    model.eval()
    print("Initialized dense model.")

    return model, tokenizer


def get_query_embeddings(queries: List[str], model: AutoModel) -> torch.Tensor:
    return model.encode_text(queries, task="retrieval", prompt_name="query")


def get_passage_embeddings(
    chunks: List[str],
    model: AutoModel,
    tokenizer: AutoTokenizer,
    max_tokens: int = 8192,
    overlap_size: int = 512,
) -> torch.Tensor:
    return long_late_chunking(
        chunks, model, tokenizer, max_tokens=max_tokens, overlap_size=overlap_size
    )
