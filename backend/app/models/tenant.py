from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Tenant(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "tenants"

    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    operation_type: Mapped[str] = mapped_column(String(80), default="mcmv")
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    crm_provider: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="draft")

    memberships = relationship("Membership", back_populates="tenant", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="tenant")
    leads = relationship("Lead", back_populates="tenant")
