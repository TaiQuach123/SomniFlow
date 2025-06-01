from fastapi import APIRouter, Depends
from backend.auth.dependencies import get_current_user
from backend.auth.models import User
from backend.api.schemas import ChatInput


router = APIRouter(prefix="/api", tags=["api"])


@router.get("/chats")
async def get_chat_history(user: User = Depends(get_current_user)):
    print(user.thread_ids)
    return {"message": "Hello, World!"}


@router.get("/chats/{thread_id}")
async def get_chat_session(thread_id: str):
    return {"message": "Hello, World!"}


@router.post("/chat")
async def stream_response(input: ChatInput):
    pass
