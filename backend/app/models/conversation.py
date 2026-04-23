from __future__ import annotations

from sqlalchemy import ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Conversation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "conversations"

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), index=True)
    runtime_state: Mapped[str] = mapped_column(default="novo")
    current_step: Mapped[str | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(default="ativa")
    last_message_direction: Mapped[str | None] = mapped_column(nullable=True)

    lead = relationship("Lead", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "messages"

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), index=True)

    direction: Mapped[str] = mapped_column(default="inbound")
    message_type: Mapped[str] = mapped_column(default="text")
    provider_message_id: Mapped[str | None] = mapped_column(nullable=True)
    content_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    sent_by_ai: Mapped[bool] = mapped_column(default=False)

    conversation = relationship("Conversation", back_populates="messages")
