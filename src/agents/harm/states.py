from typing import List
from typing_extensions import TypedDict


class HarmState(TypedDict):
    rag_sources: dict
    web_sources: dict
    loops: int
    harm_task: str
    feedback: str
    queries: List[str]
    harm_context: dict
    messageId: str


class HarmOutputState(TypedDict):
    harm_context: dict
