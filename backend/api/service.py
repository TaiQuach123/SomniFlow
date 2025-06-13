from sqlalchemy.ext.asyncio import AsyncSession
from backend.api.models import SessionMetadata as SessionMetadataORM
from sqlalchemy import select, and_
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import insert
import json
from typing import List
from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter, ModelRequest
from backend.api.schemas import Message, Interaction as InteractionSchema
import uuid
from backend.api.models import Interaction


class APIService:
    async def get_chat_sessions(self, user_id, session: AsyncSession):
        result = await session.execute(
            select(SessionMetadataORM).where(SessionMetadataORM.user_id == user_id)
        )
        return result.scalars().all()

    async def create_or_update_session(
        self, user_id, thread_id, title, session: AsyncSession
    ):
        now = datetime.now(timezone.utc)
        stmt = (
            insert(SessionMetadataORM)
            .values(
                thread_id=thread_id,
                user_id=user_id,
                title=title,
                last_updated=now,
            )
            .on_conflict_do_update(
                index_elements=["thread_id"], set_={"last_updated": now}
            )
        )
        await session.execute(stmt)
        await session.commit()
        # Optionally, fetch and return the session object
        result = await session.execute(
            select(SessionMetadataORM).where(SessionMetadataORM.thread_id == thread_id)
        )
        return result.scalar_one_or_none()

    async def get_chat_history_from_checkpointer(self, thread_id, checkpointer):
        print("Getting chat history from checkpointer")
        messages: List[Message] = []
        config = {"configurable": {"thread_id": thread_id}}
        latest_checkpoint = await checkpointer.aget(config)

        message_history: List[ModelMessage] = []
        for message_row in latest_checkpoint["channel_values"]["messages"]:
            message_history.extend(ModelMessagesTypeAdapter.validate_json(message_row))

        for i, message in enumerate(message_history):
            if isinstance(message, ModelRequest):
                role = "user"
                created_at = str(message.parts[0].timestamp)
            else:
                role = "assistant"
                created_at = str(message.timestamp)

            content = message.parts[0].content

            messages.append(
                Message(
                    id=uuid.uuid4(),
                    thread_id=thread_id,
                    content=content,
                    role=role,
                    metadata=json.dumps({"created_at": created_at}),
                )
            )

        created_at = (
            str(message_history[0].parts[0].timestamp) if message_history else None
        )
        return messages, created_at

    async def create_interaction(
        self,
        session: AsyncSession,
        thread_id: str,
        user_query: str,
        tasks: list,
        sources: list,
        assistant_response: str,
    ) -> Interaction:
        # Check for existing interaction with same thread_id, user_query, and assistant_response
        result = await session.execute(
            select(Interaction).where(
                and_(
                    Interaction.thread_id == thread_id,
                    Interaction.user_query == user_query,
                    Interaction.assistant_response == assistant_response,
                )
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing
        new_interaction = Interaction(
            thread_id=thread_id,
            user_query=user_query,
            tasks=tasks,
            sources=sources,
            assistant_response=assistant_response,
        )
        session.add(new_interaction)
        await session.commit()
        await session.refresh(new_interaction)
        return new_interaction

    async def get_interactions(
        self, session: AsyncSession, thread_id: str
    ) -> list[InteractionSchema]:
        result = await session.execute(
            select(Interaction)
            .where(Interaction.thread_id == thread_id)
            .order_by(Interaction.created_at)
        )
        interactions = result.scalars().all()
        return [InteractionSchema.model_validate(i) for i in interactions]

    async def delete_thread(self, session: AsyncSession, thread_id: str) -> bool:
        # Try to find the session
        result = await session.execute(
            select(SessionMetadataORM).where(SessionMetadataORM.thread_id == thread_id)
        )
        session_metadata = result.scalar_one_or_none()
        if not session_metadata:
            return False
        await session.delete(session_metadata)
        await session.commit()
        return True
