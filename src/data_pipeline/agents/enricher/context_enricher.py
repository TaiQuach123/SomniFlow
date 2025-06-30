from pydantic_ai import Agent, RunContext
from src.common.llm import create_llm_agent
from src.data_pipeline.agents.enricher.base import BaseEnricher
from src.data_pipeline.agents.enricher.models import Context, ContextLeadInOutput
from src.data_pipeline.agents.enricher.prompts import CONTEXT_EXTRACTOR_PROMPT


def _create_context_enrichment_agent() -> Agent:
    agent = create_llm_agent(
        provider="gemini",
        model_name="gemini-2.5-flash-lite-preview-06-17",
        system_prompt=CONTEXT_EXTRACTOR_PROMPT,
        result_type=ContextLeadInOutput,
        deps_type=Context,
    )

    @agent.system_prompt
    def add_context(ctx: RunContext[Context]):
        metadata = f"""=== Title (if available) ===\n{ctx.deps.title}\n\n=== Summary (if available) ===\n{ctx.deps.summary}\n\n"""
        context = f"""=== Preceding Context (if available) ===\n{ctx.deps.preceding_context}\n\n=== Chunk ===\n{ctx.deps.target_chunk}\n\n=== Following Context (if available) ===\n{ctx.deps.following_context}"""
        return f"{metadata}{context}"

    return agent


class ContextEnricher(BaseEnricher):
    def __init__(self):
        self.agent = _create_context_enrichment_agent()

    async def enrich(self, context: Context) -> ContextLeadInOutput:
        output = await self.agent.run("", deps=context)
        return output.output
