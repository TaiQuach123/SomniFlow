import os
import httpx
from typing import List, Dict, Any
from urllib.parse import urlparse
from collections import defaultdict
from src.tools.web.search.models import SearXNGSearchResult, BoostedSearXNGSearchResult


class URLRanker:
    def __init__(self, jina_api_key: str | None = None):
        self.api_key = jina_api_key or os.getenv("JINA_API_KEY")
        if not self.api_key:
            raise ValueError("JINA_API_KEY not provided or found in environment")

    @staticmethod
    def extract_url_parts(url: str) -> dict:
        """Extract hostname and path segments from URL."""
        parsed = urlparse(url)
        return {
            "hostname": parsed.netloc,
            "path": parsed.path,
            "path_segments": [seg for seg in parsed.path.split("/") if seg],
        }

    @staticmethod
    def normalize_count(count: int, total: int) -> float:
        """Normalize a count relative to total."""
        return count / total if total > 0 else 0

    @staticmethod
    def count_url_parts(url_items: List[SearXNGSearchResult]) -> dict:
        """Count frequency of hostnames and path prefixes."""
        hostname_count = defaultdict(int)
        path_prefix_count = defaultdict(int)
        total_urls = len(url_items)

        for item in url_items:
            parts = URLRanker.extract_url_parts(item.url)
            hostname_count[parts["hostname"]] += 1

            # Count path prefixes
            path_segments = parts["path_segments"]
            current_path = ""
            for segment in path_segments:
                current_path += f"/{segment}"
                path_prefix_count[current_path] += 1

        return {
            "hostname_count": dict(hostname_count),
            "path_prefix_count": dict(path_prefix_count),
            "total_urls": total_urls,
        }

    async def rerank_documents(
        self, query: str, documents: List[str], batch_size: int = 2000
    ) -> Dict:
        """Rerank documents using Jina API."""

        base_url = "https://api.jina.ai/v1/rerank"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        try:
            batches = [
                documents[i : i + batch_size]
                for i in range(0, len(documents), batch_size)
            ]
            all_results = []

            async with httpx.AsyncClient() as client:
                for batch_idx, batch_docs in enumerate(batches):
                    request_data = {
                        "model": "jina-reranker-v2-base-multilingual",
                        "query": query,
                        "top_n": len(batch_docs),
                        "documents": batch_docs,
                    }

                    response = await client.post(
                        base_url, json=request_data, headers=headers
                    )

                    if response.status_code == 200:
                        data = response.json()
                        start_idx = batch_idx * batch_size
                        batch_results = [
                            {
                                "index": start_idx + result["index"],
                                "relevance_score": result["relevance_score"],
                            }
                            for result in data["results"]
                        ]
                        all_results.extend(batch_results)

            all_results.sort(key=lambda x: x["relevance_score"], reverse=True)
            return {"results": all_results}

        except Exception as e:
            print(f"Error in reranking documents: {e}")
            return {"results": []}

    async def rank_urls(
        self, query: str, url_items: List[SearXNGSearchResult], options: Dict[str, Any]
    ) -> List[BoostedSearXNGSearchResult]:
        """Rank URLs based on multiple factors."""
        # Default parameters
        freq_factor = options.get("freq_factor", 0.5)
        hostname_boost_factor = options.get("hostname_boost_factor", 0.5)
        path_boost_factor = options.get("path_boost_factor", 0.4)
        decay_factor = options.get("decay_factor", 0.8)
        jina_rerank_factor = options.get("jina_rerank_factor", 0.8)
        min_boost = options.get("min_boost", 0)
        max_boost = options.get("max_boost", 5)
        boost_hostnames = options.get("boost_hostnames", [])

        counts = self.count_url_parts(url_items)
        boosted_items = [BoostedSearXNGSearchResult(**vars(item)) for item in url_items]

        if query.strip():
            unique_content_map: Dict[str, List[int]] = {}
            for idx, item in enumerate(url_items):
                content = f"{item.title} {item.content}".strip()
                if content not in unique_content_map:
                    unique_content_map[content] = []
                unique_content_map[content].append(idx)

            unique_contents = list(unique_content_map.keys())
            rerank_results = await self.rerank_documents(query, unique_contents)

            for result in rerank_results["results"]:
                boost = result["relevance_score"] * jina_rerank_factor
                original_indices = unique_content_map[unique_contents[result["index"]]]
                for idx in original_indices:
                    boosted_items[idx].jina_rerank_boost = boost

        # Calculate scores for each item
        for item in boosted_items:
            self._calculate_item_score(
                item=item,
                counts=counts,
                freq_factor=freq_factor,
                hostname_boost_factor=hostname_boost_factor,
                path_boost_factor=path_boost_factor,
                decay_factor=decay_factor,
                boost_hostnames=boost_hostnames,
                min_boost=min_boost,
                max_boost=max_boost,
            )

        boosted_items.sort(key=lambda x: x.final_score, reverse=True)
        return boosted_items

    def _calculate_item_score(
        self,
        item: BoostedSearXNGSearchResult,
        counts: Dict,
        freq_factor: float,
        hostname_boost_factor: float,
        path_boost_factor: float,
        decay_factor: float,
        boost_hostnames: List[str],
        min_boost: float,
        max_boost: float,
    ) -> None:
        """Calculate scores for a single item."""
        parts = self.extract_url_parts(item.url)
        hostname = parts["hostname"]
        path_segments = parts["path_segments"]

        # Calculate hostname boost
        hostname_freq = self.normalize_count(
            counts["hostname_count"].get(hostname, 0), counts["total_urls"]
        )
        hostname_multiplier = 2 if hostname in boost_hostnames else 1
        item.hostname_boost = (
            hostname_freq * hostname_boost_factor * hostname_multiplier
        )

        # Calculate path boost with decay
        path_boost = 0
        current_path = ""
        for idx, segment in enumerate(path_segments):
            current_path += f"/{segment}"
            prefix_freq = self.normalize_count(
                counts["path_prefix_count"].get(current_path, 0), counts["total_urls"]
            )
            decayed_boost = prefix_freq * (decay_factor**idx) * path_boost_factor
            path_boost += decayed_boost
        item.path_boost = path_boost

        # Calculate frequency boost
        item.freq_boost = (
            self.normalize_count(item.weight, counts["total_urls"]) * freq_factor
        )

        # Calculate final score
        item.final_score = min(
            max(
                item.hostname_boost
                + item.path_boost
                + item.freq_boost
                + item.jina_rerank_boost,
                min_boost,
            ),
            max_boost,
        )

    def keep_k_per_hostname(
        results: List[BoostedSearXNGSearchResult], k: int
    ) -> List[BoostedSearXNGSearchResult]:
        """Keep top K results per hostname for diversity."""
        hostname_count: Dict[str, int] = {}
        filtered_results: List[BoostedSearXNGSearchResult] = []

        for result in results:
            hostname = URLRanker.extract_url_parts(result.url)["hostname"]
            if hostname not in hostname_count:
                hostname_count[hostname] = 0

            if hostname_count[hostname] < k:
                filtered_results.append(result)
                hostname_count[hostname] += 1

        return filtered_results
