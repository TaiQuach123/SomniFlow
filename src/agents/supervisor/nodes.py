from typing import Literal, Union
import logging
import json

from pydantic_ai import Agent
from pydantic_ai.messages import (
    ModelMessage,
    ModelMessagesTypeAdapter,
    ModelResponse,
    TextPart,
    ModelRequest,
    UserPromptPart,
)
from src.common.llm import create_llm_agent
from src.graph.states import MainGraphState
from src.agents.supervisor.models import ClarificationRequest, AgentDelegation
from src.agents.supervisor.prompts import supervisor_prompt

from langgraph.config import get_stream_writer
from langgraph.types import Command, interrupt

from src.common.logging import get_logger

logger = get_logger("my_app")
logging.getLogger("httpx").setLevel(logging.WARNING)


def create_supervisor_agent() -> Agent:
    supervisor_agent = create_llm_agent(
        provider="gemini",
        model_name="gemini-2.0-flash",
        result_type=Union[ClarificationRequest, AgentDelegation],
        instructions=supervisor_prompt,
        deps_type=str,
        retries=3,
    )
    return supervisor_agent


async def supervisor_node(
    state: MainGraphState,
) -> Command[
    Literal[
        "suggestion_agent",
        "harm_agent",
        "factor_agent",
        "ask_human_node",
        "response_agent",
    ]
]:
    writer = get_stream_writer()

    writer(json.dumps({"type": "taskStart", "messageId": state["messageId"]}) + "\n")

    message_history: list[ModelMessage] = []
    supervisor_agent = create_supervisor_agent()
    for message_row in state["messages"]:
        message_history.extend(ModelMessagesTypeAdapter.validate_json(message_row))

    # logger.info(print(message_history))
    writer(
        json.dumps(
            {
                "type": "step",
                "data": "Planning...",
                "messageId": state["messageId"],
            }
        )
        + "\n"
    )

    output = await supervisor_agent.run(
        state["user_input"],
        message_history=message_history,
        model_settings={"temperature": 0.0},
    )

    if isinstance(output.output, ClarificationRequest):
        logger.info("Clarification Request")
        writer(
            json.dumps(
                {
                    "type": "taskEnd",
                    "messageId": state["messageId"],
                }
            )
            + "\n"
        )

        writer(json.dumps({"type": "messageStart"}) + "\n")
        writer(
            json.dumps(
                {
                    "type": "message",
                    "data": output.output.follow_up_question,
                    "messageId": state["messageId"],
                }
            )
            + "\n"
        )
        writer(json.dumps({"type": "messageEnd"}) + "\n")

        return Command(
            goto="ask_human_node",
            update={
                "messages": [
                    ModelMessagesTypeAdapter.dump_json(
                        [
                            ModelRequest(
                                parts=[UserPromptPart(content=state["user_input"])]
                            ),
                            ModelResponse(
                                parts=[
                                    TextPart(content=output.output.follow_up_question)
                                ]
                            ),
                        ]
                    ),
                ]
            },
        )

    else:
        if output.output.should_response:
            return Command(
                goto="response_agent",
                update={},
            )
        else:
            goto = []
            if output.output.suggestion_agent:
                goto.append("suggestion_agent")
            if output.output.harm_agent:
                goto.append("harm_agent")
            if output.output.factor_agent:
                goto.append("factor_agent")
            return Command(
                goto=goto,
                update={
                    "suggestion_task": output.output.suggestion_agent,
                    "harm_task": output.output.harm_agent,
                    "factor_task": output.output.factor_agent,
                },
            )


def ask_human(state: MainGraphState):
    value = interrupt({})
    return {"user_input": value}
