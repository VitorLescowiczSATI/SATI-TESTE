from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "202604230002"
down_revision = "202604230001"
branch_labels = None
depends_on = None


def create_timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.add_column("leads", sa.Column("first_message_signature", sa.String(length=255), nullable=True))
    op.add_column("leads", sa.Column("classification", sa.String(length=40), nullable=True))
    op.add_column("leads", sa.Column("classification_reason", sa.Text(), nullable=True))
    op.add_column("leads", sa.Column("last_inbound_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("leads", sa.Column("last_outbound_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("leads", sa.Column("assigned_strategy_key", sa.String(length=80), nullable=True))

    op.add_column("lead_profiles", sa.Column("schedule_date_raw", sa.String(length=40), nullable=True))
    op.add_column("lead_profiles", sa.Column("schedule_time_raw", sa.String(length=20), nullable=True))
    op.add_column("lead_profiles", sa.Column("schedule_attempts", sa.Integer(), nullable=False, server_default="0"))

    op.add_column("conversations", sa.Column("strategy_key", sa.String(length=80), nullable=True))
    op.add_column("conversations", sa.Column("handoff_mode", sa.String(length=40), nullable=True))
    op.add_column("conversations", sa.Column("idle_started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("conversations", sa.Column("summary_text", sa.Text(), nullable=True))
    op.add_column("conversations", sa.Column("summary_generated_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("conversations", sa.Column("classified_at", sa.DateTime(timezone=True), nullable=True))

    op.add_column("messages", sa.Column("tool_name", sa.String(length=120), nullable=True))
    op.add_column("messages", sa.Column("tool_payload", sa.JSON(), nullable=True))
    op.add_column("messages", sa.Column("tool_result_text", sa.Text(), nullable=True))
    op.add_column("messages", sa.Column("media_url", sa.String(length=1000), nullable=True))
    op.add_column("messages", sa.Column("delivery_status", sa.String(length=40), nullable=True))

    op.add_column("scheduled_jobs", sa.Column("dedupe_key", sa.String(length=120), nullable=True))
    op.add_column("scheduled_jobs", sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("scheduled_jobs", sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True))

    op.add_column("crm_dispatches", sa.Column("response_payload", sa.JSON(), nullable=True))
    op.add_column("crm_dispatches", sa.Column("dispatched_at", sa.DateTime(timezone=True), nullable=True))
    op.alter_column(
        "crm_dispatches",
        "provider",
        existing_type=sa.String(length=80),
        server_default="pipedrive",
        existing_nullable=False,
    )

    op.create_table(
        "source_signature_maps",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        *create_timestamps(),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("signature", sa.String(length=255), nullable=False),
        sa.Column("source_channel", sa.String(length=80), nullable=False),
        sa.Column("source_campaign", sa.String(length=160), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", "signature", name="uq_source_signature_maps_tenant_signature"),
    )
    op.create_index("ix_source_signature_maps_signature", "source_signature_maps", ["signature"])
    op.create_index("ix_source_signature_maps_tenant_id", "source_signature_maps", ["tenant_id"])

    op.create_table(
        "media_assets",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        *create_timestamps(),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("project_slug", sa.String(length=160), nullable=False),
        sa.Column("media_type", sa.String(length=60), nullable=False),
        sa.Column("label", sa.String(length=160), nullable=True),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "tenant_id",
            "project_slug",
            "media_type",
            "url",
            name="uq_media_assets_tenant_project_type_url",
        ),
    )
    op.create_index("ix_media_assets_project_slug", "media_assets", ["project_slug"])
    op.create_index("ix_media_assets_media_type", "media_assets", ["media_type"])
    op.create_index("ix_media_assets_tenant_id", "media_assets", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_media_assets_tenant_id", table_name="media_assets")
    op.drop_index("ix_media_assets_media_type", table_name="media_assets")
    op.drop_index("ix_media_assets_project_slug", table_name="media_assets")
    op.drop_table("media_assets")

    op.drop_index("ix_source_signature_maps_tenant_id", table_name="source_signature_maps")
    op.drop_index("ix_source_signature_maps_signature", table_name="source_signature_maps")
    op.drop_table("source_signature_maps")

    op.alter_column(
        "crm_dispatches",
        "provider",
        existing_type=sa.String(length=80),
        server_default="facilita",
        existing_nullable=False,
    )
    op.drop_column("crm_dispatches", "dispatched_at")
    op.drop_column("crm_dispatches", "response_payload")

    op.drop_column("scheduled_jobs", "completed_at")
    op.drop_column("scheduled_jobs", "locked_at")
    op.drop_column("scheduled_jobs", "dedupe_key")

    op.drop_column("messages", "delivery_status")
    op.drop_column("messages", "media_url")
    op.drop_column("messages", "tool_result_text")
    op.drop_column("messages", "tool_payload")
    op.drop_column("messages", "tool_name")

    op.drop_column("conversations", "classified_at")
    op.drop_column("conversations", "summary_generated_at")
    op.drop_column("conversations", "summary_text")
    op.drop_column("conversations", "idle_started_at")
    op.drop_column("conversations", "handoff_mode")
    op.drop_column("conversations", "strategy_key")

    op.drop_column("lead_profiles", "schedule_attempts")
    op.drop_column("lead_profiles", "schedule_time_raw")
    op.drop_column("lead_profiles", "schedule_date_raw")

    op.drop_column("leads", "assigned_strategy_key")
    op.drop_column("leads", "last_outbound_at")
    op.drop_column("leads", "last_inbound_at")
    op.drop_column("leads", "classification_reason")
    op.drop_column("leads", "classification")
    op.drop_column("leads", "first_message_signature")
