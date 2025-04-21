from src.graph.states import MainGraphState
from src.common.logging import get_logger

from pydantic_ai.messages import (
    ModelMessage,
    ModelMessagesTypeAdapter,
    ModelResponse,
    TextPart,
    ModelRequest,
    # SystemPromptPart,
    UserPromptPart,
)


logger = get_logger("my_app")


async def response_node(state: MainGraphState):
    logger.info("Response Node")

    combined_context = "\n".join(
        [
            state.get("suggestion_context", ""),
            state.get("harm_context", ""),
            state.get("factor_context", ""),
        ]
    )

    # response = await response_agent.run(
    #     state["user_input"],
    #     context=combined_context,
    #     model_settings={"temperature": 0.0},
    # )

    response = "The response from model"

    return {
        "messages": [
            ModelMessagesTypeAdapter.dump_json(
                [ModelResponse(parts=[TextPart(content=response)])]
            )
        ]
    }
