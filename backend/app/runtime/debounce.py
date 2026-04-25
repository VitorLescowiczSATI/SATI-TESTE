"""Debounce coordinator por conversation_id.

Quando uma mensagem chega, agendamos o processamento real para daqui
`debounce_seconds` segundos. Se chegar outra mensagem antes disso,
cancelamos o timer e reagendamos. Assim, varias mensagens rapidas do
mesmo lead viram UMA chamada ao LLM, replicando o comportamento do
Nicochat (input_debounce_seconds=7 na MCMVTendaRJStrategy).

Implementacao in-process com asyncio.Task. Funciona em uma instancia
do FastAPI; pra producao com varios workers, migrar pra Redis/Celery.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Callable

logger = logging.getLogger(__name__)

_pending_tasks: dict[str, asyncio.Task] = {}


def schedule_debounced(
    *,
    conversation_id: str,
    delay_seconds: float,
    coro_factory: Callable[[], Awaitable[None]],
) -> None:
    """Agenda `coro_factory()` pra rodar daqui `delay_seconds`.

    Se ja existe um task pendente pra essa conversation_id, cancela
    antes de reagendar.
    """
    existing = _pending_tasks.get(conversation_id)
    if existing is not None and not existing.done():
        existing.cancel()
        logger.debug("Debounce cancelado para conversation %s", conversation_id)

    async def _runner() -> None:
        try:
            await asyncio.sleep(delay_seconds)
            await coro_factory()
        except asyncio.CancelledError:
            logger.debug("Debounce task cancelado para conversation %s", conversation_id)
            raise
        except Exception:  # noqa: BLE001
            logger.exception("Erro no runner debounced de conversation %s", conversation_id)
        finally:
            current = _pending_tasks.get(conversation_id)
            if current is not None and current.done():
                _pending_tasks.pop(conversation_id, None)

    task = asyncio.create_task(_runner())
    _pending_tasks[conversation_id] = task


def has_pending(conversation_id: str) -> bool:
    task = _pending_tasks.get(conversation_id)
    return task is not None and not task.done()
