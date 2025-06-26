from pydantic_ai import Agent, RunContext
from src.common.llm import create_llm_agent
from src.data_pipeline.extractors.base import BaseExtractor
from src.data_pipeline.converters.json_to_markdown import JsonToMarkdownConverter
from src.data_pipeline.extractors.models import DocumentMetadata
from src.data_pipeline.extractors.prompts import METADATA_EXTRACTOR_PROMPT


def _create_metadata_extractor_agent() -> Agent:
    agent = create_llm_agent(
        provider="gemini",
        model_name="gemini-2.5-flash-lite-preview-06-17",
        system_prompt=METADATA_EXTRACTOR_PROMPT,
        result_type=DocumentMetadata,
        deps_type=str,
    )

    @agent.system_prompt
    def add_context(ctx: RunContext[str]):
        return f"=== Content ===\n{ctx.deps}"

    return agent


class LlmMetadataExtractor(BaseExtractor):
    def __init__(self):
        self.agent = _create_metadata_extractor_agent()

    async def extract(self, json_path: str) -> DocumentMetadata:
        page_content = JsonToMarkdownConverter.extract_first_page_content(json_path)
        output = await self.agent.run("", deps=page_content)
        return output.output
