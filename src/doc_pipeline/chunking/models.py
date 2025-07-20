from pydantic import BaseModel, Field


class ChunkMetadata(BaseModel):
    title: str = Field(
        description="The title of the document that the chunk belongs to"
    )
    summary: str = Field(
        description="The summary of the document that the chunk belongs to"
    )
    source: str = Field(
        description="The source of the document that the chunk belongs to"
    )
    chunk_no: int = Field(description="The number of the chunk in the document")
    num_chunks: int = Field(description="The total number of chunks in the document")
    headings: str = Field(
        description="The headings of the document that the chunk belongs to"
    )


class Chunk(BaseModel):
    content: str = Field(description="The content of the chunk")
    metadata: ChunkMetadata = Field(description="The metadata of the chunk")
