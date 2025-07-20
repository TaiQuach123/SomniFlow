from pydantic import BaseModel, Field


class ExtractorDeps(BaseModel):
    first_page_text: str = Field(
        description="The first page of the article", default=""
    )


class DocumentMetadata(BaseModel):
    title: str = Field(description="The main title of the article", default="")
    summary: str = Field(
        description="A brief summary of what the article is about", default=""
    )
