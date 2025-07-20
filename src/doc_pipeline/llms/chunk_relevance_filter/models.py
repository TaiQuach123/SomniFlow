from typing import Optional
from pydantic import BaseModel, Field


class Deps(BaseModel):
    chunk_text: str = Field(description="The chunk of text to evaluate")


class NoiseFilterOutput(BaseModel):
    is_irrelevant: bool = Field(
        description=(
            "Set to True if the chunk contains only irrelevant or disruptive information that should be removed from the reconstructed document "
            "(e.g., author details, footnotes, copyright, URLs, citation-only lists). "
            "Set to False if the chunk includes any meaningful scientific content, even if partial, fragmented, or in the form of a figure or table."
        )
    )
    reason_if_irrelevant: Optional[str] = Field(
        default=None,
        description="If is_irrelevant is True, briefly explain why (e.g., 'author list', 'footnote', 'URL'). Leave blank if is_irrelevant is False.",
    )
