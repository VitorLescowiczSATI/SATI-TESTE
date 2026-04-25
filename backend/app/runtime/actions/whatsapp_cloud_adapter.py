"""Adapter minimo do WhatsApp Cloud API.

Se as credenciais (`whatsapp_phone_number_id`, `whatsapp_access_token`)
estiverem configuradas, envia o texto via Graph API. Caso contrario, retorna
status `pending_send` para o caller registrar no banco.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

GRAPH_API_VERSION = "v20.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


@dataclass(slots=True)
class SendResult:
    status: str  # "sent" | "pending_send" | "failed"
    provider_message_id: str | None = None
    error: str | None = None


def send_text(to_phone: str, text: str) -> SendResult:
    phone_number_id = getattr(settings, "whatsapp_phone_number_id", None)
    access_token = getattr(settings, "whatsapp_access_token", None)

    if not phone_number_id or not access_token:
        logger.info("WhatsApp Cloud sem credenciais, marcando como pending_send.")
        return SendResult(status="pending_send")

    url = f"{GRAPH_API_BASE}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    body = {
        "messaging_product": "whatsapp",
        "to": to_phone.lstrip("+"),
        "type": "text",
        "text": {"body": text},
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(url, headers=headers, json=body)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        logger.exception("Falha enviando WhatsApp Cloud")
        return SendResult(status="failed", error=str(exc))

    provider_id = None
    messages = data.get("messages") or []
    if messages:
        provider_id = messages[0].get("id")
    return SendResult(status="sent", provider_message_id=provider_id)
