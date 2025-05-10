from typing import List
from dataclasses import dataclass
from transformers import AutoModelForCausalLM, AutoTokenizer
from langchain_core.documents import Document
from langchain_text_splitters import ExperimentalMarkdownSyntaxTextSplitter
from src.tools.utils.chunking import split_document_by_perplexity, jina_length_function


@dataclass
class PerplexityChunkingConfig:
    model: str = "Qwen/Qwen3-0.6B"
    threshold: float = 0.1
    dynamic_merge: str = "yes"
    target_size: int = 256
    batch_size: int = 1024
    max_txt_size: int = 9000


def enrich_chunks(
    chunks: List[Document], length_function=jina_length_function
) -> List[Document]:
    headers = []
    enriched_chunks = []
    for i, chunk in enumerate(chunks):
        metadata = ""
        # unused_headers = []
        for k, v in chunk.metadata.items():
            if f"{k} {v}" not in headers:
                headers.append(f"{k} {v}")
                metadata += f"{k} {v}\n"
            # else:
            #     unused_headers.append(f"{k} {v}")
        chunk_content = f"{metadata.strip()}\n{chunk.page_content}"

        # if unused_headers:
        #     unused_headers = "\n".join(unused_headers) + "\n"
        # else:
        #     unused_headers = ""

        enriched_chunks.append(
            Document(page_content=chunk_content.strip(), metadata=chunk.metadata)
        )
    return enriched_chunks


def create_perplexity_chunks(
    document: str,
    small_model: AutoModelForCausalLM,
    small_tokenizer: AutoTokenizer,
    config: PerplexityChunkingConfig | None = None,
) -> List[Document]:
    config = config or PerplexityChunkingConfig()

    new_chunks = []

    headers_to_split_on = [
        ("#", "#"),
        ("##", "##"),
        ("###", "###"),
        ("####", "####"),
        ("#####", "#####"),
        ("######", "######"),
    ]
    markdown_syntax_splitter = ExperimentalMarkdownSyntaxTextSplitter(
        headers_to_split_on
    )

    md_header_splits = markdown_syntax_splitter.split_text(document)

    for split in md_header_splits:
        content = split.page_content
        metadata = split.metadata
        chunks = split_document_by_perplexity(
            content,
            small_model,
            small_tokenizer,
            threshold=config.threshold,
            dynamic_merge=config.dynamic_merge,
            target_size=config.target_size,
            batch_size=config.batch_size,
            max_txt_size=config.max_txt_size,
        )

        for chunk in chunks:
            new_doc = Document(page_content=chunk, metadata=metadata)
            new_chunks.append(new_doc)

    enriched_chunks = enrich_chunks(new_chunks)

    return enriched_chunks
