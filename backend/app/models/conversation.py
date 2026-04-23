from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Conversation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "conversations"

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), index=True)
    runtime_state: Mapped[str] = mapped_column(default="novo")
    current_step: Mapped[str | None] = mapped_column(nullable=True)
    strategy_key: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(default="ativa")
    last_message_direction: Mapped[str | None] = mapped_column(nullable=True)
    handoff_mode: Mapped[str | None] = mapped_column(String(40), nullable=True)
    idle_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    summary_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    classified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    lead = relationship("Lead", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    scheduled_jobs = relationship("ScheduledJob", back_populates="conversation", cascade="all, delete-orphan")


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
    tool_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    tool_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    tool_result_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    delivery_status: Mapped[str | None] = mapped_column(String(40), nullable=True)

    conversation = relationship("Conversation", back_populates="messages")
