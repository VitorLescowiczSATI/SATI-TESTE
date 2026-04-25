from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "202604250001"
down_revision = "202604230002"
branch_labels = None
depends_on = None


def create_timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "agent_configs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        *create_timestamps(),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("model", sa.String(length=80), nullable=False),
        sa.Column("system_prompt", sa.Text(), nullable=False),
        sa.Column("max_tokens", sa.Integer(), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", "key", name="uq_agent_configs_tenant_key"),
    )
    op.create_index("ix_agent_configs_key", "agent_configs", ["key"])
    op.create_index("ix_agent_configs_tenant_id", "agent_configs", ["tenant_id"])

    op.create_table(
        "runtime_config_versions",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        *create_timestamps(),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("agent_config_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("key", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("version", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("channel_mode", sa.String(length=40), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["agent_config_id"], ["agent_configs.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", "key", name="uq_runtime_config_versions_tenant_key"),
    )
    op.create_index("ix_runtime_config_versions_agent_config_id", "runtime_config_versions", ["agent_config_id"])
    op.create_index("ix_runtime_config_versions_key", "runtime_config_versions", ["key"])
    op.create_index("ix_runtime_config_versions_tenant_id", "runtime_config_versions", ["tenant_id"])

    op.create_table(
        "prompt_sections",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        *create_timestamps(),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("agent_config_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["agent_config_id"], ["agent_configs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", "agent_config_id", "key", name="uq_prompt_sections_agent_key"),
    )
    op.create_index("ix_prompt_sections_agent_config_id", "prompt_sections", ["agent_config_id"])
    op.create_index("ix_prompt_sections_tenant_id", "prompt_sections", ["tenant_id"])

    op.create_table(
        "tool_definitions",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        *create_timestamps(),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("schema", sa.JSON(), nullable=True),
        sa.Column("is_enabled", sa.Boolean(), nullable=False),
        sa.Column("is_core", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", "key", name="uq_tool_definitions_tenant_key"),
    )
    op.create_index("ix_tool_definitions_key", "tool_definitions", ["key"])
    op.create_index("ix_tool_definitions_tenant_id", "tool_definitions", ["tenant_id"])

    op.create_table(
        "knowledge_projects",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        *create_timestamps(),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("slug", sa.String(length=160), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("region", sa.String(length=120), nullable=False),
        sa.Column("city_neighborhood", sa.String(length=160), nullable=True),
        sa.Column("status", sa.String(length=80), nullable=True),
        sa.Column("min_income", sa.Float(), nullable=True),
        sa.Column("typology", sa.String(length=160), nullable=True),
        sa.Column("highlights", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", "slug", name="uq_knowledge_projects_tenant_slug"),
    )
    op.create_index("ix_knowledge_projects_slug", "knowledge_projects", ["slug"])
    op.create_index("ix_knowledge_projects_tenant_id", "knowledge_projects", ["tenant_id"])

    op.create_table(
        "tool_call_logs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        *create_timestamps(),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tool_key", sa.String(length=120), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_tool_call_logs_conversation_id", "tool_call_logs", ["conversation_id"])
    op.create_index("ix_tool_call_logs_lead_id", "tool_call_logs", ["lead_id"])
    op.create_index("ix_tool_call_logs_tenant_id", "tool_call_logs", ["tenant_id"])
    op.create_index("ix_tool_call_logs_tool_key", "tool_call_logs", ["tool_key"])

    op.add_column(
        "leads",
        sa.Column("assigned_agent_config_id", postgresql.UUID(as_uuid=False), nullable=True),
    )
    op.create_foreign_key(
        "fk_leads_assigned_agent_config_id_agent_configs",
        "leads",
        "agent_configs",
        ["assigned_agent_config_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_leads_assigned_agent_config_id", "leads", ["assigned_agent_config_id"])

    op.add_column(
        "conversations",
        sa.Column("config_version_id", postgresql.UUID(as_uuid=False), nullable=True),
    )
    op.create_foreign_key(
        "fk_conversations_config_version_id_runtime_config_versions",
        "conversations",
        "runtime_config_versions",
        ["config_version_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_conversations_config_version_id", "conversations", ["config_version_id"])


def downgrade() -> None:
    op.drop_index("ix_conversations_config_version_id", table_name="conversations")
    op.drop_constraint("fk_conversations_config_version_id_runtime_config_versions", "conversations", type_="foreignkey")
    op.drop_column("conversations", "config_version_id")

    op.drop_index("ix_leads_assigned_agent_config_id", table_name="leads")
    op.drop_constraint("fk_leads_assigned_agent_config_id_agent_configs", "leads", type_="foreignkey")
    op.drop_column("leads", "assigned_agent_config_id")

    op.drop_index("ix_tool_call_logs_tool_key", table_name="tool_call_logs")
    op.drop_index("ix_tool_call_logs_tenant_id", table_name="tool_call_logs")
    op.drop_index("ix_tool_call_logs_lead_id", table_name="tool_call_logs")
    op.drop_index("ix_tool_call_logs_conversation_id", table_name="tool_call_logs")
    op.drop_table("tool_call_logs")

    op.drop_index("ix_knowledge_projects_tenant_id", table_name="knowledge_projects")
    op.drop_index("ix_knowledge_projects_slug", table_name="knowledge_projects")
    op.drop_table("knowledge_projects")

    op.drop_index("ix_tool_definitions_tenant_id", table_name="tool_definitions")
    op.drop_index("ix_tool_definitions_key", table_name="tool_definitions")
    op.drop_table("tool_definitions")

    op.drop_index("ix_prompt_sections_tenant_id", table_name="prompt_sections")
    op.drop_index("ix_prompt_sections_agent_config_id", table_name="prompt_sections")
    op.drop_table("prompt_sections")

    op.drop_index("ix_runtime_config_versions_tenant_id", table_name="runtime_config_versions")
    op.drop_index("ix_runtime_config_versions_key", table_name="runtime_config_versions")
    op.drop_index("ix_runtime_config_versions_agent_config_id", table_name="runtime_config_versions")
    op.drop_table("runtime_config_versions")

    op.drop_index("ix_agent_configs_tenant_id", table_name="agent_configs")
    op.drop_index("ix_agent_configs_key", table_name="agent_configs")
    op.drop_table("agent_configs")
