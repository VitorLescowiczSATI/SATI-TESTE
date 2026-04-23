from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class MediaAsset(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "media_assets"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "project_slug",
            "media_type",
            "url",
            name="uq_media_assets_tenant_project_type_url",
        ),
    )

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    project_slug: Mapped[str] = mapped_column(String(160), index=True)
    media_type: Mapped[str] = mapped_column(String(60), index=True)
    label: Mapped[str | None] = mapped_column(String(160), nullable=True)
    url: Mapped[str] = mapped_column(String(1000))
    sort_order: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    tenant = relationship("Tenant", back_populates="media_assets")
