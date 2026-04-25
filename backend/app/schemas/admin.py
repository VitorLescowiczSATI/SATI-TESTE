from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.conversation import ConsoleConversationDetail


class AdminRuntimeAgent(BaseModel):
    id: str
    key: str
    name: str
    description: str | None
    model: str
    max_tokens: int
    temperature: float
    status: str
    system_prompt: str


class AdminRuntimeTool(BaseModel):
    id: str
    key: str
    name: str
    description: str | None
    is_enabled: bool
    is_core: bool


class AdminKnowledgeProject(BaseModel):
    id: str
    slug: str
    name: str
    region: str
    city_neighborhood: str | None
    status: str | None
    min_income: float | None
    typology: str | None
    highlights: list[Any]
    is_active: bool


class AdminRuntimeConfig(BaseModel):
    id: str
    key: str
    name: str
    version: str
    status: str
    channel_mode: str
    notes: str | None
    agent: AdminRuntimeAgent
    tools: list[AdminRuntimeTool]
    projects: list[AdminKnowledgeProject]


class AdminRuntimeConfigUpdate(BaseModel):
    model: str | None = Field(default=None, min_length=2, max_length=80)
    max_tokens: int | None = Field(default=None, ge=100, le=4000)
    temperature: float | None = Field(default=None, ge=0, le=2)
    system_prompt: str | None = Field(default=None, min_length=50)
    enabled_tools: dict[str, bool] | None = None


class AdminLeadProfile(BaseModel):
    proof_of_income_type: str | None
    uses_fgts: bool | None
    family_income: float | None
    entry_amount: float | None
    has_property: bool | None
    employment_history_months: int | None
    marital_status: str | None
    birth_date: str | None
    dependents_summary: str | None
    interest_project: str | None
    interest_region: str | None
    scheduled_at: str | None


class AdminLeadSummary(BaseModel):
    id: str
    name: str | None
    phone: str
    status: str
    classification: str | None
    classification_reason: str | None
    source_channel: str
    source_campaign: str | None
    conversation_count: int
    message_count: int
    updated_at: datetime


class AdminLeadDetail(AdminLeadSummary):
    profile: AdminLeadProfile | None
    latest_conversation: ConsoleConversationDetail | None
    facilita_payload_preview: dict[str, Any] | None
