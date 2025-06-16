from typing import List
from typing_extensions import TypedDict


class SuggestionState(TypedDict):
    rag_sources: dict
    web_sources: dict
    loops: int
    suggestion_task: str
    feedback: str
    queries: List[str]
    suggestion_context: dict
    messageId: str


class SuggestionOutputState(TypedDict):
    suggestion_context: dict
