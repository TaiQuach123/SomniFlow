from typing import Annotated, List, TypedDict


class HarmState(TypedDict):
    harm_context: str
    messages: Annotated[List[bytes], lambda x, y: x + y]
    queries: List[str]


class HarmOutputState(TypedDict):
    harm_context: str
