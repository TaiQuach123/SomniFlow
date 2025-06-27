import torch
import torch.nn.functional as F
from torch import Tensor
from transformers import AutoTokenizer, AutoModel
from typing import List

task = "Given a web search query, retrieve relevant passages that answer the query"


def last_token_pool(last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
    left_padding = attention_mask[:, -1].sum() == attention_mask.shape[0]
    if left_padding:
        return last_hidden_states[:, -1]
    else:
        sequence_lengths = attention_mask.sum(dim=1) - 1
        batch_size = last_hidden_states.shape[0]
        return last_hidden_states[
            torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths
        ]


def get_detailed_instruct(task_description: str, query: str) -> str:
    return f"Instruct: {task_description}\nQuery:{query}"


tokenizer = AutoTokenizer.from_pretrained(
    "Qwen/Qwen3-Embedding-0.6B", padding_side="left"
)
model = AutoModel.from_pretrained("Qwen/Qwen3-Embedding-0.6B")


def get_query_embeddings(queries: List[str], task: str = task) -> Tensor:
    input_texts = [get_detailed_instruct(task, query) for query in queries]
    batch_dict = tokenizer(
        input_texts, padding=True, truncation=True, max_length=8192, return_tensors="pt"
    ).to(model.device)

    outputs = model(**batch_dict)
    embeddings = last_token_pool(
        outputs.last_hidden_state, batch_dict["attention_mask"]
    )
    embeddings = F.normalize(embeddings, p=2, dim=1)

    return embeddings


def get_passage_embeddings(passages: List[str]) -> Tensor:
    batch_dict = tokenizer(
        passages, padding=True, truncation=True, max_length=8192, return_tensors="pt"
    ).to(model.device)

    outputs = model(**batch_dict)
    embeddings = last_token_pool(
        outputs.last_hidden_state, batch_dict["attention_mask"]
    )
    embeddings = F.normalize(embeddings, p=2, dim=1)

    return embeddings
