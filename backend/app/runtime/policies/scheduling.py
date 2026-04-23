from __future__ import annotations

from datetime import UTC, datetime, timedelta, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def get_default_timezone() -> tzinfo:
    try:
        return ZoneInfo("America/Sao_Paulo")
    except ZoneInfoNotFoundError:
        return UTC


def normalize_schedule_datetime(date_text: str, time_text: str, tz: tzinfo | None = None) -> datetime:
    timezone = tz or get_default_timezone()
    scheduled_at = datetime.strptime(f"{date_text} {time_text}", "%d/%m/%Y %H:%M").replace(tzinfo=timezone)
    minimum_allowed = datetime.now(timezone) + timedelta(hours=1)
    if scheduled_at < minimum_allowed:
        raise ValueError("scheduled time must be at least one hour in the future")
    return scheduled_at


def can_offer_schedule(profile: dict[str, object | None]) -> bool:
    return all(profile.get(field) not in (None, "") for field in ("proof_of_income_type", "uses_fgts", "family_income"))
