from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.core.security import create_session_token, hash_session_token, verify_password
from app.models.membership import Membership
from app.models.session import UserSession
from app.models.user import User

settings = get_settings()


def authenticate_user(db: Session, email: str, password: str) -> tuple[User, Membership] | None:
    stmt = (
        select(User)
        .options(joinedload(User.memberships).joinedload(Membership.tenant))
        .where(User.email == email.lower().strip(), User.status == "active")
    )
    user = db.scalar(stmt)
    if user is None or not verify_password(password, user.password_hash):
        return None

    membership = next(
        (
            item
            for item in sorted(user.memberships, key=lambda current: current.is_default, reverse=True)
            if item.status == "active"
        ),
        None,
    )
    if membership is None:
        return None

    return user, membership


def create_session(db: Session, user: User, membership: Membership) -> tuple[UserSession, str]:
    raw_token = create_session_token()
    now = datetime.now(timezone.utc)
    current_session = UserSession(
        user_id=user.id,
        tenant_id=membership.tenant_id,
        role=membership.role,
        token_hash=hash_session_token(raw_token),
        expires_at=now + timedelta(hours=settings.session_ttl_hours),
        last_seen_at=now,
    )
    db.add(current_session)
    db.commit()
    db.refresh(current_session)
    return current_session, raw_token


def revoke_session(db: Session, current_session: UserSession) -> None:
    current_session.revoked_at = datetime.now(timezone.utc)
    db.add(current_session)
    db.commit()
