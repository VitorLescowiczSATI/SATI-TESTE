from __future__ import annotations

from pydantic import BaseModel, Field

from app.runtime.policies.scheduling import normalize_schedule_datetime
from app.runtime.tools.base import RuntimeTool, ToolExecutionResult


class ScheduleTimePayload(BaseModel):
    date: str = Field(min_length=8, max_length=10)
    time: str = Field(min_length=4, max_length=5)


class ScheduleTimeTool(RuntimeTool[ScheduleTimePayload]):
    name = "schedule_time"
    description = "Registra o pre-agendamento de conversa ou visita."
    payload_model = ScheduleTimePayload

    def execute(self, payload: ScheduleTimePayload) -> ToolExecutionResult:
        scheduled_at = normalize_schedule_datetime(payload.date, payload.time)
        return ToolExecutionResult(
            message_to_agent=(
                "Agendado com sucesso! Diga que em breve o especialista "
                "entrara em contato para confirmar."
            ),
            state_updates={
                "lead": {
                    "status": "agendado",
                },
                "lead_profile": {
                    "schedule_date_raw": payload.date,
                    "schedule_time_raw": payload.time,
                    "scheduled_at": scheduled_at.isoformat(),
                },
                "conversation": {
                    "current_step": "agendamento_concluido",
                },
            },
            tags_to_add=["agendado"],
            metadata={"scheduled_at": scheduled_at.isoformat()},
        )
