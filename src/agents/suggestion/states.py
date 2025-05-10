from typing import List
from typing_extensions import TypedDict


class SuggestionState(TypedDict):
    rag_source_map: dict
    web_source_map: dict
    loops: int
    suggestion_task: str
    feedback: str
    queries: List[str]
    raw_contexts: str
    suggestion_context: str
    messageId: str


class SuggestionOutputState(TypedDict):
    suggestion_context: str
