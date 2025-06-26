from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    title: str = Field(description="The main title of the article")
    summary: str = Field(description="A brief summary of what the article is about")
