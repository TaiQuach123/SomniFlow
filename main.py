from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.graph.builder import create_main_graph
from typing import AsyncIterable
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver


config = {"configurable": {"thread_id": "10"}}


app_state = {"checkpointer": None, "graph": None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = AsyncConnectionPool(
        conninfo="postgresql://postgres:0913979472aA@localhost:5432/postgres?sslmode=disable",
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
    async for data in app_state["graph"].astream(
        {"user_input": query}, config, stream_mode="custom"
    ):
        print(data.replace("TOKEN: ", ""), end="")
        yield data.replace("TOKEN: ", "")


@app.post("/stream_chat")
async def stream_response(user_input: UserInput):
    generator = generate_response(user_input.user_input)
    return StreamingResponse(generator, media_type="text/event-stream")
