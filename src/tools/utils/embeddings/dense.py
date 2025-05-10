import torch
from typing import List
from transformers import AutoTokenizer, AutoModel
from src.tools.utils.embeddings.late_chunking import long_late_chunking


def init_dense_model(
    model_name: str = "jinaai/jina-embeddings-v3", device="mps"
) -> AutoModel:
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModel.from_pretrained(model_name, trust_remote_code=True).to(device)
    passage_task_id = model._adaptation_map["retrieval.passage"]
    passage_adapter_mask = torch.full(
        (1,), passage_task_id, dtype=torch.int32, device=model.device
    )
    model.eval()
    print("Initialized dense model.")

    return model, tokenizer, passage_adapter_mask


def get_query_embeddings(queries: List[str], model: AutoModel) -> torch.Tensor:
    return model.encode(queries, task="retrieval.query")


def get_passage_embeddings(
    chunks: List[str],
    model: AutoModel,
    tokenizer: AutoTokenizer,
    passage_apdapter_mask: torch.Tensor,
    max_tokens: int = 8192,
    overlap_size: int = 512,
) -> torch.Tensor:
    return long_late_chunking(
        model, tokenizer, passage_apdapter_mask, chunks, max_tokens, overlap_size
    )
