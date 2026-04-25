from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AgentConfig(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "agent_configs"
    __table_args__ = (UniqueConstraint("tenant_id", "key", name="uq_agent_configs_tenant_key"),)

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    key: Mapped[str] = mapped_column(String(100), index=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    model: Mapped[str] = mapped_column(String(80), default="gpt-4.1-mini")
    system_prompt: Mapped[str] = mapped_column(Text)
    max_tokens: Mapped[int] = mapped_column(Integer, default=700)
    temperature: Mapped[float] = mapped_column(Float, default=0.3)
    status: Mapped[str] = mapped_column(String(40), default="active")

    tenant = relationship("Tenant", back_populates="agent_configs")
    runtime_versions = relationship("RuntimeConfigVersion", back_populates="agent_config")


class RuntimeConfigVersion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "runtime_config_versions"
    __table_args__ = (UniqueConstraint("tenant_id", "key", name="uq_runtime_config_versions_tenant_key"),)

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    agent_config_id: Mapped[str] = mapped_column(ForeignKey("agent_configs.id", ondelete="RESTRICT"), index=True)
    key: Mapped[str] = mapped_column(String(120), index=True)
    name: Mapped[str] = mapped_column(String(160))
    version: Mapped[str] = mapped_column(String(40), default="v1")
    status: Mapped[str] = mapped_column(String(40), default="draft")
    channel_mode: Mapped[str] = mapped_column(String(40), default="playground")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    tenant = relationship("Tenant", back_populates="runtime_config_versions")
    agent_config = relationship("AgentConfig", back_populates="runtime_versions")
    conversations = relationship("Conversation", back_populates="runtime_config_version")


class PromptSection(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "prompt_sections"
    __table_args__ = (UniqueConstraint("tenant_id", "agent_config_id", "key", name="uq_prompt_sections_agent_key"),)

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    agent_config_id: Mapped[str] = mapped_column(ForeignKey("agent_configs.id", ondelete="CASCADE"), index=True)
    key: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(160))
    content: Mapped[str] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(default=True)


class ToolDefinition(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "tool_definitions"
    __table_args__ = (UniqueConstraint("tenant_id", "key", name="uq_tool_definitions_tenant_key"),)

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    key: Mapped[str] = mapped_column(String(100), index=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    schema: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_enabled: Mapped[bool] = mapped_column(default=True)
    is_core: Mapped[bool] = mapped_column(default=True)


class KnowledgeProject(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "knowledge_projects"
    __table_args__ = (UniqueConstraint("tenant_id", "slug", name="uq_knowledge_projects_tenant_slug"),)

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    slug: Mapped[str] = mapped_column(String(160), index=True)
    name: Mapped[str] = mapped_column(String(180))
    region: Mapped[str] = mapped_column(String(120))
    city_neighborhood: Mapped[str | None] = mapped_column(String(160), nullable=True)
    status: Mapped[str | None] = mapped_column(String(80), nullable=True)
    min_income: Mapped[float | None] = mapped_column(Float, nullable=True)
    typology: Mapped[str | None] = mapped_column(String(160), nullable=True)
    highlights: Mapped[list | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)


class ToolCallLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "tool_call_logs"

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), index=True)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
    tool_key: Mapped[str] = mapped_column(String(120), index=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="planned")
