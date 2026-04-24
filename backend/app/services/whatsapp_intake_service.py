from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message
from app.models.lead import Lead, LeadProfile
from app.models.tenant import Tenant


@dataclass(frozen=True)
class IntakeResult:
    processed: int
    ignored: int


def process_whatsapp_webhook(db: Session, tenant: Tenant, payload: dict[str, Any]) -> IntakeResult:
    processed = 0
    ignored = 0

    for item in iter_inbound_messages(payload):
        if item.provider_message_id:
            existing_message = db.scalar(
                select(Message).where(
                    Message.tenant_id == tenant.id,
                    Message.provider_message_id == item.provider_message_id,
                )
            )
            if existing_message is not None:
                ignored += 1
                continue

        lead = get_or_create_lead(db, tenant, item)
        conversation = get_or_create_active_conversation(db, tenant, lead)
        now = datetime.now(timezone.utc)

        lead.last_inbound_at = now
        lead.status = "em_atendimento"
        lead.assigned_strategy_key = lead.assigned_strategy_key or "mcmv_tenda_rj"
        if lead.first_message_signature is None and item.content_text:
            lead.first_message_signature = item.content_text[:255]

        conversation.runtime_state = "em_atendimento"
        conversation.current_step = "whatsapp_intake"
        conversation.strategy_key = conversation.strategy_key or "mcmv_tenda_rj"
        conversation.status = "ativa"
        conversation.last_message_direction = "inbound"
        conversation.idle_started_at = now

        db.add(
            Message(
                tenant_id=tenant.id,
                conversation_id=conversation.id,
                lead_id=lead.id,
                direction="inbound",
                message_type=item.message_type,
                provider_message_id=item.provider_message_id,
                content_text=item.content_text,
                raw_payload=item.raw_payload,
                sent_by_ai=False,
                delivery_status="received",
            )
        )
        db.add(lead)
        db.add(conversation)
        processed += 1

    db.commit()
    return IntakeResult(processed=processed, ignored=ignored)


@dataclass(frozen=True)
class InboundWhatsAppMessage:
    provider_message_id: str | None
    from_phone: str
    profile_name: str | None
    message_type: str
    content_text: str | None
    raw_payload: dict[str, Any]


def iter_inbound_messages(payload: dict[str, Any]) -> list[InboundWhatsAppMessage]:
    messages: list[InboundWhatsAppMessage] = []

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            contacts = {
                contact.get("wa_id"): contact.get("profile", {}).get("name")
                for contact in value.get("contacts", [])
                if contact.get("wa_id")
            }

            for raw_message in value.get("messages", []):
                from_phone = raw_message.get("from")
                if not from_phone:
                    continue

                message_type = raw_message.get("type", "unknown")
                messages.append(
                    InboundWhatsAppMessage(
                        provider_message_id=raw_message.get("id"),
                        from_phone=normalize_phone(from_phone),
                        profile_name=contacts.get(from_phone),
                        message_type=message_type,
                        content_text=extract_text(raw_message, message_type),
                        raw_payload={
                            "entry_id": entry.get("id"),
                            "field": change.get("field"),
                            "metadata": value.get("metadata"),
                            "contact_name": contacts.get(from_phone),
                            "message": raw_message,
                        },
                    )
                )

    return messages


def extract_text(message: dict[str, Any], message_type: str) -> str | None:
    if message_type == "text":
        return message.get("text", {}).get("body")
    if message_type == "button":
        return message.get("button", {}).get("text")
    if message_type == "interactive":
        interactive = message.get("interactive", {})
        return (
            interactive.get("button_reply", {}).get("title")
            or interactive.get("list_reply", {}).get("title")
        )
    return None


def normalize_phone(phone: str) -> str:
    digits = "".join(char for char in phone if char.isdigit())
    return f"+{digits}" if digits else phone


def get_or_create_lead(db: Session, tenant: Tenant, item: InboundWhatsAppMessage) -> Lead:
    lead = db.scalar(
        select(Lead).where(
            Lead.tenant_id == tenant.id,
            Lead.phone == item.from_phone,
        )
    )
    if lead is not None:
        if lead.name is None and item.profile_name:
            lead.name = item.profile_name
        return lead

    lead = Lead(
        tenant_id=tenant.id,
        name=item.profile_name,
        phone=item.from_phone,
        source_channel="whatsapp",
        status="novo",
        assigned_strategy_key="mcmv_tenda_rj",
    )
    db.add(lead)
    db.flush()
    db.add(LeadProfile(tenant_id=tenant.id, lead_id=lead.id))
    db.flush()
    return lead


def get_or_create_active_conversation(db: Session, tenant: Tenant, lead: Lead) -> Conversation:
    conversation = db.scalar(
        select(Conversation)
        .where(
            Conversation.tenant_id == tenant.id,
            Conversation.lead_id == lead.id,
            Conversation.status == "ativa",
        )
        .order_by(Conversation.updated_at.desc())
    )
    if conversation is not None:
        return conversation

    conversation = Conversation(
        tenant_id=tenant.id,
        lead_id=lead.id,
        runtime_state="novo",
        current_step="whatsapp_intake",
        strategy_key="mcmv_tenda_rj",
        status="ativa",
    )
    db.add(conversation)
    db.flush()
    return conversation
