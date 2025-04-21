from pydantic import BaseModel
from typing import Optional, TypedDict, List


class SearXNGSearchResult(BaseModel):
    title: str
    url: str
    content: str
    img_src: Optional[str]
    thumbnail: Optional[str]
    iframe_src: Optional[str]


class SearXNGSearchResponse(BaseModel):
    results: List[SearXNGSearchResult]


class SearXNGSearchParams(TypedDict):
    categories: Optional[str]
    engines: Optional[str]
    language: Optional[str]
    pageno: Optional[int]
    time_range: Optional[str]
    safe_search: Optional[int]
