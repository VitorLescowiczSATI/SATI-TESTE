from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message
from app.models.lead import Lead, LeadProfile
from app.models.tenant import Tenant
from app.runtime.runtime_service import process_inbound
from app.runtime.strategies.mcmv_tenda_rj import MCMVTendaRJStrategy
from app.services.runtime_config_service import get_published_runtime_config


def create_playground_conversation(db: Session, tenant_id: str, lead_name: str | None) -> Conversation:
    runtime_config = get_published_runtime_config(db, tenant_id)
    lead = Lead(
        tenant_id=tenant_id,
        name=lead_name or "Lead de Teste",
        phone=f"playground-{uuid4().hex[:12]}",
        source_channel="playground",
        status="novo",
        assigned_strategy_key=MCMVTendaRJStrategy.config.key,
        assigned_agent_config_id=runtime_config.agent_config_id,
    )
    db.add(lead)
    db.flush()
    db.add(LeadProfile(tenant_id=tenant_id, lead_id=lead.id))

    conversation = Conversation(
        tenant_id=tenant_id,
        lead_id=lead.id,
        config_version_id=runtime_config.id,
        runtime_state="novo",
        current_step="playground_inicio",
        strategy_key=MCMVTendaRJStrategy.config.key,
        status="ativa",
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def handle_playground_message(db: Session, tenant: Tenant, conversation_id: str, message: str) -> Conversation:
    return _handle_inbound(
        db,
        tenant=tenant,
        conversation_id=conversation_id,
        content_text=message,
        message_type="text",
        raw_payload={"source": "playground"},
    )


def handle_playground_audio(
    db: Session,
    tenant: Tenant,
    conversation_id: str,
    *,
    transcript: str,
    audio_filename: str | None,
    audio_size_bytes: int,
    mime_type: str | None,
) -> Conversation:
    return _handle_inbound(
        db,
        tenant=tenant,
        conversation_id=conversation_id,
        content_text=transcript,
        message_type="audio",
        raw_payload={
            "source": "playground",
            "input_kind": "audio",
            "audio_transcript": transcript,
            "audio_filename": audio_filename,
            "audio_size_bytes": audio_size_bytes,
            "mime_type": mime_type,
        },
    )


def _handle_inbound(
    db: Session,
    *,
    tenant: Tenant,
    conversation_id: str,
    content_text: str,
    message_type: str,
    raw_payload: dict,
) -> Conversation:
    conversation = db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == tenant.id,
        )
    )
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversa de playground nao encontrada.")

    now = datetime.now(timezone.utc)
    lead = conversation.lead
    lead.last_inbound_at = now
    lead.status = "em_atendimento"
    conversation.runtime_state = "em_atendimento"
    conversation.current_step = "playground_conversa"
    conversation.last_message_direction = "inbound"
    conversation.idle_started_at = now

    inbound = Message(
        tenant_id=tenant.id,
        conversation_id=conversation.id,
        lead_id=lead.id,
        direction="inbound",
        message_type=message_type,
        content_text=content_text,
        raw_payload=raw_payload,
        sent_by_ai=False,
        delivery_status="received",
    )
    db.add(inbound)
    db.add(lead)
    db.add(conversation)
    db.flush()

    process_inbound(
        db,
        conversation=conversation,
        inbound_message=inbound,
        source_label="playground",
    )
    db.commit()
    db.refresh(conversation)
    return conversation
