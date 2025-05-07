import os
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from src.graph.builder import create_main_graph
from typing import AsyncIterable
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from dotenv import load_dotenv

load_dotenv()


config = {"configurable": {"thread_id": "20"}}


app_state = {"graph": None}


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

    yield

    await pool.close()


class UserInput(BaseModel):
    user_input: str


app = FastAPI(lifespan=lifespan)

# Create templates directory if it doesn't exist
os.makedirs("templates", exist_ok=True)

# Set up templates
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def get_chat_interface(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    return {"status": "ok"}


async def generate_response(query: str) -> AsyncIterable[str]:
    async for data in app_state["graph"].astream(
        {"user_input": query}, config, stream_mode="custom"
    ):
        # Pass through all data types (TOKEN, RAG_QUERIES, WEB_QUERIES)
        print(data)
        yield data + "\n"


@app.post("/stream_chat")
async def stream_response(user_input: UserInput):
    generator = generate_response(user_input.user_input)
    return StreamingResponse(generator, media_type="text/event-stream")
