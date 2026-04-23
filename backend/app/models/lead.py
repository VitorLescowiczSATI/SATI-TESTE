from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint
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
    status: Mapped[str] = mapped_column(String(40), default="novo")

    tenant = relationship("Tenant", back_populates="leads")
    profile = relationship("LeadProfile", back_populates="lead", uselist=False, cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="lead", cascade="all, delete-orphan")
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
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    lead = relationship("Lead", back_populates="profile")
