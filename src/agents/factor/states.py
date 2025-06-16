from typing import List
from typing_extensions import TypedDict


class FactorState(TypedDict):
    rag_sources: dict
    web_sources: dict
    loops: int
    factor_task: str
    feedback: str
    queries: List[str]
    factor_context: dict
    messageId: str


class FactorOutputState(TypedDict):
    factor_context: dict
