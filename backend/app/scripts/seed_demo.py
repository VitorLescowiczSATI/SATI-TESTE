from __future__ import annotations

from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.membership import Membership
from app.models.tenant import Tenant
from app.models.user import User


def main() -> None:
    settings = get_settings()
    if not settings.seed_admin_email or not settings.seed_admin_password:
        print("Seed skipped: SEED_ADMIN_EMAIL or SEED_ADMIN_PASSWORD not configured.")
        return

    email = settings.seed_admin_email.lower().strip()

    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.slug == "tenda-rj"))
        if tenant is None:
            tenant = Tenant(
                slug="tenda-rj",
                name="Tenda RJ",
                operation_type="MCMV",
                city="Rio de Janeiro",
                crm_provider="facilita",
                status="active",
            )
            db.add(tenant)
            db.flush()

        user = db.scalar(select(User).where(User.email == email))
        if user is None:
            user = User(
                email=email,
                full_name=settings.seed_admin_name,
                password_hash=hash_password(settings.seed_admin_password),
                status="active",
            )
            db.add(user)
            db.flush()
        else:
            user.full_name = settings.seed_admin_name
            user.status = "active"

        membership = db.scalar(
            select(Membership).where(
                Membership.user_id == user.id,
                Membership.tenant_id == tenant.id,
            )
        )
        if membership is None:
            membership = Membership(
                user_id=user.id,
                tenant_id=tenant.id,
                role="sati_admin",
                is_default=True,
                status="active",
            )
            db.add(membership)
        else:
            membership.role = "sati_admin"
            membership.is_default = True
            membership.status = "active"

        db.commit()
        print(f"Seed ready: {email} -> {tenant.slug}")


if __name__ == "__main__":
    main()
