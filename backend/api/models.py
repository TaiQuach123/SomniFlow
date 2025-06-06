import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP, Text
from backend.database import Base


class SessionMetadata(Base):
    __tablename__ = "session_metadata"

    thread_id = Column(String, primary_key=True, unique=True, nullable=False)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    last_updated = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    thread_id = Column(
        String,
        ForeignKey("session_metadata.thread_id", ondelete="CASCADE"),
        nullable=False,
    )
    user_query = Column(Text, nullable=False)
    tasks = Column(JSONB, nullable=True)
    sources = Column(JSONB, nullable=True)
    assistant_response = Column(Text, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
