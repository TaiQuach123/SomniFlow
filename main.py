from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from src.graph.builder import create_main_graph
from typing import AsyncIterable
import os

config = {"configurable": {"thread_id": "1"}}


class UserInput(BaseModel):
    user_input: str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


async def generate_response(query: str) -> AsyncIterable[str]:
    workflow = create_main_graph()
    graph = workflow.compile()
    async for data in graph.astream(
        {"user_input": query}, config, stream_mode="custom"
    ):
        yield data


@app.post("/stream_chat")
async def stream_response(user_input: UserInput):
    try:
        generator = generate_response(user_input.user_input)
        return StreamingResponse(generator, media_type="text/event-stream")
