from typing import List, TypedDict


class FactorState(TypedDict):
    factor_context: str
    factor_task: str
    queries: List[str]


class FactorOutputState(TypedDict):
    factor_context: str
