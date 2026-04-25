from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message
from app.models.lead import Lead, LeadProfile


def refresh_conversation_analysis(db: Session, conversation: Conversation) -> None:
    lead = conversation.lead
    profile = lead.profile
    messages = db.scalars(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
    ).all()

    classification, reason = classify_lead(lead, profile, messages)
    summary = build_summary_text(lead, profile, messages, classification)

    lead.classification = classification
    lead.classification_reason = reason
    conversation.summary_text = summary
    conversation.summary_generated_at = datetime.now(timezone.utc)
    conversation.classified_at = datetime.now(timezone.utc)

    db.add(lead)
    db.add(conversation)


def classify_lead(
    lead: Lead,
    profile: LeadProfile | None,
    messages: list[Message],
) -> tuple[str, str]:
    text = " ".join((message.content_text or "").lower() for message in messages)

    if any(keyword in text for keyword in ("sou corretor", "sou imobiliaria", "parceria")):
        return "corretor", "Contato parece ser corretor/imobiliaria, nao lead comprador final."

    if profile and profile.scheduled_at:
        return "agendado", "Lead tem pre-agendamento registrado."

    if any(keyword in text for keyword in ("visita", "visitar", "agendar", "sabado", "domingo")):
        return "agendado", "Lead demonstrou intencao clara de agendamento ou visita."

    has_simulation_data = bool(
        profile
        and (
            profile.family_income
            or profile.uses_fgts is not None
            or profile.proof_of_income_type
            or profile.interest_project
            or profile.interest_region
        )
    )
    has_buying_intent = any(
        keyword in text
        for keyword in (
            "simular",
            "simulacao",
            "renda",
            "fgts",
            "entrada",
            "parcela",
            "apartamento",
            "empreendimento",
            "minha casa minha vida",
            "mcmv",
        )
    )

    if has_simulation_data or has_buying_intent:
        return "quente", "Lead trouxe sinais de compra/simulacao ou dados comerciais relevantes."

    if len([message for message in messages if message.direction == "inbound"]) <= 1:
        return "frio", "Lead ainda tem pouca interacao e nenhum dado de simulacao."

    return "frio", "Conversa ainda nao mostrou dados suficientes para qualificacao."


def build_summary_text(
    lead: Lead,
    profile: LeadProfile | None,
    messages: list[Message],
    classification: str,
) -> str:
    inbound_messages = [message.content_text for message in messages if message.direction == "inbound" and message.content_text]
    last_inbound = inbound_messages[-1] if inbound_messages else "sem mensagem do lead ainda"

    fields: list[str] = []
    if profile:
        if profile.interest_project:
            fields.append(f"Empreendimento: {profile.interest_project}")
        if profile.interest_region:
            fields.append(f"Regiao: {profile.interest_region}")
        if profile.family_income:
            fields.append(f"Renda familiar: R$ {profile.family_income:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        if profile.uses_fgts is not None:
            fields.append(f"FGTS: {'sim' if profile.uses_fgts else 'nao'}")
        if profile.proof_of_income_type:
            fields.append(f"Comprovacao: {profile.proof_of_income_type}")
        if profile.scheduled_at:
            fields.append(f"Agendamento: {profile.scheduled_at.isoformat()}")

    fields_text = "; ".join(fields) if fields else "sem dados estruturados coletados ainda"
    return (
        f"Lead {lead.name or lead.phone} classificado como {classification}. "
        f"Ultima mensagem: \"{last_inbound}\". "
        f"Dados coletados: {fields_text}."
    )


def build_facilita_payload(lead: Lead, conversation: Conversation) -> dict:
    profile = lead.profile
    return {
        "provider": "facilita",
        "mode": "preview",
        "lead": {
            "id": lead.id,
            "nome": lead.name,
            "telefone": lead.phone,
            "origem": lead.source_channel,
            "campanha": lead.source_campaign,
            "status": lead.status,
            "classificacao": lead.classification,
            "motivo_classificacao": lead.classification_reason,
        },
        "resumo_atendimento": conversation.summary_text,
        "proximo_passo": next_step_for_classification(lead.classification),
        "dados_simulacao": {
            "comprovacao_renda": profile.proof_of_income_type if profile else None,
            "usa_fgts": profile.uses_fgts if profile else None,
            "renda_familiar": profile.family_income if profile else None,
            "entrada": profile.entry_amount if profile else None,
            "tempo_carteira_meses": profile.employment_history_months if profile else None,
            "estado_civil": profile.marital_status if profile else None,
            "data_nascimento": profile.birth_date.isoformat() if profile and profile.birth_date else None,
            "dependentes": profile.dependents_summary if profile else None,
            "empreendimento_interesse": profile.interest_project if profile else None,
            "regiao_interesse": profile.interest_region if profile else None,
            "agendamento": profile.scheduled_at.isoformat() if profile and profile.scheduled_at else None,
        },
        "metadados_sati": {
            "conversation_id": conversation.id,
            "runtime_state": conversation.runtime_state,
            "strategy_key": conversation.strategy_key,
            "config_version_id": conversation.config_version_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }


def next_step_for_classification(classification: str | None) -> str:
    if classification == "agendado":
        return "Confirmar horario e direcionar para corretor responsavel."
    if classification == "quente":
        return "Priorizar contato humano para simulacao e tentativa de agendamento."
    if classification == "corretor":
        return "Encaminhar para avaliacao interna antes de tratar como lead comprador."
    return "Manter nutricao leve ou aguardar nova interacao."
