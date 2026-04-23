from __future__ import annotations

from pydantic import BaseModel, Field

from app.runtime.tools.base import RuntimeTool, ToolExecutionResult


class SendMediaPayload(BaseModel):
    project_slug: str = Field(min_length=2, max_length=160)
    media_type: str | None = Field(default=None, max_length=60)


class SendMediaTool(RuntimeTool[SendMediaPayload]):
    name = "send_media"
    description = "Envia materiais de um empreendimento de forma estruturada."
    payload_model = SendMediaPayload

    def execute(self, payload: SendMediaPayload) -> ToolExecutionResult:
        return ToolExecutionResult(
            message_to_agent="Enviado. Pergunte o que achou do empreendimento.",
            state_updates={
                "conversation": {
                    "current_step": "midia_enviada",
                },
            },
            tags_to_add=["recebeu_imagens"],
            metadata={
                "project_slug": payload.project_slug,
                "media_type": payload.media_type,
            },
        )
