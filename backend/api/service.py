from sqlalchemy.ext.asyncio import AsyncSession
from backend.api.models import SessionMetadata as SessionMetadataORM
from sqlalchemy import select
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import insert
import json
from typing import List
from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter, ModelRequest
from backend.api.schemas import Message
import uuid


class APIService:
    async def get_chat_sessions(self, user_id, session: AsyncSession):
        result = await session.execute(
            select(SessionMetadataORM).where(SessionMetadataORM.user_id == user_id)
        )
        return result.scalars().all()

    async def create_or_update_session(
        self, user_id, thread_id, title, session: AsyncSession
    ):
        # --- Old logic (for reference) ---
        # result = await session.execute(
        #     select(SessionMetadataORM).where(SessionMetadataORM.thread_id == thread_id)
        # )
        # session_obj = result.scalar_one_or_none()
        # if not session_obj:
        #     new_session = SessionMetadataORM(
        #         thread_id=thread_id,
        #         user_id=user_id,
        #         title=title,
        #         last_updated=datetime.now(timezone.utc),
        #     )
        #     session.add(new_session)
        #     await session.commit()
        #     return new_session
        # else:
        #     session_obj.last_updated = datetime.now(timezone.utc)
        #     await session.commit()
        #     return session_obj

        # --- New upsert logic ---
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
