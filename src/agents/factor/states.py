from typing import List
from typing_extensions import TypedDict


class FactorState(TypedDict):
    rag_sources: dict
    web_sources: dict
    loops: int
    factor_task: str
    feedback: str
    queries: List[str]
    raw_contexts: str
    factor_context: str
    messageId: str


class FactorOutputState(TypedDict):
    factor_context: str
