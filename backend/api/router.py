from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_async_session
from backend.auth.dependencies import get_current_user_id
from backend.api.service import APIService
from backend.api.dependencies import get_checkpointer, get_graph
from backend.api.schemas import (
    ChatRequest,
    Source,
    Message,
    SessionMetadata,
    ConversationHistory,
)
from backend.api.utils import generate_response


api_service = APIService()
router = APIRouter(prefix="/api", tags=["api"])


@router.get("/chats", response_model=List[SessionMetadata])
async def get_chat_sessions(
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session),
):
    sessions = await api_service.get_chat_sessions(user_id, session)
    return [
        SessionMetadata(
            thread_id=s.thread_id,
            title=s.title,
            created_at=s.created_at.isoformat() if s.created_at else None,
            last_updated=s.last_updated.isoformat() if s.last_updated else None,
        )
        for s in sessions
    ]


@router.get("/chats/{thread_id}", response_model=ConversationHistory)
async def get_chat_history(
    thread_id: UUID, checkpointer: AsyncPostgresSaver = Depends(get_checkpointer)
):
    messages, created_at = await api_service.get_chat_history_from_checkpointer(
        str(thread_id), checkpointer
    )
    return ConversationHistory(
        messages=messages,
        # Optionally add session_metadata if needed
        # session_metadata=SessionMetadata(
        #     thread_id=thread_id,
        #     title=title,  # If you extract title from messages or elsewhere
        #     created_at=created_at,
        #     last_updated=created_at,
        # ),
    )


@router.post("/chat")
async def stream_response(
    input: ChatRequest,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session),
    graph=Depends(get_graph),
):
    try:
        session_obj = await api_service.create_or_update_session(
            user_id, str(input.thread_id), input.user_input, session
        )

        generator = generate_response(input.user_input, str(input.thread_id), graph)

        async def stream_generator():
            async for data in generator:
                yield data

        return StreamingResponse(
            stream_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-transform",
                "Connection": "keep-alive",
            },
        )
    except HTTPException as e:
        # Re-raise HTTPExceptions so FastAPI can handle them
        raise e
    except Exception as e:
        # Catch-all for unexpected errors
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
