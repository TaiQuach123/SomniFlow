from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.database import init_db
from backend.redis import close_redis
from backend.auth.config import oauth_config
from backend.auth.router import router as auth_router
from backend.api.router import router as api_router
from starlette.middleware.sessions import SessionMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_redis()


app = FastAPI(lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=oauth_config.SESSION_SECRET_KEY)


app.include_router(auth_router)
app.include_router(api_router)
