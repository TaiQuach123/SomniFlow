from pydantic import BaseModel
from typing import List


class ChatInput(BaseModel):
    user_input: str
    thread_id: str


class Source(BaseModel):
    metadata: dict
    pageContent: str


class Chat(BaseModel):
    threadId: str
    title: str | None = None
    createdAt: str | None = None


class Message(BaseModel):
    # id: int
    threadId: str
    content: str
    role: str
    metadata: str | None = None


class ChatHistory(BaseModel):
    chat: Chat
    messages: List[Message]
