from typing import Literal
from pydantic_ai import Agent, RunContext
from src.common.llm import create_llm_agent
from src.doc_pipeline.llms.chunk_relevance_filter.models import Deps, NoiseFilterOutput
from src.doc_pipeline.llms.chunk_relevance_filter.prompts import CHUNK_FILTER_PROMPT
from src.doc_pipeline.llms.base import BaseAgent


def create_chunk_relevance_filter_agent(
    provider: Literal["ollama", "groq", "gemini"] = "ollama",
    model_name: str = "qwen3",
) -> Agent:
    agent = create_llm_agent(
        provider=provider,
        model_name=model_name,
        system_prompt=CHUNK_FILTER_PROMPT,
        result_type=NoiseFilterOutput,
        deps_type=Deps,
    )

    @agent.system_prompt
    def add_context(ctx: RunContext[Deps]):
        context = f"=== Chunk of Text ===\n{ctx.deps.chunk_text}"
        return context

    return agent


class ChunkRelevanceFilterAgent(BaseAgent):
    def __init__(
        self,
        provider: Literal["ollama", "groq", "gemini"] = "ollama",
        model_name: str = "qwen3",
    ):
        self.agent = create_chunk_relevance_filter_agent(
            provider=provider, model_name=model_name
        )

    def run_sync(self, user_prompt: str = "/no_think", chunk: str = ""):
        return self.agent.run_sync(
            user_prompt=user_prompt,
            deps=Deps(chunk_text=chunk),
            model_settings={"temperature": 0.0},
        )

    async def run(self, user_prompt: str = "/no_think", chunk: str = ""):
        return await self.agent.run(
            user_prompt=user_prompt,
            deps=Deps(chunk_text=chunk),
            model_settings={"temperature": 0.0},
        )
