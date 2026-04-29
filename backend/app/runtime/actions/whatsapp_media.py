"""Download de midia recebida via WhatsApp Cloud API.

Quando o webhook entrega uma mensagem do tipo `audio`, `image`, etc, o
payload traz um `id` de midia. Esse id precisa ser resolvido em duas
chamadas:
1. GET https://graph.facebook.com/v20.0/{media_id}  -> retorna URL temporaria
2. GET dessa URL com o mesmo bearer token -> retorna os bytes
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
class MediaDownload:
    content: bytes
    mime_type: str | None
    filename: str


def download_media(media_id: str, fallback_filename: str = "audio.ogg") -> MediaDownload | None:
    """Baixa o binario de uma midia do WhatsApp Cloud.

    Retorna None se nao houver credenciais configuradas (caso comum em dev).
    """
    access_token = getattr(settings, "whatsapp_access_token", None)
    if not access_token:
        logger.info("WhatsApp access token ausente, pulando download de midia.")
        return None

    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        with httpx.Client(timeout=20.0) as client:
            meta_response = client.get(f"{GRAPH_API_BASE}/{media_id}", headers=headers)
            meta_response.raise_for_status()
            meta = meta_response.json()
            media_url = meta.get("url")
            mime_type = meta.get("mime_type")
            if not media_url:
                logger.warning("Resposta sem URL de midia para %s", media_id)
                return None

            binary_response = client.get(media_url, headers=headers)
            binary_response.raise_for_status()
            content = binary_response.content
    except httpx.HTTPError as exc:
        logger.exception("Falha baixando midia %s: %s", media_id, exc)
        return None

    filename = fallback_filename
    if mime_type and "/" in mime_type:
        ext = mime_type.split("/", 1)[1].split(";", 1)[0]
        filename = f"audio.{ext}" if ext else fallback_filename

    return MediaDownload(content=content, mime_type=mime_type, filename=filename)
