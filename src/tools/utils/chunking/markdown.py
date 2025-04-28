from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import (
    ExperimentalMarkdownSyntaxTextSplitter,
    MarkdownTextSplitter,
)

from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    "jinaai/jina-embeddings-v3", trust_remote_code=True
)


# Compute number of tokens with the text -> use jina embedding v3 tokenizer
def jina_length_function(text: str, tokenizer=tokenizer) -> int:
    return len(tokenizer(text)["input_ids"])


def split_document_by_headers(
    document: str,
    chunk_size: int = 512,
    chunk_overlap: int = 0,
    length_function=jina_length_function,
) -> List[Document]:
    """Use this for webpage markdown"""
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
    text_splitter = MarkdownTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=length_function,
    )

    md_header_splits = markdown_syntax_splitter.split_text(document)
    splits = text_splitter.split_documents(md_header_splits)
    return splits
