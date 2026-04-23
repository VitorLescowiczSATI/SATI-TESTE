from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CrmDispatch(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "crm_dispatches"

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), index=True)
    provider: Mapped[str] = mapped_column(String(80), default="pipedrive")
    status: Mapped[str] = mapped_column(String(40), default="pending")
    attempts: Mapped[int] = mapped_column(default=0)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    response_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    external_reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    dispatched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    lead = relationship("Lead", back_populates="crm_dispatches")
