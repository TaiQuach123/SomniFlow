from typing import List
from src.lmchunker.modules import llm_chunker_ppl


def chunker(
    text,
    small_model,
    small_tokenizer,
    methodth="ppl",
    threshold=0,
    dynamic_merge="no",
    target_size=200,
    batch_size=4096,
    max_txt_size=9000,
) -> List[str]:
    """
    Segments the given text into chunks based on the specified method and parameters.

    Parameters:
    !!! necessary
    - text: Text that needs to be segmented
    - small_model: The small language model used for segmentation
    - small_tokenizer: The tokenizer used for text tokenization
    !!! optional
    - methodth: The LLM chunking method that needs to be used, ['ppl','ms','lumber_ms']
    - threshold: The threshold for controlling PPL Chunking is inversely proportional to the chunk length; the smaller the threshold, the shorter the chunk length.
    - dynamic_merge: no or yes
    - target_size: If dynamic_merge='yes', then the chunk length value needs to be set
    - batch_size: The length of a single document processed at a time, used to optimize GPU memory usage when processing longer documents
    - max_txt_size: The total context length that can be considered or the maximum length that the GPU memory can accommodate

    Returns:
    - List[str]: A list of segmented text chunks
    """
    if methodth == "ppl":
        chunks = llm_chunker_ppl(
            text,
            small_model,
            small_tokenizer,
            threshold,
            dynamic_merge=dynamic_merge,
            target_size=target_size,
            batch_size=batch_size,
            max_txt_size=max_txt_size,
        )

    else:
        raise ValueError("Please select a valid method: ['ppl']")

    return chunks
