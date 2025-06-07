import asyncio
from typing import List, Tuple, Dict
from src.tools.web.search import SearXNGSearch, URLRanker
from src.tools.web.scraper import WebScraper, SemanticSnippetSelector
from src.tools.utils.embeddings.api import get_api_query_embeddings
from src.tools.web.search.models import BoostedSearXNGSearchResult


class WebSearchPipeline:
    def __init__(self):
        self.searcher = SearXNGSearch()
        self.ranker = URLRanker()
        self.scraper = WebScraper()
        self.snippet_selector = SemanticSnippetSelector()

    async def gather_top_ranked_urls_for_query(
        self,
        query: str,
        max_urls: int = 5,
        max_results: int = 3,
        ranking_options: dict = None,
    ) -> List[BoostedSearXNGSearchResult]:
        """Search and rank URLs for a single query, returning the top URLs and their metadata."""
        default_options = {
            "freq_factor": 0.5,
            "hostname_boost_factor": 0.5,
            "path_boost_factor": 0.4,
            "jina_rerank_factor": 0.8,
            "boost_hostnames": [],
        }
        ranking_options = ranking_options or default_options

        search_response = await self.searcher.search(query=query, max_results=max_urls)
        if not search_response.results:
            print("No search results found")
            return []

        ranked_results = await self.ranker.rank_urls(
            query, search_response.results, ranking_options
        )
        top_results = ranked_results[:max_results]
        return top_results

    async def gather_top_ranked_urls_for_queries(
        self,
        queries: List[str],
        max_urls: int = 5,
        max_results: int = 3,
        ranking_options: dict = None,
    ) -> Tuple[List[dict], List[List[BoostedSearXNGSearchResult]]]:
        """
        For a list of queries, gather top ranked URLs for each query.
        Returns:
            unique_url_summaries: List of dicts with unique url, title, and content (short description)
            per_query_top_results: List of lists, each containing top results for a query
        """
        unique_url_summaries = []
        seen_urls = set()
        tasks = [
            self.gather_top_ranked_urls_for_query(
                query=query,
                max_urls=max_urls,
                max_results=max_results,
                ranking_options=ranking_options,
            )
            for query in queries
        ]
        per_query_top_results = await asyncio.gather(*tasks)
        for top_results in per_query_top_results:
            for result in top_results:
                if result.url not in seen_urls:
                    seen_urls.add(result.url)
                    unique_url_summaries.append(
                        {
                            "url": result.url,
                            "title": result.title,
                            "content": result.content,
                        }
                    )
        return unique_url_summaries, per_query_top_results

    async def scrape_unique_urls(
        self,
        per_query_top_results: List[List[BoostedSearXNGSearchResult]],
    ) -> Dict[str, str]:
        """
        Scrape all unique URLs from the top results of all queries in parallel.
        Returns a dict mapping url -> scraped content.
        """
        unique_urls = []
        for result_list in per_query_top_results:
            for result in result_list:
                if result.url not in unique_urls:
                    unique_urls.append(result.url)
        url_to_content = await self.scraper.parallel_crawl_urls(unique_urls)

        return url_to_content

    async def get_query_embeddings_for_queries(
        self,
        queries: List[str],
    ):
        """
        Get embeddings for all queries in parallel.
        Returns a list of embeddings, one per query (same order as queries).
        """
        return await get_api_query_embeddings(queries)

    async def extract_relevant_snippets_for_query(
        self,
        query: str,
        top_ranked_results_for_query: List[BoostedSearXNGSearchResult],
        url_to_content: Dict[str, str],
        query_embedding=None,
    ):
        """
        For a given query and its top ranked results, extract relevant snippets using pre-scraped content.
        If query_embedding is provided, use it; otherwise, compute it.
        """
        if query_embedding is None:
            query_embedding = await get_api_query_embeddings([query])
        # If embedding is a list (from batch), get the first
        if isinstance(query_embedding, list):
            query_embedding = query_embedding[0]

        urls = [result.url for result in top_ranked_results_for_query]
        titles = [result.title for result in top_ranked_results_for_query]
        descriptions = [result.content for result in top_ranked_results_for_query]

        contents = [url_to_content.get(url, "") for url in urls]

        valid_data = [
            (content, url, title, desc)
            for content, url, title, desc in zip(contents, urls, titles, descriptions)
            if content.strip()
        ]

        if not valid_data:
            return []

        valid_contents, valid_urls, valid_titles, valid_descriptions = zip(*valid_data)

        snippet_tasks = [
            self.snippet_selector.select_snippets(
                query,
                query_embedding,
                content,
                url,
                title,
                description,
            )
            for content, url, title, description in zip(
                valid_contents,
                valid_urls,
                valid_titles,
                valid_descriptions,
            )
        ]

        snippets = await asyncio.gather(*snippet_tasks)

        return snippets

    async def extract_relevant_snippets_for_queries(
        self,
        queries: List[str],
        per_query_top_results: List[List[BoostedSearXNGSearchResult]],
        url_to_content: Dict[str, str],
        query_embeddings=None,
    ):
        """
        For each query and its top ranked results, extract relevant snippets using pre-scraped content and precomputed query embeddings if provided.
        Returns a list of lists of snippets, one per query (same order as queries).
        """
        if query_embeddings is None:
            query_embeddings = await self.get_query_embeddings_for_queries(queries)
        snippet_tasks = [
            self.extract_relevant_snippets_for_query(
                query, top_results, url_to_content, query_embedding
            )
            for query, top_results, query_embedding in zip(
                queries, per_query_top_results, query_embeddings
            )
        ]
        all_snippets = await asyncio.gather(*snippet_tasks)
        return all_snippets
