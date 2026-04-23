from __future__ import annotations

from pydantic import BaseModel, Field

from app.runtime.tools.base import RuntimeTool, ToolExecutionResult


class SimulaPayload(BaseModel):
    proof_of_income_type: str = Field(min_length=2, max_length=60)
    uses_fgts: bool | None = None
    family_income: float = Field(gt=0)


class SimulaTool(RuntimeTool[SimulaPayload]):
    name = "simula"
    description = "Registra os dados da simulacao inicial do lead."
    payload_model = SimulaPayload

    def execute(self, payload: SimulaPayload) -> ToolExecutionResult:
        return ToolExecutionResult(
            message_to_agent=(
                "Anotado! Diga que ja passou para o especialista iniciar a simulacao "
                "e que entrara em contato em breve."
            ),
            state_updates={
                "lead_profile": {
                    "proof_of_income_type": payload.proof_of_income_type,
                    "uses_fgts": payload.uses_fgts,
                    "family_income": payload.family_income,
                },
                "conversation": {
                    "current_step": "simulacao_inicial_concluida",
                },
            },
            tags_to_add=["simulacao_inicial"],
        )
