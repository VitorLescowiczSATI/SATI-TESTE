from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException
from openai import OpenAI
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.conversation import Conversation, Message
from app.models.lead import Lead, LeadProfile
from app.models.tenant import Tenant
from app.runtime.strategies.mcmv_tenda_rj import MCMVTendaRJStrategy
from app.services.lead_analysis_service import refresh_conversation_analysis
from app.services.runtime_config_service import build_runtime_prompt, get_published_runtime_config

settings = get_settings()


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

    db.add(
        Message(
            tenant_id=tenant.id,
            conversation_id=conversation.id,
            lead_id=lead.id,
            direction="inbound",
            message_type="text",
            content_text=message,
            raw_payload={"source": "playground"},
            sent_by_ai=False,
            delivery_status="received",
        )
    )
    db.add(lead)
    db.add(conversation)
    db.commit()

    assistant_text = generate_maju_response(db, conversation)
    conversation.last_message_direction = "outbound"
    lead.last_outbound_at = datetime.now(timezone.utc)

    db.add(
        Message(
            tenant_id=tenant.id,
            conversation_id=conversation.id,
            lead_id=lead.id,
            direction="outbound",
            message_type="text",
            content_text=assistant_text,
            raw_payload={"source": "openai", "mode": "playground"},
            sent_by_ai=True,
            delivery_status="sent",
        )
    )
    refresh_conversation_analysis(db, conversation)
    db.add(lead)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def generate_maju_response(db: Session, conversation: Conversation) -> str:
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY nao configurada no backend.",
        )

    messages = db.scalars(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
    ).all()
    input_messages = [
        {
            "role": "user" if message.direction == "inbound" else "assistant",
            "content": message.content_text or "",
        }
        for message in messages
        if message.content_text
    ]

    runtime_config = (
        conversation.runtime_config_version
        if conversation.runtime_config_version is not None
        else get_published_runtime_config(db, conversation.tenant_id)
    )
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(
        model=runtime_config.agent_config.model or settings.openai_model,
        instructions=build_runtime_prompt(db, runtime_config),
        input=input_messages,
        max_output_tokens=runtime_config.agent_config.max_tokens,
    )

    output_text = getattr(response, "output_text", None)
    if output_text:
        return output_text.strip()

    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                return text.strip()

    return "Consegui te acompanhar por aqui. Pode me mandar mais uma mensagem pra eu continuar?"
