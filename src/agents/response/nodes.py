import json
import logging
from src.graph.states import MainGraphState
from src.common.logging import get_logger
from src.agents.response.prompts import response_agent_prompt
from langgraph.config import get_stream_writer
import os
import binascii

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import (
    ModelMessage,
    ModelMessagesTypeAdapter,
    ModelResponse,
    TextPart,
    ModelRequest,
    SystemPromptPart,
    UserPromptPart,
)

from src.common.llm import create_llm_agent


logger = get_logger("my_app")
logging.getLogger("httpx").setLevel(logging.WARNING)


def get_response_agent() -> Agent:
    response_agent = create_llm_agent(
        provider="gemini",
        model_name="gemini-2.0-flash",
        result_type=str,
        deps_type=str,
        instructions=response_agent_prompt,
    )

    @response_agent.instructions
    def add_context(ctx: RunContext[str]):
        return f"Retrieved Contexts:\n{ctx.deps}\n"

    return response_agent


async def response_node(state: MainGraphState):
    writer = get_stream_writer()
    logger.info("Response Node")

    contexts = "\n\n".join(
        [
            state.get("suggestion_context", ""),
            state.get("harm_context", ""),
            state.get("factor_context", ""),
        ]
    )

    contexts = contexts.strip()

    message_history: list[ModelMessage] = []
    for message_row in state["messages"]:
        message_history.extend(ModelMessagesTypeAdapter.validate_json(message_row))

    response_agent = get_response_agent()

    async with response_agent.run_stream(
        state["user_input"],
        message_history=message_history,
        deps=contexts,
        model_settings={"temperature": 0.0},
    ) as result:
        async for chunk in result.stream_text(delta=True, debounce_by=None):
            writer(
                json.dumps(
                    {
                        "type": "message",
                        "data": chunk,
                        "messageId": state["messageId"],
                    }
                )
                + "\n"
            )

        writer(json.dumps({"type": "messageEnd"}) + "\n")

    response = await result.get_output()

    return {
        "messages": [
            ModelMessagesTypeAdapter.dump_json(
                [
                    ModelRequest(parts=[UserPromptPart(content=state["user_input"])]),
                    ModelResponse(parts=[TextPart(content=response)]),
                ]
            )
        ]
    }
