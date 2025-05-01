from src.tools.web.search import SearXNGSearch, URLRanker
from src.tools.web.scraper import WebScraper, SemanticSnippetSelector
import asyncio


class WebSearchPipeline:
    def __init__(self):
        self.searcher = SearXNGSearch()
        self.ranker = URLRanker()
        self.scraper = WebScraper()
        self.snippet_selector = SemanticSnippetSelector()

    async def search_and_process(
        self,
        query: str,
        max_urls: int = 10,
        max_results: int = 5,
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

            # Take top K results
            top_results = ranked_results[:max_results]

            # Scrape content
            print("Scraping content...")
            urls = [result.url for result in top_results]
            scraped_contents = await self.scraper.parallel_crawl_urls(urls)

            # Extract relevant snippets
            print("Extracting snippets...")

            valid_contents = []
            valid_urls = []

            for content, url in zip(scraped_contents, urls):
                if content.strip():
                    valid_contents.append(content)
                    valid_urls.append(url)
                else:
                    print(f"Skipping empty content for URL: {url}")

            snippet_tasks = [
                self.snippet_selector.select_snippets(query, content, url)
                for content, url in zip(valid_contents, valid_urls)
            ]
            all_snippets = await asyncio.gather(*snippet_tasks)

            return all_snippets

        except Exception as e:
            print(f"Error in pipeline: {e}")
            return []
