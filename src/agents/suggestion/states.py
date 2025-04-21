from typing import List, TypedDict


class SuggestionState(TypedDict):
    task: str
    queries: List[str]
    suggestion_context: str


class SuggestionOutputState(TypedDict):
    suggestion_context: str
