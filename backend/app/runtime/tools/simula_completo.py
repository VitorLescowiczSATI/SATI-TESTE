from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from app.runtime.tools.base import RuntimeTool, ToolExecutionResult


class SimulaCompletoPayload(BaseModel):
    employment_history_months: int = Field(ge=0)
    marital_status: str = Field(min_length=2, max_length=40)
    birth_date: date
    dependents_summary: str | None = Field(default=None, max_length=255)


class SimulaCompletoTool(RuntimeTool[SimulaCompletoPayload]):
    name = "simula_completo"
    description = "Registra os dados complementares da simulacao completa."
    payload_model = SimulaCompletoPayload

    def execute(self, payload: SimulaCompletoPayload) -> ToolExecutionResult:
        return ToolExecutionResult(
            message_to_agent=(
                "Anotado! Diga que ja passou para o especialista iniciar a simulacao "
                "e que entrara em contato em breve."
            ),
            state_updates={
                "lead_profile": {
                    "employment_history_months": payload.employment_history_months,
                    "marital_status": payload.marital_status,
                    "birth_date": payload.birth_date.isoformat(),
                    "dependents_summary": payload.dependents_summary,
                },
                "conversation": {
                    "current_step": "simulacao_completa_concluida",
                },
            },
            tags_to_add=["simulacao_completa"],
        )
