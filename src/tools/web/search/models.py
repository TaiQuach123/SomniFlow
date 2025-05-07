from pydantic import BaseModel
from typing import Optional, TypedDict, List


class SearXNGSearchResult(BaseModel):
    url: str
    title: str
    content: str | None = None
    publishedDate: str | None = None
    score: float | None = None  # Score from SearXNG engine
    weight: float = 1.0
    # img_src: str | None = None
    # thumbnail: str | None = None
    # iframe_src: str | None = None

    class Config:
        extra = "ignore"


class BoostedSearXNGSearchResult(SearXNGSearchResult):
    freq_boost: float = 0.0
    hostname_boost: float = 0.0
    path_boost: float = 0.0
    jina_rerank_boost: float = 0.0
    final_score: float = 0.0


class SearXNGSearchResponse(BaseModel):
    results: List[SearXNGSearchResult]


class SearXNGSearchParams(TypedDict):
    language: Optional[str]
    pageno: Optional[int]
    time_range: Optional[str]
    safe_search: Optional[int]
