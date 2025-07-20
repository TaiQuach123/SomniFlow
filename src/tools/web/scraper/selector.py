import asyncio
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional
from langchain_core.documents import Document
from src.tools.utils.chunking import split_document_by_headers, jina_length_function
from src.tools.utils.embeddings.api import (
    get_api_passage_embeddings,
)


@dataclass
class SnippetConfig:
    chunk_size: int = 512
    chunk_overlap: int = 0
    max_tokens: int = 8192
    window_size: int = 0
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

    @staticmethod
    def _validate_content(context: str) -> str:
        """Validate and clean content before processing."""
        if not context or not context.strip():
            raise ValueError("Context is empty or contains only whitespace")

        # Check for content length
        if len(context) > 1000000:  # 1MB limit
            print(
                f"Warning: Content is very large ({len(context)} characters), truncating..."
            )
            context = context[:1000000]

        # Check for problematic characters
        problematic_chars = [
            "\x00",
            "\x01",
            "\x02",
            "\x03",
            "\x04",
            "\x05",
            "\x06",
            "\x07",
            "\x08",
            "\x0b",
            "\x0c",
            "\x0e",
            "\x0f",
            "\x10",
            "\x11",
            "\x12",
            "\x13",
            "\x14",
            "\x15",
            "\x16",
            "\x17",
            "\x18",
            "\x19",
            "\x1a",
            "\x1b",
            "\x1c",
            "\x1d",
            "\x1e",
            "\x1f",
        ]

        for char in problematic_chars:
            if char in context:
                print(f"Warning: Found problematic character in content, removing...")
                context = context.replace(char, "")

        return context

    async def select_snippets(
        self,
        query: str,
        query_embedding: np.ndarray,
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

        if not context.strip():
            raise ValueError("Context cannot be empty")

        if query_embedding is None or query_embedding.size == 0:
            raise ValueError("Query embedding cannot be empty")

        # Validate and clean content
        context = self._validate_content(context)

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

            if not chunks:
                raise ValueError("No chunks created from context")

            print(f"Created {len(chunks)} chunks from context (length: {len(context)})")

            enriched_chunks = self._enrich_chunks(chunks)
            chunk_batches = self._create_batches(enriched_chunks, config.max_tokens)

            if not chunk_batches:
                raise ValueError("No chunk batches created")

            print(f"Created {len(chunk_batches)} batches for embedding")

            # Get embeddings for all chunks - create and start tasks immediately
            embedding_tasks = [
                asyncio.create_task(get_api_passage_embeddings(batch))
                for batch in chunk_batches
            ]

            # Await all embedding tasks
            batch_embeddings_list = await asyncio.gather(
                *embedding_tasks, return_exceptions=True
            )

            # Check for exceptions in embedding tasks
            for i, result in enumerate(batch_embeddings_list):
                if isinstance(result, Exception):
                    error_details = str(result)
                    if not error_details.strip():
                        error_details = f"Unknown error in embedding task {i}"
                    print(f"Batch {i} failed: {error_details}")
                    print(
                        f"Batch {i} content preview: {chunk_batches[i][:100] if chunk_batches[i] else 'Empty batch'}..."
                    )
                    raise Exception(f"Embedding task {i} failed: {error_details}")

            # Efficiently combine all embeddings at once
            all_chunk_embeddings = (
                np.vstack(batch_embeddings_list)
                if batch_embeddings_list
                else np.empty((0, 1024))
            )

            if all_chunk_embeddings.size == 0:
                raise ValueError("No embeddings generated")

            print(
                f"Successfully generated embeddings with shape: {all_chunk_embeddings.shape}"
            )

            # Calculate similarities
            similarities = self._cosine_similarity(
                query_embedding, all_chunk_embeddings
            )

            windows = self._get_windowed_indexes(
                similarities, window_size=config.window_size, top_k=config.top_k
            )

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

            print(f"Created {len(snippets)} snippets")

            web_page_snippets = WebPageSnippets(
                url=url, title=title, description=description, snippets=snippets
            )

            return web_page_snippets

        except Exception as e:
            error_msg = f"Error selecting snippets for URL {url}: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)
