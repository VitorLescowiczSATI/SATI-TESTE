from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.conversation import Conversation, Message
from app.schemas.conversation import (
    ConsoleConversationDetail,
    ConsoleConversationSummary,
    ConsoleLead,
    ConsoleMessage,
)


def list_active_conversations(db: Session, tenant_id: str) -> list[ConsoleConversationSummary]:
    conversations = db.scalars(
        select(Conversation)
        .options(joinedload(Conversation.lead))
        .where(Conversation.tenant_id == tenant_id)
        .order_by(Conversation.updated_at.desc())
        .limit(30)
    ).unique()

    return [serialize_summary(db, conversation) for conversation in conversations]


def get_conversation_detail(db: Session, tenant_id: str, conversation_id: str) -> ConsoleConversationDetail | None:
    conversation = db.scalar(
        select(Conversation)
        .options(joinedload(Conversation.lead))
        .where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == tenant_id,
        )
    )
    if conversation is None:
        return None

    messages = db.scalars(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
    ).all()

    summary = serialize_summary(db, conversation)
    return ConsoleConversationDetail(
        **summary.model_dump(),
        messages=[serialize_message(message) for message in messages],
        summary_text=conversation.summary_text,
        classified_at=conversation.classified_at,
    )


def serialize_summary(db: Session, conversation: Conversation) -> ConsoleConversationSummary:
    last_message = db.scalar(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.desc())
        .limit(1)
    )
    message_count = db.scalar(
        select(func.count(Message.id)).where(Message.conversation_id == conversation.id)
    )

    return ConsoleConversationSummary(
        id=conversation.id,
        lead=ConsoleLead(
            id=conversation.lead.id,
            name=conversation.lead.name,
            phone=conversation.lead.phone,
            status=conversation.lead.status,
            classification=conversation.lead.classification,
            source_campaign=conversation.lead.source_campaign,
        ),
        runtime_state=conversation.runtime_state,
        status=conversation.status,
        last_message_direction=conversation.last_message_direction,
        last_message_preview=last_message.content_text if last_message else None,
        message_count=message_count or 0,
        updated_at=conversation.updated_at,
    )


def serialize_message(message: Message) -> ConsoleMessage:
    return ConsoleMessage(
        id=message.id,
        direction=message.direction,
        message_type=message.message_type,
        content_text=message.content_text,
        sent_by_ai=message.sent_by_ai,
        tool_name=message.tool_name,
        delivery_status=message.delivery_status,
        created_at=message.created_at,
    )
