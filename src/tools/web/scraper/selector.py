import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional
from langchain_core.documents import Document
from src.tools.utils.chunking import split_document_by_headers, jina_length_function
from src.tools.utils.embeddings.api import (
    get_api_passage_embeddings,
    get_api_query_embeddings,
)


@dataclass
class SnippetConfig:
    chunk_size: int = 128
    chunk_overlap: int = 0
    max_tokens: int = 8192
    window_size: int = 2
    top_k: int = 5


@dataclass
class SelectedSnippet:
    content: str
    start_index: int
    end_index: int


@dataclass
class WebPageSnippets:
    url: str
    title: str
    description: str
    snippets: List[SelectedSnippet]


class SemanticSnippetSelector:
    def __init__(self, config: Optional[SnippetConfig] = None):
        self.config = config or SnippetConfig()

    @staticmethod
    def _cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> np.array:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(vec_a, vec_b.T)

        return dot_product

    @staticmethod
    def _enrich_chunks(
        chunks: List[Document], length_function=jina_length_function
    ) -> List[Document]:
        headers = []
        enriched_chunks = []
        for i, chunk in enumerate(chunks):
            metadata = ""
            unused_headers = []
            for k, v in chunk.metadata.items():
                if f"{k} {v}" not in headers:
                    headers.append(f"{k} {v}")
                    metadata += f"{k} {v}\n"
                else:
                    unused_headers.append(f"{k} {v}")
            chunk_content = f"{metadata.strip()}\n{chunk.page_content}"

            if unused_headers:
                unused_headers = "\n".join(unused_headers) + "\n"
            else:
                unused_headers = ""

            enriched_chunks.append(
                Document(
                    page_content=chunk_content.strip(),
                    metadata={
                        "num_tokens": length_function(chunk_content.strip()),
                        "unused_headers": unused_headers,
                        "num_unused_tokens": length_function(unused_headers),
                    },
                )
            )
        return enriched_chunks

    def _create_chunks(
        self, context: str, chunk_size: int = 512, chunk_overlap: int = 0
    ) -> List[Document]:
        """Split text into chunks of specified size."""
        chunks: List[Document] = split_document_by_headers(
            context,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        return chunks

    def _create_batches(
        self, chunks: List[Document], max_tokens: int = 8192
    ) -> List[List[str]]:
        """Create batches of chunks to stay under token limit."""
        i = 0
        j = 0
        total_tokens = 0
        batches = []
        chunks_content = [chunk.page_content for chunk in chunks]
        while j < len(chunks):
            total_tokens += chunks[j].metadata["num_tokens"]
            if total_tokens > max_tokens:
                batches.append(chunks_content[i:j])
                chunks_content[j] = (
                    chunks[j].metadata["unused_headers"] + chunks[j].page_content
                )

                total_tokens = (
                    chunks[j].metadata["num_tokens"]
                    + chunks[j].metadata["num_unused_tokens"]
                )

                i = j
            j += 1

        batches.append(chunks_content[i:j])

        return batches

    def _get_windowed_indexes(
        self,
        similarities: np.ndarray,
        window_size: int = 1,
        top_k: int = 3,
    ) -> List[tuple[int, int]]:
        sorted_indexes = np.argsort(similarities)[::-1]
        length = len(sorted_indexes)
        top_k_sorted_indexes = sorted_indexes[:top_k]
        selected_chunks = set()
        for center_idx in top_k_sorted_indexes:
            start_idx = max(0, center_idx - window_size)
            end_idx = min(center_idx + window_size + 1, length)
            selected_chunks.update(range(start_idx, end_idx))

        selected_chunks = sorted(list(selected_chunks))
        windows = []

        start = selected_chunks[0]
        prev = start

        for curr in selected_chunks[1:]:
            if curr != prev + 1:
                windows.append((start, prev + 1))
                start = curr
            prev = curr

        windows.append((start, prev + 1))

        return windows

    def _get_combined_content(self, snippets: List[SelectedSnippet]) -> str:
        return "\n\n".join(
            [
                f"Snippet {i + 1}: {snippet.content}"
                for i, snippet in enumerate(snippets)
            ]
        )

    def _format_web_page_content(self, web_page_snippets: WebPageSnippets) -> str:
        url = web_page_snippets.url
        title = web_page_snippets.title
        description = web_page_snippets.description
        content = self._get_combined_content(web_page_snippets.snippets)
        return f"{title}\nURL: {url}\nDescription: {description}\n\n{content}\n===\n"

    async def select_snippets(
        self,
        query: str,
        context: str,
        url: str,
        title: str,
        description: str,
        options: Optional[Dict] = None,
    ) -> WebPageSnippets:
        """
        Select most relevant snippets from context based on query.

        Args:
            query: The query to match against
            context: The full context text to extract snippets from
            options: Optional configuration overrides

        Returns:
            List of SelectedSnippet containing the most relevant text segments
        """
        if not query.strip():
            raise ValueError("Query cannot be empty")

        # Apply any option overrides
        if options:
            config = SnippetConfig(**{**self.config.__dict__, **options})
        else:
            config = self.config

        try:
            # Create and process chunks
            chunks = self._create_chunks(
                context, config.chunk_size, config.chunk_overlap
            )
            enriched_chunks = self._enrich_chunks(chunks)
            chunk_batches = self._create_batches(enriched_chunks, config.max_tokens)

            # Get embeddings for all chunks
            all_chunk_embeddings = np.empty((0, 1024))
            for batch in chunk_batches:
                batch_embeddings = await get_api_passage_embeddings(batch)
                all_chunk_embeddings = np.concatenate(
                    (all_chunk_embeddings, batch_embeddings), axis=0
                )

            # Get query embedding
            question_embedding = await get_api_query_embeddings([query])

            # Calculate similarities
            similarities = self._cosine_similarity(
                question_embedding, all_chunk_embeddings
            )[0]

            # print("Similarities:", similarities)

            windows = self._get_windowed_indexes(
                similarities, window_size=config.window_size, top_k=config.top_k
            )
            # print("Windows:", windows)
            snippets = []
            for window in windows:
                snippet = SelectedSnippet(
                    content="\n".join(
                        [
                            chunk.page_content
                            for chunk in enriched_chunks[window[0] : window[1]]
                        ]
                    ),
                    start_index=window[0],
                    end_index=window[1],
                )
                snippets.append(snippet)

            web_page_snippets = WebPageSnippets(
                url=url, title=title, description=description, snippets=snippets
            )

            return web_page_snippets

        except Exception as e:
            raise Exception(f"Error selecting snippets: {e}")
