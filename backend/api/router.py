from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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
    Interaction,
    CreateInteractionRequest,
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


@router.get("/interactions/{thread_id}", response_model=List[Interaction])
async def get_interactions(
    thread_id: str, session: AsyncSession = Depends(get_async_session)
):
    return await api_service.get_interactions(session, thread_id)


# @router.get("/chats/{thread_id}", response_model=ConversationHistory)
# async def get_chat_history(
#     thread_id: UUID, checkpointer: AsyncPostgresSaver = Depends(get_checkpointer)
# ):
#     messages, created_at = await api_service.get_chat_history_from_checkpointer(
#         str(thread_id), checkpointer
#     )
#     return ConversationHistory(
#         messages=messages,
#     )


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


@router.post("/interactions")
async def create_interaction_endpoint(
    data: CreateInteractionRequest, session: AsyncSession = Depends(get_async_session)
):
    interaction = await api_service.create_interaction(
        session=session,
        thread_id=data.thread_id,
        user_query=data.user_query,
        tasks=data.tasks,
        sources=data.sources,
        assistant_response=data.assistant_response,
    )
    return {"status": "success", "interaction_id": str(interaction.id)}


@router.delete("/chats/{thread_id}")
async def delete_chat(
    thread_id: str,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session),
):
    # Check if the thread exists and belongs to the user
    # Use the service method for deletion
    deleted = await api_service.delete_thread(session, thread_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Thread not found")
    return {"status": "success", "message": f"Thread {thread_id} deleted"}
