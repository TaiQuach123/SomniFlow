from pydantic import BaseModel, Field


class ContextLeadInOutput(BaseModel):
    """Structured output for the Context Enrichment Agent."""

    context_lead_in: str = Field(
        description="A brief sentence or two that, when prepended to the target chunk, adds necessary context to improve its clarity and standalone interpretability for downstream tasks like embedding or retrieval.",
    )


class Context(BaseModel):
    title: str = Field(description="The title of the article", default="")
    summary: str = Field(
        description="A brief summary of what the article is about", default=""
    )
    target_chunk: str = Field(
        description="The main chunk from the article to be contextualized.", default=""
    )
    preceding_context: str = Field(
        description="The text that comes before the target chunk, which may consist of one or more chunks.",
        default="",
    )
    following_context: str = Field(
        description="The text that comes after the target chunk, which may consist of one or more chunks.",
        default="",
    )
