from typing import Annotated, List, TypedDict


class FactorState(TypedDict):
    factor_context: str
    messages: Annotated[List[bytes], lambda x, y: x + y]
    queries: List[str]


class FactorOutputState(TypedDict):
    factor_context: str
