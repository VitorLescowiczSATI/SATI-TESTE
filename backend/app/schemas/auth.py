from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TenantSummary(BaseModel):
    id: str
    slug: str
    name: str
    role: str


class SessionResponse(BaseModel):
    user_id: str
    email: EmailStr
    full_name: str
    tenant: TenantSummary
    expires_at: datetime
