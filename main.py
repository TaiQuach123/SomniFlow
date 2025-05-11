import json
import os
import binascii
from typing import List
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.graph.builder import create_main_graph
from typing import AsyncIterable
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from pydantic_ai.messages import (
    ModelMessage,
    ModelMessagesTypeAdapter,
    ModelRequest,
)

from dotenv import load_dotenv

load_dotenv()


app_state = {"graph": None, "checkpointer": None, "pool": None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = AsyncConnectionPool(
        conninfo=os.getenv("POSTGRES_DB_URL"),
        max_size=20,
        kwargs={"autocommit": True, "prepare_threshold": 0},
        open=False,
    )
    await pool.open()
    checkpointer = AsyncPostgresSaver(pool)
    await checkpointer.setup()

    workflow = create_main_graph()
    graph = workflow.compile(checkpointer=checkpointer)

    app_state["graph"] = graph
    app_state["checkpointer"] = checkpointer
    app_state["pool"] = pool

    yield

    await pool.close()


class ChatRequest(BaseModel):
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


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


async def generate_response(query: str, thread_id: str) -> AsyncIterable[str]:
    async for data in app_state["graph"].astream(
        {"user_input": query, "messageId": binascii.hexlify(os.urandom(7)).decode()},
        {"configurable": {"thread_id": thread_id}},
        stream_mode="custom",
    ):
        yield data
        print(data)


@app.post("/api/chat")
async def stream_response(request: ChatRequest):
    print(request)
    generator = generate_response(request.user_input, request.thread_id)

    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.get("/api/chats/{thread_id}", response_model=ChatHistory)
async def get_chat(thread_id: str):
    messages: List[Message] = []

    config = {"configurable": {"thread_id": thread_id}}
    latest_checkpoint = await app_state["checkpointer"].aget(config)

    message_history: list[ModelMessage] = []
    for message_row in latest_checkpoint["channel_values"]["messages"]:
        message_history.extend(ModelMessagesTypeAdapter.validate_json(message_row))

    for i, message in enumerate(message_history):
        if isinstance(message, ModelRequest):
            role = "user"
            createdAt = str(message.parts[0].timestamp)
        else:
            role = "assistant"
            createdAt = str(message.timestamp)

        content = message.parts[0].content

        messages.append(
            Message(
                # id=i,
                threadId=thread_id,
                content=content,
                role=role,
                metadata=json.dumps({"createdAt": createdAt}),
            )
        )

    title = message_history[0].parts[0].content
    createdAt = str(message_history[0].parts[0].timestamp)

    return ChatHistory(
        chat=Chat(threadId=thread_id, title=title, createdAt=createdAt),
        messages=messages,
    )


@app.get("/api/chats", response_model=List[Chat])
async def get_chats():
    async with app_state["pool"].connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(""" SELECT DISTINCT thread_id FROM checkpoints """)
            rows = await cur.fetchall()
            thread_ids = [row[0] for row in rows]

    chats: List[Chat] = []

    for thread_id in thread_ids:
        chat = await get_chat(thread_id)
        chats.append(chat.chat)

    return chats
