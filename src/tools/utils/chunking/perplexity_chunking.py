from transformers import AutoModelForCausalLM, AutoTokenizer
from src.lmchunker.chunker import chunker

from dotenv import load_dotenv

load_dotenv()


def initialize_perplexity_model(model: str = "Qwen/Qwen3-0.6B", device: str = "mps"):
    small_tokenizer = AutoTokenizer.from_pretrained(model, trust_remote_code=True)
    small_model = AutoModelForCausalLM.from_pretrained(
        model, trust_remote_code=True
    ).to(device)
    small_model.eval()

    return small_model, small_tokenizer


def split_document_by_perplexity(
    text: str,
    small_model: AutoModelForCausalLM,
    small_tokenizer: AutoTokenizer,
    threshold: float = 0.0,
    dynamic_merge: str = "yes",
    target_size: int = 256,
    batch_size=1024,
    max_txt_size=4500,
) -> list:
    chunks = chunker(
        text=text,
        small_model=small_model,
        small_tokenizer=small_tokenizer,
        methodth="ppl",
        threshold=threshold,
        dynamic_merge=dynamic_merge,
        target_size=target_size,
        batch_size=batch_size,
        max_txt_size=max_txt_size,
    )
    return chunks
