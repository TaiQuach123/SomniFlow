import asyncio
from pydantic_ai import RunContext

from src.common.llm import create_llm_agent
from src.agents.base import TaskHandlerOutput
from src.agents.suggestion.prompts import suggestion_agent_prompt
from src.agents.suggestion.states import SuggestionState

from src.common.logging import get_logger

logger = get_logger("my_app")

suggestion_agent = create_llm_agent(
    provider="groq",
    model_name="qwen-qwq-32b",
    system_prompt=suggestion_agent_prompt,
    result_type=TaskHandlerOutput,
    deps_type=str,
)


@suggestion_agent.system_prompt
def add_instruction(ctx: RunContext[str]):
    return ctx.deps


async def task_handler_node(state: SuggestionState):
    logger.info("Suggestion Task Handler Node")
    res = await suggestion_agent.run(
        "", deps=f"Task: {state['task']}", model_settings={"temperature": 0.0}
    )
    logger.info(f"Queries: {res.output.queries}")
    return {"queries": res.output.queries}


async def retriever(state: SuggestionState):
    logger.info("Suggestion Retriever Node")
    await asyncio.sleep(2)
    return {"suggestion_context": "This is the context from the retriever agent."}
