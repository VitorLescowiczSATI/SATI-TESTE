"""Servico de transcricao de audio via OpenAI Whisper.

Usado tanto pelo intake do WhatsApp (audio recebido do lead) quanto pelo
endpoint de playground (audio enviado via upload pra testes manuais).
"""
from __future__ import annotations

import io
import logging

from fastapi import HTTPException
from openai import OpenAI

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Whisper-1 aceita ate 25MB. Limita aqui pra falhar cedo com mensagem clara.
MAX_AUDIO_BYTES = 24 * 1024 * 1024


def transcribe(audio_bytes: bytes, filename: str = "audio.ogg", language: str = "pt") -> str:
    """Transcreve um audio em bytes para texto.

    `filename` e usado pra Whisper inferir o formato pelo extension. WhatsApp
    Cloud entrega audio em ogg/opus por padrao - default coerente.
    """
    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY nao configurada no backend.")

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Audio vazio.")

    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Audio acima do limite de {MAX_AUDIO_BYTES // 1024 // 1024}MB do Whisper.",
        )

    buffer = io.BytesIO(audio_bytes)
    buffer.name = filename  # Whisper usa o nome pra detectar formato

    client = OpenAI(api_key=settings.openai_api_key)
    try:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=buffer,
            language=language,
            response_format="text",
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Erro chamando Whisper")
        raise HTTPException(status_code=502, detail=f"Falha transcrevendo audio: {exc}") from exc

    # response_format="text" retorna string direta na nova SDK
    text = response if isinstance(response, str) else getattr(response, "text", "")
    return (text or "").strip()
