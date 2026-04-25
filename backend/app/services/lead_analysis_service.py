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
    """Classifica o lead pelo ESTADO REAL verificavel (tools chamadas e dados
    estruturados), nao por keywords no texto. Heuristica de texto entra
    apenas pra detectar corretor/parceiro e como sinal fraco de "morno"."""
    text = " ".join((message.content_text or "").lower() for message in messages)
    inbound_count = sum(1 for m in messages if m.direction == "inbound")
    tool_names = {m.tool_name for m in messages if m.tool_name}

    # 1) Corretor/parceiro - heuristica de texto e suficiente, e raro.
    if any(keyword in text for keyword in ("sou corretor", "sou imobiliaria", "parceria")):
        return "corretor", "Contato parece corretor/imobiliaria, nao lead comprador final."

    # 2) Agendado - SO se a tool schedule_time foi chamada e gravou data.
    if profile and profile.scheduled_at:
        return "agendado", "Pre-agendamento confirmado via tool schedule_time."

    # 3) Quente - sinais estruturados coletados via tool.
    if "simula_completo" in tool_names:
        return "quente", "Simulacao completa registrada (dados completos coletados)."
    if "simula" in tool_names or (profile and profile.family_income):
        return "quente", "Simulacao inicial registrada com renda e comprovacao."

    # 4) Morno - lead engajou e mostrou interesse mas ainda nao gerou tool.
    has_buying_intent = any(
        keyword in text
        for keyword in (
            "simular", "simulacao", "renda", "fgts", "entrada", "parcela",
            "apartamento", "empreendimento", "minha casa minha vida", "mcmv",
            "quero ver", "quero saber", "tenho interesse",
        )
    )
    if inbound_count >= 3 and has_buying_intent:
        return "morno", "Lead demonstrou interesse mas ainda nao concluiu simulacao."

    # 5) Frio - default.
    if inbound_count <= 1:
        return "frio", "Lead ainda tem pouca interacao."
    return "frio", "Conversa em andamento sem dados estruturados ainda."


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
