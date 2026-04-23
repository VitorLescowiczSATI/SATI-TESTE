from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SourceSignatureMap(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "source_signature_maps"
    __table_args__ = (UniqueConstraint("tenant_id", "signature", name="uq_source_signature_maps_tenant_signature"),)

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    signature: Mapped[str] = mapped_column(String(255), index=True)
    source_channel: Mapped[str] = mapped_column(String(80), default="whatsapp")
    source_campaign: Mapped[str | None] = mapped_column(String(160), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    tenant = relationship("Tenant", back_populates="source_signature_maps")
