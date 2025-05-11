from typing import List
from typing_extensions import TypedDict


class HarmState(TypedDict):
    rag_source_map: dict
    web_source_map: dict
    loops: int
    harm_task: str
    feedback: str
    queries: List[str]
    raw_contexts: str
    harm_context: str
    messageId: str


class HarmOutputState(TypedDict):
    harm_context: str
