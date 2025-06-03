import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
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
