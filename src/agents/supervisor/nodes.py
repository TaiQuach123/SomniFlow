from typing import Literal, Union

from pydantic_ai import RunContext
from pydantic_ai.messages import (
    ModelMessage,
    ModelMessagesTypeAdapter,
    ModelResponse,
    TextPart,
    ModelRequest,
    # SystemPromptPart,
    UserPromptPart,
)
from src.common.llm import create_llm_agent, process_instruction
from src.graph.states import MainGraphState
from src.agents.supervisor.models import ClarificationRequest, AgentDelegation
from src.agents.supervisor.prompts import supervisor_prompt, reasoning_prompt

from langgraph.config import get_stream_writer
from langgraph.types import Command, interrupt

from src.common.logging import get_logger

logger = get_logger("my_app")

reasoning_agent = create_llm_agent(
    provider="groq",
    model_name="deepseek-r1-distill-llama-70b",
    system_prompt=reasoning_prompt,
)

supervisor_agent = create_llm_agent(
    provider="groq",
    model_name="qwen-qwq-32b",
    system_prompt=supervisor_prompt,
    result_type=Union[ClarificationRequest, AgentDelegation],
    deps_type=str,
    retries=3,
)


@supervisor_agent.system_prompt
def add_instruction(ctx: RunContext[str]):
    return ctx.deps


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
    logger.info("Supervisor")
    writer("\n--- Supervisor ---\n")
    message_history: list[ModelMessage] = []

    for message_row in state["messages"]:
        message_history.extend(ModelMessagesTypeAdapter.validate_json(message_row))

    reasoning_output = await reasoning_agent.run(
        state["user_input"],
        message_history=message_history,
        model_settings={"temperature": 0.0},
    )
    instruction = process_instruction(reasoning_output.output)

    output = await supervisor_agent.run(
        instruction, deps=instruction, model_settings={"temperature": 0.0}
    )

    if isinstance(output.output, ClarificationRequest):
        writer(output.output.follow_up_question)

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
                update={
                    "messages": [
                        ModelMessagesTypeAdapter.dump_json(
                            [
                                ModelRequest(
                                    parts=[UserPromptPart(content=state["user_input"])]
                                )
                            ]
                        ),
                    ]
                },
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
                    "messages": [
                        ModelMessagesTypeAdapter.dump_json(
                            [
                                ModelRequest(
                                    parts=[UserPromptPart(content=state["user_input"])]
                                )
                            ]
                        ),
                    ]
                },
            )


def ask_human(state: MainGraphState):
    print("--- ask_human node ---")
    value = interrupt({})
    print(value)

    return {"user_input": value}
