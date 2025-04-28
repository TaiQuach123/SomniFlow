import os
import httpx
from typing import List, Optional
from urllib.parse import urljoin, urlparse

from src.tools.web.search.models import (
    SearXNGSearchResult,
    SearXNGSearchResponse,
    SearXNGSearchParams,
)


class SearXNGSearch:
    def __init__(self, base_url: str | None = None):
        if not base_url:
            self.base_url = os.getenv("SEARXNG_API_URL")
            if not self.base_url:
                raise ValueError("SEARXNG_API_URL environment variable not set")
        else:
            self.base_url = base_url

    async def search(
        self,
        query: str,
        #    max_results: int = 5,
        include_domains: List[str] = [],
        exclude_domains: List[str] = [],
        opts: Optional[SearXNGSearchParams] = None,
    ) -> SearXNGSearchResponse:
        url = urljoin(self.base_url, "/search")
        params = {"q": query, "format": "json"}

        if opts:
            params.update(opts)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                data = response.json()

            if not isinstance(data, dict) or "results" not in data:
                raise Exception("Invalid response structure from SearXNG")

            # Filter out image results
            general_results = [
                result for result in data["results"] if not result.get("img_src")
            ]

            # Apply domain filters
            if include_domains or exclude_domains:
                general_results = [
                    result
                    for result in general_results
                    if self._check_domain_filters(
                        result["url"], include_domains, exclude_domains
                    )
                ]

            general_results: List[SearXNGSearchResult] = [
                SearXNGSearchResult(**result) for result in general_results
            ]

            return SearXNGSearchResponse(results=general_results)  # type: ignore

        except Exception as e:
            print(f"Error: {e}")

            return SearXNGSearchResponse(results=[])  # type: ignore

    def _check_domain_filters(
        self, url: str, include_domains: List[str], exclude_domains: List[str]
    ):
        try:
            domain = urlparse(url).netloc
            if include_domains and domain not in include_domains:
                return False
            if exclude_domains and domain in exclude_domains:
                return False
            return True

        except ValueError:
            return False
