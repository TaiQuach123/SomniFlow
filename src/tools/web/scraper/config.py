from pydantic_settings import BaseSettings
from crawl4ai import (
    CrawlerRunConfig,
    CacheMode,
    LXMLWebScrapingStrategy,
)
from crawl4ai.async_configs import BrowserConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter

# from crawl4ai import RateLimiter
# from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher
from typing import List
from functools import lru_cache


class ScraperSettings(BaseSettings):
    # Browser settings
    browser_headless: bool = True

    # Content filtering settings
    pruning_threshold: float = 0.2
    pruning_threshold_type: str = "fixed"

    # Markdown generation options
    ignore_links: bool = True
    ignore_images: bool = True
    skip_internal_links: bool = True
    include_sup_sub: bool = True

    # Crawler settings
    exclude_external_links: bool = False
    exclude_social_media_links: bool = True
    exclude_external_images: bool = True
    process_iframes: bool = False
    remove_overlay_elements: bool = True
    # user_agent_mode: str = "random"
    excluded_tags: List[str] = ["form", "header", "footer", "nav"]
    cache_mode: CacheMode = CacheMode.BYPASS

    # Rate limiting settings
    # base_delay: tuple = (0.25, 0.5)
    # max_delay: float = 5

    # Dispatcher settings
    # max_session_permit: int = 50

    @property
    def get_markdown_options(self) -> dict:
        return {
            "ignore_links": self.ignore_links,
            "ignore_images": self.ignore_images,
            "skip_internal_links": self.skip_internal_links,
            "include_sup_sub": self.include_sup_sub,
        }

    def get_browser_config(self) -> BrowserConfig:
        return BrowserConfig(headless=self.browser_headless)

    def get_run_config(self) -> CrawlerRunConfig:
        prune_filter = PruningContentFilter(
            threshold=self.pruning_threshold,
            threshold_type=self.pruning_threshold_type,
        )
        markdown_generator = DefaultMarkdownGenerator(
            content_filter=prune_filter, options=self.get_markdown_options
        )
        return CrawlerRunConfig(
            markdown_generator=markdown_generator,
            exclude_external_links=self.exclude_external_links,
            exclude_social_media_links=self.exclude_social_media_links,
            exclude_external_images=self.exclude_external_images,
            process_iframes=self.process_iframes,
            remove_overlay_elements=self.remove_overlay_elements,
            excluded_tags=self.excluded_tags,
            # user_agent_mode=self.user_agent_mode,
            scraping_strategy=LXMLWebScrapingStrategy(),
            cache_mode=self.cache_mode,
        )

    # def get_rate_limiter(self) -> RateLimiter:
    #     return RateLimiter(base_delay=self.base_delay, max_delay=self.max_delay)

    # def get_dispatcher(self) -> MemoryAdaptiveDispatcher:
    #     return MemoryAdaptiveDispatcher(
    #         max_session_permit=self.max_session_permit,
    #         rate_limiter=self.get_rate_limiter(),
    #     )


@lru_cache()
def get_settings() -> ScraperSettings:
    """Get cached settings instance"""
    return ScraperSettings()


settings = get_settings()

browser_config = settings.get_browser_config()
run_config = settings.get_run_config()
# dispatcher = settings.get_dispatcher()

if __name__ == "__main__":
    print(browser_config)
    print(run_config)

# options = {
#     "ignore_links": True,
#     "ignore_images": True,
#     "skip_internal_links": True,
#     "include_sup_sub": True,
# }
# browser_config = BrowserConfig()
# prune_filter = PruningContentFilter(
#     threshold=0.2,
#     threshold_type="dynamic",
# )
# markdown_generator = DefaultMarkdownGenerator(
#     content_filter=prune_filter, options=options
# )
# run_config = CrawlerRunConfig(
#     markdown_generator=markdown_generator,
#     exclude_external_links=True,
#     exclude_social_media_links=True,
#     exclude_external_images=True,
#     process_iframes=True,
#     remove_overlay_elements=True,
#     excluded_tags=["form", "header", "footer", "nav"],
#     scraping_strategy=LXMLWebScrapingStrategy(),
#     cache_mode=CacheMode.BYPASS,
# )
