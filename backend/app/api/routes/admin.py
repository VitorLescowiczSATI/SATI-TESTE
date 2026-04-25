from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_session
from app.db.session import get_db
from app.models.session import UserSession
from app.schemas.admin import AdminLeadDetail, AdminLeadSummary, AdminRuntimeConfig, AdminRuntimeConfigUpdate
from app.services.admin_service import (
    delete_admin_lead,
    get_admin_lead_detail,
    list_admin_leads,
    refresh_admin_lead_analysis,
)
from app.services.runtime_config_service import get_runtime_config_payload, update_runtime_config

router = APIRouter()


@router.get("/runtime-config", response_model=AdminRuntimeConfig)
def read_runtime_config(
    current_session: UserSession = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> AdminRuntimeConfig:
    return AdminRuntimeConfig.model_validate(
        get_runtime_config_payload(db, current_session.tenant_id)
    )


@router.patch("/runtime-config", response_model=AdminRuntimeConfig)
def patch_runtime_config(
    payload: AdminRuntimeConfigUpdate,
    current_session: UserSession = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> AdminRuntimeConfig:
    update_runtime_config(
        db,
        current_session.tenant_id,
        model=payload.model,
        max_tokens=payload.max_tokens,
        temperature=payload.temperature,
        system_prompt=payload.system_prompt,
        enabled_tools=payload.enabled_tools,
    )
    return AdminRuntimeConfig.model_validate(
        get_runtime_config_payload(db, current_session.tenant_id)
    )


@router.get("/leads", response_model=list[AdminLeadSummary])
def read_leads(
    current_session: UserSession = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> list[AdminLeadSummary]:
    return list_admin_leads(db, current_session.tenant_id)


@router.get("/leads/{lead_id}", response_model=AdminLeadDetail)
def read_lead_detail(
    lead_id: str,
    current_session: UserSession = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> AdminLeadDetail:
    detail = get_admin_lead_detail(db, current_session.tenant_id, lead_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Lead nao encontrado.")
    return detail


@router.post("/leads/{lead_id}/refresh-analysis", response_model=AdminLeadDetail)
def refresh_lead_analysis(
    lead_id: str,
    current_session: UserSession = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> AdminLeadDetail:
    detail = refresh_admin_lead_analysis(db, current_session.tenant_id, lead_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Lead nao encontrado.")
    return detail


@router.delete("/leads/{lead_id}", status_code=204)
def delete_lead(
    lead_id: str,
    current_session: UserSession = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> Response:
    deleted = delete_admin_lead(db, current_session.tenant_id, lead_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Lead nao encontrado.")
    return Response(status_code=204)
