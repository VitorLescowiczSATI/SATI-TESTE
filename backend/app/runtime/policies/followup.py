from __future__ import annotations

from datetime import timedelta


FOLLOW_UP_SEQUENCE: tuple[tuple[str, timedelta, str], ...] = (
    ("follow_up_15m", timedelta(minutes=15), "Follow Up - 15min"),
    ("follow_up_1h", timedelta(hours=1), "Follow Up - 1 hora"),
    ("follow_up_22h", timedelta(hours=22), "Follow Up - 22 horas"),
)


def next_follow_up_kind(current_kind: str) -> str | None:
    kinds = [kind for kind, _, _ in FOLLOW_UP_SEQUENCE]
    try:
        current_index = kinds.index(current_kind)
    except ValueError:
        return kinds[0]

    next_index = current_index + 1
    if next_index >= len(kinds):
        return None
    return kinds[next_index]
