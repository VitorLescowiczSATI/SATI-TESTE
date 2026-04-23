from __future__ import annotations

from datetime import datetime, timezone

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.core.security import hash_session_token
from app.db.session import get_db
from app.models.session import UserSession

settings = get_settings()


def get_current_session(
    db: Session = Depends(get_db),
    session_token: str | None = Cookie(default=None, alias=settings.auth_cookie_name),
) -> UserSession:
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessao nao encontrada.",
        )

    token_hash = hash_session_token(session_token)
    stmt = (
        select(UserSession)
        .options(joinedload(UserSession.user), joinedload(UserSession.tenant))
        .where(
            UserSession.token_hash == token_hash,
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > datetime.now(timezone.utc),
        )
    )
    current_session = db.scalar(stmt)

    if current_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessao invalida ou expirada.",
        )

    return current_session
