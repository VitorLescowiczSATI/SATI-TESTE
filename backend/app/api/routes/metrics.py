from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_session
from app.db.session import get_db
from app.models.session import UserSession
from app.schemas.metrics import TodayMetricsResponse, ToolCallStatSchema
from app.services.metrics_service import get_today_metrics

router = APIRouter()


@router.get("/today", response_model=TodayMetricsResponse)
def read_today_metrics(
    current_session: UserSession = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> TodayMetricsResponse:
    metrics = get_today_metrics(db, current_session.tenant_id)
    return TodayMetricsResponse(
        leads_today=metrics.leads_today,
        leads_total=metrics.leads_total,
        conversations_active=metrics.conversations_active,
        messages_inbound_today=metrics.messages_inbound_today,
        messages_outbound_today=metrics.messages_outbound_today,
        classification_distribution=metrics.classification_distribution,
        tool_calls_today=[
            ToolCallStatSchema(name=stat.name, count=stat.count)
            for stat in metrics.tool_calls_today
        ],
        last_inbound_at=metrics.last_inbound_at,
        generated_at=metrics.generated_at,
    )
