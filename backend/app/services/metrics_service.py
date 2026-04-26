"""Agregacoes pra a tela de Dashboard.

Tudo derivado direto do banco - sem cache, sem materializado. Volume
do MVP-demo nao justifica. Quando passar de 10k leads/dia migrar pra
view materializada ou tabela de daily_metrics.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message
from app.models.lead import Lead


@dataclass(slots=True)
class ToolCallStat:
    name: str
    count: int


@dataclass(slots=True)
class TodayMetrics:
    leads_today: int
    leads_total: int
    conversations_active: int
    messages_inbound_today: int
    messages_outbound_today: int
    classification_distribution: dict[str, int] = field(default_factory=dict)
    tool_calls_today: list[ToolCallStat] = field(default_factory=list)
    last_inbound_at: datetime | None = None
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def get_today_metrics(db: Session, tenant_id: str) -> TodayMetrics:
    today_start = datetime.combine(date.today(), time.min, tzinfo=timezone.utc)

    leads_today = db.scalar(
        select(func.count(Lead.id)).where(
            Lead.tenant_id == tenant_id,
            Lead.created_at >= today_start,
        )
    ) or 0

    leads_total = db.scalar(
        select(func.count(Lead.id)).where(Lead.tenant_id == tenant_id)
    ) or 0

    conversations_active = db.scalar(
        select(func.count(Conversation.id)).where(
            Conversation.tenant_id == tenant_id,
            Conversation.status == "ativa",
        )
    ) or 0

    messages_inbound_today = db.scalar(
        select(func.count(Message.id)).where(
            Message.tenant_id == tenant_id,
            Message.direction == "inbound",
            Message.created_at >= today_start,
        )
    ) or 0

    messages_outbound_today = db.scalar(
        select(func.count(Message.id)).where(
            Message.tenant_id == tenant_id,
            Message.direction == "outbound",
            Message.message_type == "text",
            Message.created_at >= today_start,
        )
    ) or 0

    # Distribuicao por classificacao - de TODOS os leads do tenant.
    # No MVP-demo o volume e baixo; depois trocar pra "leads dos ultimos 30d".
    rows = db.execute(
        select(Lead.classification, func.count(Lead.id))
        .where(Lead.tenant_id == tenant_id)
        .group_by(Lead.classification)
    ).all()
    distribution = {
        (classification or "sem_classificacao"): int(count)
        for classification, count in rows
    }
    # Garante presenca de todas as classes pra UI nao precisar de fallback.
    for key in ("frio", "morno", "quente", "agendado", "corretor", "sem_classificacao"):
        distribution.setdefault(key, 0)

    # Tools chamadas hoje, agregadas por nome.
    tool_rows = db.execute(
        select(Message.tool_name, func.count(Message.id))
        .where(
            Message.tenant_id == tenant_id,
            Message.tool_name.isnot(None),
            Message.created_at >= today_start,
        )
        .group_by(Message.tool_name)
        .order_by(func.count(Message.id).desc())
    ).all()
    tool_calls_today = [
        ToolCallStat(name=name or "desconhecida", count=int(count))
        for name, count in tool_rows
    ]

    last_inbound_at = db.scalar(
        select(func.max(Message.created_at)).where(
            Message.tenant_id == tenant_id,
            Message.direction == "inbound",
        )
    )

    return TodayMetrics(
        leads_today=leads_today,
        leads_total=leads_total,
        conversations_active=conversations_active,
        messages_inbound_today=messages_inbound_today,
        messages_outbound_today=messages_outbound_today,
        classification_distribution=distribution,
        tool_calls_today=tool_calls_today,
        last_inbound_at=last_inbound_at,
    )


# Helper exposto pra testes ou scripts ad-hoc se precisar.
def summarize_classification(leads: list[Lead]) -> dict[str, int]:
    counter: Counter[str] = Counter(
        (lead.classification or "sem_classificacao") for lead in leads
    )
    return dict(counter)
