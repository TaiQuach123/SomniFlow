from pydantic import BaseModel, Field
from typing import List, Literal, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime


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


class Interaction(BaseModel):
    id: UUID
    thread_id: str
    user_query: str
    tasks: Optional[list[Any]] = None
    sources: Optional[list[Any]] = None
    assistant_response: str
    created_at: datetime

    class Config:
        from_attributes = True


class CreateInteractionRequest(BaseModel):
    thread_id: str
    user_query: str
    tasks: list = []
    sources: list = []
    assistant_response: str
