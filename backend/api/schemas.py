from pydantic import BaseModel, Field
from typing import List, Literal
from uuid import UUID, uuid4


class ChatRequest(BaseModel):
    user_input: str
    thread_id: UUID | None = Field(default_factory=uuid4)


class Source(BaseModel):
    metadata: dict
    page_content: str


class Message(BaseModel):
    id: UUID
    thread_id: UUID
    content: str
    role: Literal["user", "assistant"]
    metadata: str | None = None


class SessionMetadata(BaseModel):
    thread_id: UUID
    title: str | None = None
    created_at: str | None = None
    last_updated: str | None = None


class ConversationHistory(BaseModel):
    # session_metadata: SessionMetadata
    messages: List[Message]
