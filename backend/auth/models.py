import uuid
from sqlalchemy import Column, String, ForeignKey, Text, UniqueConstraint, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    # name = Column(String)
    # avatar_url = Column(String)
    thread_ids = Column(ARRAY(String), nullable=False, default=[])
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    auth_providers = relationship(
        "AuthProvider", back_populates="user", cascade="all, delete-orphan"
    )


class AuthProvider(Base):
    __tablename__ = "auth_providers"
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_provider_user"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    provider = Column(String, nullable=False)  # e.g., 'email', 'google', 'github'
    provider_user_id = Column(String)  # For OAuth, stores the external user ID
    hashed_password = Column(Text, nullable=True)  # Only used for 'email' provider
    name = Column(String, nullable=True)
    avatar_url = Column(
        String,
        default="https://ssl.gstatic.com/accounts/ui/avatar_2x.png",
        nullable=True,
    )
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    user = relationship("User", back_populates="auth_providers")
