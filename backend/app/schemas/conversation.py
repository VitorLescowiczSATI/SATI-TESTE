from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel


class ConsoleLead(BaseModel):
    id: str
    name: str | None
    phone: str
    status: str
    classification: str | None
    classification_reason: str | None = None
    source_campaign: str | None


class ConsoleLeadProfile(BaseModel):
    proof_of_income_type: str | None = None
    uses_fgts: bool | None = None
    family_income: float | None = None
    employment_history_months: int | None = None
    marital_status: str | None = None
    birth_date: date | None = None
    dependents_summary: str | None = None
    interest_project: str | None = None
    interest_region: str | None = None
    schedule_date_raw: str | None = None
    schedule_time_raw: str | None = None
    scheduled_at: datetime | None = None


class ConsoleConversationSummary(BaseModel):
    id: str
    lead: ConsoleLead
    runtime_state: str
    status: str
    last_message_direction: str | None
    last_message_preview: str | None
    message_count: int
    updated_at: datetime


class ConsoleMessage(BaseModel):
    id: str
    direction: str
    message_type: str
    content_text: str | None
    sent_by_ai: bool
    tool_name: str | None
    tool_payload: dict[str, Any] | None = None
    tool_result_text: str | None = None
    delivery_status: str | None
    created_at: datetime


class ConsoleConversationDetail(ConsoleConversationSummary):
    messages: list[ConsoleMessage]
    summary_text: str | None = None
    classified_at: datetime | None = None
    lead_profile: ConsoleLeadProfile | None = None


class PlaygroundConversationCreate(BaseModel):
    lead_name: str | None = None


class PlaygroundMessageCreate(BaseModel):
    conversation_id: str
    message: str
