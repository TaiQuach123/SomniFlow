from pydantic import BaseModel, Field
from typing import List


class ReflectionDeps(BaseModel):
    task: str = Field(description="A specific task related to insomnia")
    extracted_contexts: str = Field(
        description="A formatted string of all extracted contexts with reference number, title, source, and content"
    )


class ReflectionOutput(BaseModel):
    should_proceed: bool = Field(
        description="True if the extracted contexts are good enough to answer the task without needing further refinement."
    )
    feedback_to_task_handler: str | None = Field(
        description="Only provided when should_proceed is False. Contains helpful feedback for improving context retrieval.",
        default=None,
    )


class ExtractedContext(BaseModel):
    reference_number: int = Field(description="The reference number of the context")
    title: str = Field(description="The title of the context")
    url_or_source: str = Field(description="The URL or source of the context")
    content: str = Field(description="The extracted content from the context")


class ExtractorOutput(BaseModel):
    extracted_contexts: List[ExtractedContext] = Field(
        description="The list of extracted contexts"
    )


class ExtractorDeps(BaseModel):
    task: str = Field(description="A specific task related to insomnia")
    contexts: str = Field(
        description="The contexts retrieved from RAG and/or web search"
    )


class TaskHandlerOutput(BaseModel):
    queries: List[str] = Field(description="The list of queries to be executed")


class TaskHandlerDeps(BaseModel):
    feedback: str = Field(
        description="The feedback from the Reflection Agent", default=""
    )
    task: str = Field(description="A specific task related to insomnia")


class EvaluatorOutput(BaseModel):
    feedback: str = Field(
        description="Insightful reasoning about context sufficiency and sub-query quality"
    )
    should_proceed: bool = Field(
        description="True if the information is sufficient to answer the original task"
    )
    new_queries: List[str] = Field(
        description="Improved sub-queries (up to 2). Empty if original ones is still valid",
        default=[],
    )


class EvaluatorDeps(BaseModel):
    task: str
    queries: list[str]
    contexts: list[str]
