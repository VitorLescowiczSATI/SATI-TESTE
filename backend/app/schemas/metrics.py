from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ToolCallStatSchema(BaseModel):
    name: str
    count: int


class TodayMetricsResponse(BaseModel):
    leads_today: int
    leads_total: int
    conversations_active: int
    messages_inbound_today: int
    messages_outbound_today: int
    classification_distribution: dict[str, int]
    tool_calls_today: list[ToolCallStatSchema]
    last_inbound_at: datetime | None
    generated_at: datetime
