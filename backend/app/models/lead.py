from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Lead(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "leads"
    __table_args__ = (UniqueConstraint("tenant_id", "phone", name="uq_leads_tenant_phone"),)

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    phone: Mapped[str] = mapped_column(String(40), index=True)
    source_channel: Mapped[str] = mapped_column(String(40), default="whatsapp")
    source_campaign: Mapped[str | None] = mapped_column(String(120), nullable=True)
    first_message_signature: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="novo")
    classification: Mapped[str | None] = mapped_column(String(40), nullable=True)
    classification_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_inbound_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_outbound_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    assigned_strategy_key: Mapped[str | None] = mapped_column(String(80), nullable=True)
    assigned_agent_config_id: Mapped[str | None] = mapped_column(
        ForeignKey("agent_configs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    tenant = relationship("Tenant", back_populates="leads")
    profile = relationship("LeadProfile", back_populates="lead", uselist=False, cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="lead", cascade="all, delete-orphan")
    scheduled_jobs = relationship("ScheduledJob", back_populates="lead", cascade="all, delete-orphan")
    crm_dispatches = relationship("CrmDispatch", back_populates="lead", cascade="all, delete-orphan")


class LeadProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lead_profiles"

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), unique=True, index=True)

    proof_of_income_type: Mapped[str | None] = mapped_column(String(60), nullable=True)
    uses_fgts: Mapped[bool | None] = mapped_column(nullable=True)
    family_income: Mapped[float | None] = mapped_column(Float, nullable=True)
    entry_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    has_property: Mapped[bool | None] = mapped_column(nullable=True)
    employment_history_months: Mapped[int | None] = mapped_column(nullable=True)
    marital_status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    birth_date: Mapped[date | None] = mapped_column(nullable=True)
    dependents_summary: Mapped[str | None] = mapped_column(String(255), nullable=True)
    interest_project: Mapped[str | None] = mapped_column(String(160), nullable=True)
    interest_region: Mapped[str | None] = mapped_column(String(160), nullable=True)
    schedule_date_raw: Mapped[str | None] = mapped_column(String(40), nullable=True)
    schedule_time_raw: Mapped[str | None] = mapped_column(String(20), nullable=True)
    schedule_attempts: Mapped[int] = mapped_column(default=0)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    lead = relationship("Lead", back_populates="profile")
