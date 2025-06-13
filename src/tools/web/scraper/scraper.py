from typing import List
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
from src.tools.web.scraper.config import browser_config, run_config, dispatcher


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
        try:
            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                results = await crawler.arun_many(
                    urls=urls, config=self.run_config, dispatcher=dispatcher
                )

            url_to_content = {
                result.url: result.markdown.fit_markdown if result.success else ""
                for result in results
            }

            return url_to_content

        except Exception as e:
            print(f"Error crawling URLs: {e}")
            return []
