from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_session
from app.core.config import get_settings
from app.db.session import get_db
from app.models.session import UserSession
from app.schemas.auth import LoginRequest, SessionResponse, TenantSummary
from app.services.auth_service import authenticate_user, create_session, revoke_session

router = APIRouter()
settings = get_settings()


def serialize_session(current_session: UserSession) -> SessionResponse:
    return SessionResponse(
        user_id=current_session.user.id,
        email=current_session.user.email,
        full_name=current_session.user.full_name,
        tenant=TenantSummary(
            id=current_session.tenant.id,
            slug=current_session.tenant.slug,
            name=current_session.tenant.name,
            role=current_session.role,
        ),
        expires_at=current_session.expires_at,
    )


@router.post("/login", response_model=SessionResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> SessionResponse:
    auth_result = authenticate_user(db, payload.email, payload.password)
    if auth_result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais invalidas.",
        )

    user, membership = auth_result
    current_session, raw_token = create_session(db, user=user, membership=membership)

    response.set_cookie(
        key=settings.auth_cookie_name,
        value=raw_token,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,
        domain=settings.auth_cookie_domain,
        max_age=settings.session_ttl_hours * 3600,
        expires=settings.session_ttl_hours * 3600,
        path="/",
    )

    return serialize_session(current_session)


@router.get("/me", response_model=SessionResponse)
def me(current_session: UserSession = Depends(get_current_session), db: Session = Depends(get_db)) -> SessionResponse:
    current_session.last_seen_at = datetime.now(timezone.utc)
    db.add(current_session)
    db.commit()
    db.refresh(current_session)
    return serialize_session(current_session)


@router.post("/logout")
def logout(
    response: Response,
    current_session: UserSession = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> dict[str, bool]:
    revoke_session(db, current_session)
    response.delete_cookie(
        key=settings.auth_cookie_name,
        domain=settings.auth_cookie_domain,
        path="/",
    )
    return {"ok": True}
