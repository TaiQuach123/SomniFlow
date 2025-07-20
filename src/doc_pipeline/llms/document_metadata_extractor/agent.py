from typing import Literal
from pydantic_ai import Agent, RunContext
from src.common.llm import create_llm_agent
from src.doc_pipeline.llms.document_metadata_extractor.models import (
    DocumentMetadata,
    ExtractorDeps,
)
from src.doc_pipeline.llms.document_metadata_extractor.prompts import (
    METADATA_EXTRACTOR_PROMPT,
)
from src.doc_pipeline.llms.base import BaseAgent


def create_metadata_extractor_agent(
    provider: Literal["ollama", "groq", "gemini"] = "gemini",
    model_name: str = "gemini-2.5-flash-lite-preview-06-17",
) -> Agent:
    agent = create_llm_agent(
        provider=provider,
        model_name=model_name,
        system_prompt=METADATA_EXTRACTOR_PROMPT,
        result_type=DocumentMetadata,
        deps_type=ExtractorDeps,
    )

    @agent.system_prompt
    def add_context(ctx: RunContext[ExtractorDeps]):
        return f"=== Content ===\n{ctx.deps.first_page_text}"

    return agent


class MetadataExtractor(BaseAgent):
    def __init__(
        self,
        provider: Literal["ollama", "groq", "gemini"] = "gemini",
        model_name: str = "gemini-2.5-flash-lite-preview-06-17",
    ):
        self.agent = create_metadata_extractor_agent(
            provider=provider, model_name=model_name
        )

    def run_sync(self, user_prompt: str = "", first_page_text: str = ""):
        return self.agent.run_sync(
            user_prompt=user_prompt,
            deps=ExtractorDeps(first_page_text=first_page_text),
            model_settings={"temperature": 0.0},
        )

    async def run(self, user_prompt: str = "", first_page_text: str = ""):
        return await self.agent.run(
            user_prompt=user_prompt,
            deps=ExtractorDeps(first_page_text=first_page_text),
            model_settings={"temperature": 0.0},
        )
