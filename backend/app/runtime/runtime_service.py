"""Servico runtime unificado: recebe mensagem inbound persistida, executa
o ciclo de OpenAI + function calling, persiste outbound e tool calls,
aplica state_updates ao lead/profile/conversation.

Usado tanto pelo playground quanto pelo webhook do WhatsApp.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any

from fastapi import HTTPException
from openai import OpenAI
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.conversation import Conversation, Message
from app.models.lead import Lead, LeadProfile
from app.runtime.strategies.base import BaseStrategy
from app.runtime.strategies.mcmv_tenda_rj import MCMVTendaRJStrategy
from app.runtime.tools.base import RuntimeTool, ToolExecutionResult
from app.services.lead_analysis_service import refresh_conversation_analysis
from app.services.runtime_config_service import build_runtime_prompt, get_published_runtime_config

logger = logging.getLogger(__name__)
settings = get_settings()


STRATEGY_REGISTRY: dict[str, type[BaseStrategy]] = {
    MCMVTendaRJStrategy.config.key: MCMVTendaRJStrategy,
}

DEFAULT_STRATEGY_KEY = MCMVTendaRJStrategy.config.key
MAX_TOOL_LOOPS = 5


@dataclass(slots=True)
class ToolCallTrace:
    name: str
    payload: dict[str, Any]
    result_text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RuntimeResponse:
    assistant_text: str
    assistant_chunks: list[str]
    tool_calls: list[ToolCallTrace]
    finish_reason: str | None = None


MAX_CHUNKS_PER_TURN = 3
MAX_CHARS_PER_CHUNK = 600


# Anexado pelo runtime apos o prompt do agent (operador nao pode desligar).
# Garante que tools e splitting funcionem mesmo se o admin editar o prompt.
HARDCODED_RULES_FOOTER = """
# Regras criticas do runtime SATI (nao remover)

## Tools disponiveis

Voce TEM acesso as seguintes funcoes (function calling). Use-as ao inves de
descrever em texto que vai fazer:

- `simula(proof_of_income_type, uses_fgts, family_income)` -> CHAME assim que
  tiver os 3 dados da simulacao inicial. Nao diga "vou simular" sem chamar.
- `simula_completo(employment_history_months, marital_status, birth_date, dependents_summary)`
  -> CHAME apos coletar todos os 4 campos da simulacao completa.
- `schedule_time(date, time)` -> CHAME assim que tiver dia E horario claros do
  pre-agendamento. Formate date como YYYY-MM-DD e time como HH:MM (24h).
- `send_media(project_slug, media_type)` -> CHAME quando o lead pedir material
  de um empreendimento.

REGRA: se voce ja coletou os dados necessarios, CHAME a funcao na mesma
resposta. Nao prometa "vou fazer mais a frente". A SATI persiste o resultado
no banco assim que voce chama.

## Formato obrigatorio de resposta

- Toda resposta deve ser dividida em 1 a 3 mensagens curtas, separadas por
  UMA linha em branco.
- Cada mensagem tem no maximo 2 frases.
- Sem markdown pesado, sem listas numeradas em rajada, sem bullets pesados.
""".strip()


def split_assistant_text(text: str) -> list[str]:
    """Quebra a resposta da Maju em mensagens curtas como o Nicochat faz.

    Usa linha em branco (`\\n\\n`) como separador primario. Se nao houver
    quebra, devolve uma unica mensagem. Limita a 3 mensagens por turno.
    """
    cleaned = (text or "").strip()
    if not cleaned:
        return []
    raw_chunks = [chunk.strip() for chunk in cleaned.split("\n\n") if chunk.strip()]
    if not raw_chunks:
        return [cleaned]
    if len(raw_chunks) > MAX_CHUNKS_PER_TURN:
        # Junta o excesso na ultima permitida pra nao perder conteudo.
        head = raw_chunks[: MAX_CHUNKS_PER_TURN - 1]
        tail = " ".join(raw_chunks[MAX_CHUNKS_PER_TURN - 1 :])
        raw_chunks = head + [tail]
    return [chunk[:MAX_CHARS_PER_CHUNK] for chunk in raw_chunks]


def resolve_strategy(strategy_key: str | None) -> type[BaseStrategy]:
    key = strategy_key or DEFAULT_STRATEGY_KEY
    strategy = STRATEGY_REGISTRY.get(key)
    if strategy is None:
        logger.warning("Strategy '%s' nao registrada, usando default '%s'", key, DEFAULT_STRATEGY_KEY)
        return STRATEGY_REGISTRY[DEFAULT_STRATEGY_KEY]
    return strategy


def process_inbound(
    db: Session,
    *,
    conversation: Conversation,
    inbound_message: Message,
    source_label: str = "playground",
) -> RuntimeResponse:
    """Executa o ciclo completo a partir do inbound ja persistido."""
    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY nao configurada no backend.")

    lead = conversation.lead
    strategy_cls = resolve_strategy(conversation.strategy_key or lead.assigned_strategy_key)
    tool_registry = strategy_cls.tool_registry()
    tool_schemas_openai = _openai_tool_schemas(strategy_cls)

    runtime_config = (
        conversation.runtime_config_version
        if conversation.runtime_config_version is not None
        else get_published_runtime_config(db, conversation.tenant_id)
    )
    base_instructions = build_runtime_prompt(db, runtime_config)
    instructions = f"{base_instructions}\n\n{HARDCODED_RULES_FOOTER}"
    model = runtime_config.agent_config.model or strategy_cls.config.model or settings.openai_model
    max_tokens = runtime_config.agent_config.max_tokens or strategy_cls.config.max_tokens

    history_messages = _load_chat_history(db, conversation)
    chat_messages: list[dict[str, Any]] = [{"role": "system", "content": instructions}]
    chat_messages.extend(history_messages)

    client = OpenAI(api_key=settings.openai_api_key)
    tool_traces: list[ToolCallTrace] = []
    finish_reason: str | None = None
    assistant_text = ""

    for loop_index in range(MAX_TOOL_LOOPS):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=chat_messages,
                tools=tool_schemas_openai or None,
                tool_choice="auto" if tool_schemas_openai else None,
                max_tokens=max_tokens,
                temperature=runtime_config.agent_config.temperature or 0.4,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Erro chamando OpenAI no runtime_service")
            raise HTTPException(status_code=502, detail=f"Falha chamando OpenAI: {exc}") from exc

        choice = completion.choices[0]
        finish_reason = choice.finish_reason
        message = choice.message

        if message.tool_calls:
            chat_messages.append(
                {
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [
                        {
                            "id": call.id,
                            "type": "function",
                            "function": {
                                "name": call.function.name,
                                "arguments": call.function.arguments or "{}",
                            },
                        }
                        for call in message.tool_calls
                    ],
                }
            )

            for call in message.tool_calls:
                tool_name = call.function.name
                raw_arguments = call.function.arguments or "{}"
                try:
                    arguments_dict = json.loads(raw_arguments) if raw_arguments else {}
                except json.JSONDecodeError:
                    arguments_dict = {"_raw": raw_arguments}

                trace = _execute_tool(
                    db,
                    conversation=conversation,
                    lead=lead,
                    tool_registry=tool_registry,
                    tool_name=tool_name,
                    arguments=arguments_dict,
                    source_label=source_label,
                )
                tool_traces.append(trace)
                chat_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": trace.result_text,
                    }
                )
            # Loop again so the model produces final text after tool results.
            continue

        # No more tool calls -> final assistant text.
        assistant_text = (message.content or "").strip()
        break
    else:
        logger.warning("Runtime loop atingiu MAX_TOOL_LOOPS sem resposta final.")
        assistant_text = (
            "Desculpa, tive um problema tecnico para te responder agora. "
            "Pode me mandar a pergunta de novo?"
        )

    if not assistant_text:
        assistant_text = (
            "Consegui te acompanhar por aqui. "
            "Pode me mandar mais uma mensagem pra eu continuar?"
        )

    chunks = split_assistant_text(assistant_text)
    now = datetime.now(timezone.utc)
    initial_status = "sent" if source_label == "playground" else "pending_send"
    for index, chunk in enumerate(chunks):
        db.add(
            Message(
                tenant_id=conversation.tenant_id,
                conversation_id=conversation.id,
                lead_id=lead.id,
                direction="outbound",
                message_type="text",
                content_text=chunk,
                raw_payload={
                    "source": "openai",
                    "mode": source_label,
                    "finish_reason": finish_reason,
                    "chunk_index": index,
                    "chunk_total": len(chunks),
                },
                sent_by_ai=True,
                delivery_status=initial_status,
            )
        )
    conversation.last_message_direction = "outbound"
    lead.last_outbound_at = now

    refresh_conversation_analysis(db, conversation)
    db.add(lead)
    db.add(conversation)

    return RuntimeResponse(
        assistant_text=assistant_text,
        assistant_chunks=chunks,
        tool_calls=tool_traces,
        finish_reason=finish_reason,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _openai_tool_schemas(strategy_cls: type[BaseStrategy]) -> list[dict[str, Any]]:
    schemas: list[dict[str, Any]] = []
    for tool_cls in strategy_cls.tools:
        json_schema = _clean_schema_for_openai(tool_cls.json_schema())
        schemas.append(
            {
                "type": "function",
                "function": {
                    "name": tool_cls.name,
                    "description": tool_cls.description,
                    "parameters": json_schema,
                },
            }
        )
    return schemas


def _clean_schema_for_openai(schema: dict[str, Any]) -> dict[str, Any]:
    """Remove campos que confundem o function calling da OpenAI:
    `title` redundante, defaults excessivos, e garante que cada propriedade
    tenha description (cai pra title se nao tiver)."""
    cleaned = dict(schema)
    cleaned.pop("title", None)
    cleaned.pop("$defs", None)
    cleaned["type"] = cleaned.get("type", "object")
    cleaned["additionalProperties"] = False

    properties = dict(cleaned.get("properties", {}))
    for name, prop_schema in properties.items():
        if not isinstance(prop_schema, dict):
            continue
        prop_clean = dict(prop_schema)
        # OpenAI mostra a description ao modelo - melhor ter algo.
        if "description" not in prop_clean:
            prop_clean["description"] = prop_clean.pop("title", name)
        else:
            prop_clean.pop("title", None)
        # `anyOf` com null e padrao do Pydantic pra Optional - simplifica.
        any_of = prop_clean.get("anyOf")
        if isinstance(any_of, list):
            non_null = [item for item in any_of if item.get("type") != "null"]
            if len(non_null) == 1:
                prop_clean.pop("anyOf", None)
                prop_clean.update(non_null[0])
        properties[name] = prop_clean
    cleaned["properties"] = properties
    return cleaned


def _load_chat_history(db: Session, conversation: Conversation) -> list[dict[str, Any]]:
    messages = db.scalars(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
    ).all()

    history: list[dict[str, Any]] = []
    for msg in messages:
        if msg.tool_name:
            # Mensagens de tool ja persistidas em rodadas anteriores. Como
            # nao guardamos o tool_call_id da OpenAI, regenerar o tool ciclo
            # antigo quebraria. Solucao: incluir como nota do sistema breve.
            history.append(
                {
                    "role": "system",
                    "content": f"[tool {msg.tool_name} executada anteriormente] {msg.tool_result_text or ''}",
                }
            )
            continue
        if not msg.content_text:
            continue
        role = "user" if msg.direction == "inbound" else "assistant"
        history.append({"role": role, "content": msg.content_text})
    return history


def _execute_tool(
    db: Session,
    *,
    conversation: Conversation,
    lead: Lead,
    tool_registry: dict[str, RuntimeTool[Any]],
    tool_name: str,
    arguments: dict[str, Any],
    source_label: str,
) -> ToolCallTrace:
    tool = tool_registry.get(tool_name)
    if tool is None:
        result_text = f"[erro] tool '{tool_name}' nao registrada na strategy."
        _persist_tool_message(
            db,
            conversation=conversation,
            lead=lead,
            tool_name=tool_name,
            payload=arguments,
            result_text=result_text,
            source_label=source_label,
        )
        return ToolCallTrace(name=tool_name, payload=arguments, result_text=result_text)

    try:
        payload = tool.parse_payload(arguments)
        result: ToolExecutionResult = tool.execute(payload)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Erro executando tool %s", tool_name)
        result_text = f"[erro] {exc}"
        _persist_tool_message(
            db,
            conversation=conversation,
            lead=lead,
            tool_name=tool_name,
            payload=arguments,
            result_text=result_text,
            source_label=source_label,
        )
        return ToolCallTrace(name=tool_name, payload=arguments, result_text=result_text)

    _apply_state_updates(db, lead=lead, conversation=conversation, state_updates=result.state_updates)
    _persist_tool_message(
        db,
        conversation=conversation,
        lead=lead,
        tool_name=tool_name,
        payload=arguments,
        result_text=result.message_to_agent,
        source_label=source_label,
        metadata=result.metadata,
    )
    return ToolCallTrace(
        name=tool_name,
        payload=arguments,
        result_text=result.message_to_agent,
        metadata=result.metadata,
    )


def _persist_tool_message(
    db: Session,
    *,
    conversation: Conversation,
    lead: Lead,
    tool_name: str,
    payload: dict[str, Any],
    result_text: str,
    source_label: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    db.add(
        Message(
            tenant_id=conversation.tenant_id,
            conversation_id=conversation.id,
            lead_id=lead.id,
            direction="outbound",
            message_type="tool_call",
            content_text=None,
            raw_payload={"source": source_label, "metadata": metadata or {}},
            sent_by_ai=True,
            tool_name=tool_name,
            tool_payload=payload,
            tool_result_text=result_text,
            delivery_status="internal",
        )
    )


def _apply_state_updates(
    db: Session,
    *,
    lead: Lead,
    conversation: Conversation,
    state_updates: dict[str, Any],
) -> None:
    if not state_updates:
        return

    profile = lead.profile
    if profile is None:
        profile = LeadProfile(tenant_id=lead.tenant_id, lead_id=lead.id)
        db.add(profile)
        db.flush()
        lead.profile = profile

    for key, value in (state_updates.get("lead_profile") or {}).items():
        if not hasattr(profile, key):
            continue
        setattr(profile, key, _coerce_profile_value(key, value))

    for key, value in (state_updates.get("lead") or {}).items():
        if hasattr(lead, key):
            setattr(lead, key, value)

    for key, value in (state_updates.get("conversation") or {}).items():
        if hasattr(conversation, key):
            setattr(conversation, key, value)

    db.add(profile)
    db.add(lead)
    db.add(conversation)


def _coerce_profile_value(field_name: str, value: Any) -> Any:
    if value is None:
        return None
    if field_name == "birth_date" and isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    if field_name == "scheduled_at" and isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    return value
