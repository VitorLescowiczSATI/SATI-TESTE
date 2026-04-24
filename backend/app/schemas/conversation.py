from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ConsoleLead(BaseModel):
    id: str
    name: str | None
    phone: str
    status: str
    classification: str | None
    source_campaign: str | None


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
    delivery_status: str | None
    created_at: datetime


class ConsoleConversationDetail(ConsoleConversationSummary):
    messages: list[ConsoleMessage]
