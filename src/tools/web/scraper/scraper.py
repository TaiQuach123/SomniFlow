from typing import List
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
from src.tools.web.scraper.config import browser_config, run_config


class WebScraper:
    def __init__(
        self,
        run_config: CrawlerRunConfig = run_config,
        browser_config: BrowserConfig = browser_config,
    ):
        self.browser_config = browser_config
        self.run_config = run_config

    async def parallel_crawl_urls(
        self,
        urls: List[str],
    ):
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            results = await crawler.arun_many(urls=urls, config=self.run_config)

        # if not results[0].success:
        #     print(f"Crawl failed: {results.error_message}")
        #     print(f"Status code: {results.status_code}")
        fit_markdowns = [result.markdown.fit_markdown for result in results]
        return fit_markdowns
