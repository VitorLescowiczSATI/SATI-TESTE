from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models.tenant import Tenant
from app.services.whatsapp_intake_service import process_whatsapp_webhook

router = APIRouter()
settings = get_settings()


@router.get("", response_class=PlainTextResponse)
def verify_webhook(
    mode: str = Query(alias="hub.mode"),
    verify_token: str = Query(alias="hub.verify_token"),
    challenge: str = Query(alias="hub.challenge"),
) -> str:
    if mode != "subscribe":
        raise HTTPException(status_code=400, detail="Modo de verificacao invalido.")

    if not settings.whatsapp_verify_token or verify_token != settings.whatsapp_verify_token:
        raise HTTPException(status_code=403, detail="Token de verificacao invalido.")

    return challenge


@router.post("")
async def receive_webhook(request: Request, db: Session = Depends(get_db)) -> dict[str, Any]:
    tenant = db.scalar(select(Tenant).where(Tenant.slug == settings.whatsapp_default_tenant_slug))
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant padrao do WhatsApp nao encontrado.")

    payload = await request.json()
    result = process_whatsapp_webhook(db, tenant, payload)
    return {"ok": True, "processed": result.processed, "ignored": result.ignored}
