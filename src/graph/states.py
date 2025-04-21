from typing import Annotated, List, TypedDict


class MainGraphState(TypedDict):
    user_input: str
    messages: Annotated[List[bytes], lambda x, y: x + y]
    suggestion_context: str
    harm_context: str
    factor_context: str
