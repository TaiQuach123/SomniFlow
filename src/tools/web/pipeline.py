import asyncio
from typing import List
from src.tools.web.search import SearXNGSearch, URLRanker
from src.tools.web.scraper import WebScraper, SemanticSnippetSelector


class WebSearchPipeline:
    def __init__(self):
        self.searcher = SearXNGSearch()
        self.ranker = URLRanker()
        self.scraper = WebScraper()
        self.snippet_selector = SemanticSnippetSelector()

    async def search_multiple_queries(
        self,
        queries: List[str],
        max_urls: int = 10,
        max_results: int = 3,
        ranking_options: dict = None,
    ):
        tasks = [
            self.search_extract_snippets(
                query=query,
                max_urls=max_urls,
                max_results=max_results,
                ranking_options=ranking_options,
            )
            for query in queries
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

    async def search_extract_snippets(
        self,
        query: str,
        max_urls: int = 5,
        max_results: int = 3,
        ranking_options: dict = None,
    ):
        """Execute complete pipeline of search, rank, scrape and extract snippets."""

        default_options = {
            "freq_factor": 0.5,
            "hostname_boost_factor": 0.5,
            "path_boost_factor": 0.4,
            "jina_rerank_factor": 0.8,
            "boost_hostnames": [],
        }
        ranking_options = ranking_options or default_options

        try:
            # Search
            print(f"Searching for query: {query}")
            search_response = await self.searcher.search(
                query=query, max_results=max_urls
            )
            if not search_response.results:
                print("No search results found")
                return []

            # Rank URLs
            print("Ranking results...")
            ranked_results = await self.ranker.rank_urls(
                query, search_response.results, ranking_options
            )
            print("Finished ranking results")

            # Take top K results
            top_results = ranked_results[:max_results]

            # Scrape content
            print("Scraping content...")
            urls = [result.url for result in top_results]
            titles = [result.title for result in top_results]
            descriptions = [result.content for result in top_results]
            scraped_contents = await self.scraper.parallel_crawl_urls(urls)
            print("Finished scraping content")

            # Extract relevant snippets
            print("Extracting snippets...")

            valid_contents = []
            valid_urls = []
            valid_titles = []
            valid_descriptions = []

            for content, url, title, description in zip(
                scraped_contents, urls, titles, descriptions
            ):
                if content.strip():
                    valid_contents.append(content)
                    valid_urls.append(url)
                    valid_titles.append(title)
                    valid_descriptions.append(description)
                else:
                    print(f"Skipping empty content for URL: {url}")

            snippet_tasks = [
                self.snippet_selector.select_snippets(
                    query, content, url, title, description
                )
                for content, url, title, description in zip(
                    valid_contents, valid_urls, valid_titles, valid_descriptions
                )
            ]
            all_snippets = await asyncio.gather(*snippet_tasks)
            print("Finished extracting snippets")

            return all_snippets

        except Exception as e:
            print(f"Error in pipeline: {e}")
            return []
