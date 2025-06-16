import json
import logging
from src.graph.states import MainGraphState
from src.common.logging import get_logger
from src.agents.response.prompts import response_agent_prompt
from langgraph.config import get_stream_writer
from src.tools.utils.formatters import (
    merge_rag_sources,
    merge_web_sources,
    format_merged_rag_sources,
    format_merged_web_sources,
)

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import (
    ModelMessage,
    ModelMessagesTypeAdapter,
    ModelResponse,
    TextPart,
    ModelRequest,
    UserPromptPart,
)

from src.common.llm import create_llm_agent


logger = get_logger("my_app")
logging.getLogger("httpx").setLevel(logging.WARNING)


def get_response_agent() -> Agent:
    response_agent = create_llm_agent(
        provider="gemini",
        model_name="gemini-2.0-flash-lite",
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
    # logger.info("Response Node")
    print("=== Response Node ===")

    writer(json.dumps({"type": "step", "data": "Finished"}) + "\n")

    writer(
        json.dumps(
            {
                "type": "taskEnd",
                "messageId": state["messageId"],
            }
        )
        + "\n"
    )

    merged_rag_sources = merge_rag_sources(
        state.get("suggestion_context", {}).get("rag_sources", {}),
        state.get("harm_context", {}).get("rag_sources", {}),
        state.get("factor_context", {}).get("rag_sources", {}),
    )
    merged_web_sources = merge_web_sources(
        state.get("suggestion_context", {}).get("web_sources", {}),
        state.get("harm_context", {}).get("web_sources", {}),
        state.get("factor_context", {}).get("web_sources", {}),
    )

    writer(
        json.dumps(
            {
                "type": "sources",
                "data": {
                    "rag_sources": merged_rag_sources,
                    "web_sources": merged_web_sources,
                },
            }
        )
        + "\n"
    )

    contexts = "\n\n===\n\n".join(
        s
        for s in [
            format_merged_rag_sources(merged_rag_sources),
            format_merged_web_sources(merged_web_sources, len(merged_rag_sources)),
        ]
        if s
    )

    print("Contexts: ", contexts)

    # logger.info(f"Contexts: {contexts}")

    message_history: list[ModelMessage] = []
    for message_row in state["messages"]:
        message_history.extend(ModelMessagesTypeAdapter.validate_json(message_row))

    response_agent = get_response_agent()
    writer(json.dumps({"type": "messageStart"}) + "\n")

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
        ],
        "suggestion_task": "",
        "harm_task": "",
        "factor_task": "",
        "suggestion_context": {},
        "harm_context": {},
        "factor_context": {},
    }
