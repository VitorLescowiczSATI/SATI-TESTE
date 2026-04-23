from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ScheduledJob(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "scheduled_jobs"

    tenant_id: Mapped[str | None] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True)
    lead_id: Mapped[str | None] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), nullable=True, index=True)
    conversation_id: Mapped[str | None] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), nullable=True, index=True)

    kind: Mapped[str] = mapped_column(index=True)
    status: Mapped[str] = mapped_column(default="pending")
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    attempts: Mapped[int] = mapped_column(default=0)
    dedupe_key: Mapped[str | None] = mapped_column(String(120), nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    lead = relationship("Lead", back_populates="scheduled_jobs")
    conversation = relationship("Conversation", back_populates="scheduled_jobs")
