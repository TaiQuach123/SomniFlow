import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from backend.database import init_db
from backend.redis import close_redis
from backend.auth.config import oauth_config
from backend.auth.router import router as auth_router
from backend.api.router import router as api_router
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from src.graph.builder import create_main_graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
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

    app.state.graph = graph
    app.state.checkpointer = checkpointer
    app.state.pool = pool

    yield

    await close_redis()
    await pool.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=oauth_config.SESSION_SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# Mount static files for database folder
app.mount("/database", StaticFiles(directory="database"), name="database")

app.include_router(auth_router)
app.include_router(api_router)
