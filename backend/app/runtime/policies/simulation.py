from __future__ import annotations

from collections.abc import Mapping


def missing_initial_simulation_fields(profile: Mapping[str, object | None]) -> list[str]:
    required_fields = ("proof_of_income_type", "uses_fgts", "family_income")
    return [field for field in required_fields if profile.get(field) in (None, "")]


def missing_full_simulation_fields(profile: Mapping[str, object | None]) -> list[str]:
    required_fields = (
        "employment_history_months",
        "marital_status",
        "birth_date",
    )
    return [field for field in required_fields if profile.get(field) in (None, "")]
