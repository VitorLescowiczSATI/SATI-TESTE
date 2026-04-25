from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.conversation import Conversation, Message
from app.models.lead import Lead, LeadProfile
from app.schemas.admin import AdminLeadDetail, AdminLeadProfile, AdminLeadSummary
from app.services.conversation_console_service import get_conversation_detail
from app.services.lead_analysis_service import build_facilita_payload, refresh_conversation_analysis


def list_admin_leads(db: Session, tenant_id: str) -> list[AdminLeadSummary]:
    leads = db.scalars(
        select(Lead)
        .where(Lead.tenant_id == tenant_id)
        .order_by(Lead.updated_at.desc())
        .limit(100)
    ).all()
    return [serialize_admin_lead_summary(db, lead) for lead in leads]


def get_admin_lead_detail(db: Session, tenant_id: str, lead_id: str) -> AdminLeadDetail | None:
    lead = db.scalar(
        select(Lead)
        .options(joinedload(Lead.profile))
        .where(
            Lead.id == lead_id,
            Lead.tenant_id == tenant_id,
        )
    )
    if lead is None:
        return None

    conversation = get_latest_conversation(db, lead)
    if conversation is not None:
        refresh_conversation_analysis(db, conversation)
        db.commit()
        db.refresh(lead)
        db.refresh(conversation)

    summary = serialize_admin_lead_summary(db, lead)
    latest_conversation = (
        get_conversation_detail(db, tenant_id, conversation.id)
        if conversation is not None
        else None
    )

    return AdminLeadDetail(
        **summary.model_dump(),
        profile=serialize_profile(lead.profile),
        latest_conversation=latest_conversation,
        facilita_payload_preview=build_facilita_payload(lead, conversation) if conversation else None,
    )


def refresh_admin_lead_analysis(db: Session, tenant_id: str, lead_id: str) -> AdminLeadDetail | None:
    detail = get_admin_lead_detail(db, tenant_id, lead_id)
    return detail


def delete_admin_lead(db: Session, tenant_id: str, lead_id: str) -> bool:
    lead = db.scalar(
        select(Lead).where(
            Lead.id == lead_id,
            Lead.tenant_id == tenant_id,
        )
    )
    if lead is None:
        return False
    db.delete(lead)
    db.commit()
    return True


def get_latest_conversation(db: Session, lead: Lead) -> Conversation | None:
    return db.scalar(
        select(Conversation)
        .where(
            Conversation.lead_id == lead.id,
            Conversation.tenant_id == lead.tenant_id,
        )
        .order_by(Conversation.updated_at.desc())
        .limit(1)
    )


def serialize_admin_lead_summary(db: Session, lead: Lead) -> AdminLeadSummary:
    conversation_count = db.scalar(
        select(func.count(Conversation.id)).where(Conversation.lead_id == lead.id)
    )
    message_count = db.scalar(
        select(func.count(Message.id)).where(Message.lead_id == lead.id)
    )
    return AdminLeadSummary(
        id=lead.id,
        name=lead.name,
        phone=lead.phone,
        status=lead.status,
        classification=lead.classification,
        classification_reason=lead.classification_reason,
        source_channel=lead.source_channel,
        source_campaign=lead.source_campaign,
        conversation_count=conversation_count or 0,
        message_count=message_count or 0,
        updated_at=lead.updated_at,
    )


def serialize_profile(profile: LeadProfile | None) -> AdminLeadProfile | None:
    if profile is None:
        return None
    return AdminLeadProfile(
        proof_of_income_type=profile.proof_of_income_type,
        uses_fgts=profile.uses_fgts,
        family_income=profile.family_income,
        entry_amount=profile.entry_amount,
        has_property=profile.has_property,
        employment_history_months=profile.employment_history_months,
        marital_status=profile.marital_status,
        birth_date=profile.birth_date.isoformat() if profile.birth_date else None,
        dependents_summary=profile.dependents_summary,
        interest_project=profile.interest_project,
        interest_region=profile.interest_region,
        scheduled_at=profile.scheduled_at.isoformat() if profile.scheduled_at else None,
    )
