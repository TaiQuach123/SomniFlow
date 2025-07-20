from typing import List
import torch
import numpy as np
from transformers import AutoModel, AutoTokenizer


# Jina embeddings v4 version
def late_chunking(
    chunks: List[str], model: AutoModel, tokenizer: AutoTokenizer, separator: str = " "
) -> np.array:
    embed_text = "Passage: " + f"{separator}".join(chunks)
    tokenization = tokenizer([embed_text], return_tensors="pt").to(model.device)
    with torch.no_grad():
        with torch.autocast(device_type=model.device.type, dtype=torch.bfloat16):
            hidden_states = model.get_last_hidden_states(
                **tokenization, task_label="retrieval"
            )

    start_idx = len(tokenizer("Passage:")["input_ids"])
    chunk_embeddings = []
    for chunk in chunks:
        end_idx = start_idx + len(tokenizer(f"{separator}" + chunk)["input_ids"])
        temp = hidden_states[:, start_idx:end_idx, :]
        attention_mask = tokenization["attention_mask"][:, start_idx:end_idx]
        pooled_output = torch.sum(
            temp * attention_mask.unsqueeze(-1), dim=1
        ) / torch.sum(attention_mask, dim=1, keepdim=True)
        embedding = (
            torch.nn.functional.normalize(pooled_output, p=2, dim=1)
            .cpu()
            .float()
            .numpy()
        )
        chunk_embeddings.append(embedding[0])
        start_idx = end_idx

    return np.array(chunk_embeddings)


def long_late_chunking(
    chunks: List[str],
    model: AutoModel,
    tokenizer: AutoTokenizer,
    separator: str = "\n\n",
    max_tokens: int = 32768,
    overlap_size: int = 1024,
) -> np.array:
    save_res = []
    text = f"{separator}".join(chunks)

    if len(tokenizer("Passage: " + text)["input_ids"]) < max_tokens:
        return late_chunking(chunks, model, tokenizer, separator)

    else:
        final_embeddings = np.empty((0, 2048))
        chunks_token_length = [len(tokenizer(chunk)["input_ids"]) for chunk in chunks]
        i = 0
        j = 1

        while i < len(chunks):
            num_tokens = len(tokenizer("Passage:")["input_ids"])
            j = 1
            temp_chunks = []
            if i == 0:
                temp_chunks = []
            else:
                while (num_tokens + chunks_token_length[i - j]) < overlap_size:
                    num_tokens += chunks_token_length[i - j]
                    j += 1
                temp_chunks = chunks[i - j + 1 : i]

            while (i < len(chunks)) and (
                num_tokens + chunks_token_length[i]
            ) < max_tokens:
                temp_chunks.append(chunks[i])
                num_tokens += chunks_token_length[i]
                i += 1

            save_res.append(temp_chunks)
            temp_embeddings = late_chunking(temp_chunks, model, tokenizer, separator)
            final_embeddings = np.concatenate(
                (final_embeddings, temp_embeddings[j - 1 :, :]), axis=0
            )

    return final_embeddings


# Late chunking algorithm for Jina-embeddings-v3
# def late_chunking(
#     model, tokenizer, original_text: str, chunks: List[str], passage_adapter_mask=None
# ) -> np.ndarray:
#     new_text = model._task_instructions["retrieval.passage"] + original_text
#     tokenization = tokenizer(new_text, return_tensors="pt").to(model.device)
#     with torch.inference_mode():
#         outputs = model(**tokenization, adapter_mask=passage_adapter_mask)[0]
#         outputs = outputs.float()

#     start_idx = 1 + len(
#         tokenizer(
#             model._task_instructions["retrieval.passage"], add_special_tokens=False
#         )["input_ids"]
#     )
#     chunk_embeddings = []
#     for chunk in chunks:
#         end_idx = start_idx + len(
#             tokenizer(chunk, add_special_tokens=False)["input_ids"]
#         )
#         temp = outputs[:, start_idx:end_idx, :]
#         temp = model.roberta.mean_pooling(
#             temp, tokenization["attention_mask"][:, start_idx:end_idx]
#         )
#         temp = torch.nn.functional.normalize(temp, p=2, dim=1).cpu()
#         chunk_embeddings.append(temp[0].numpy())
#         start_idx = end_idx

#     chunk_embeddings = np.array(chunk_embeddings)
#     return chunk_embeddings


# def long_late_chunking(
#     model,
#     tokenizer,
#     passage_adapter_mask,
#     chunks: List[str],
#     max_tokens: int = 8192,
#     overlap_size: int = 512,
# ) -> np.ndarray:
#     """Implements Long Late Chunking for encoding long text documents"""
#     save_res = []
#     text = "\n\n".join(chunks)
#     # If the number of tokens is small, do regular Late Chunking
#     if (
#         len(tokenizer(text)["input_ids"])
#         + len(
#             tokenizer(
#                 model._task_instructions["retrieval.passage"], add_special_tokens=False
#             )["input_ids"]
#         )
#         < max_tokens
#     ):
#         final_embeddings = late_chunking(
#             model, tokenizer, text, chunks, passage_adapter_mask=passage_adapter_mask
#         )

#     # Perform Long Late Chunking
#     else:
#         chunks_token_length = [
#             len(tokenizer(chunk, add_special_tokens=False)["input_ids"])
#             for chunk in chunks
#         ]
#         i = 0
#         j = 1
#         final_embeddings = np.empty((0, 1024))
#         while i < len(chunks):
#             j = 1
#             num_tokens = 2
#             temp_chunks = []
#             if i == 0:
#                 temp_chunks = []
#             else:
#                 while (num_tokens + chunks_token_length[i - j]) < overlap_size:
#                     num_tokens += chunks_token_length[i - j]
#                     j += 1
#                 temp_chunks = chunks[i - j + 1 : i]

#             while (i < len(chunks)) and (
#                 (num_tokens + chunks_token_length[i]) <= max_tokens
#             ):
#                 temp_chunks.append(chunks[i])
#                 num_tokens += chunks_token_length[i]
#                 i += 1

#             save_res.append(temp_chunks)
#             temp_text = "\n\n".join(temp_chunks)
#             temp_embeddings = late_chunking(
#                 model, tokenizer, temp_text, temp_chunks, passage_adapter_mask
#             )
#             final_embeddings = np.concatenate(
#                 (final_embeddings, temp_embeddings[j - 1 :, :]), axis=0
#             )

#     return final_embeddings
