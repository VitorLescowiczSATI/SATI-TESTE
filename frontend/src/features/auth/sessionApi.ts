import { apiRequest } from "../../lib/apiClient";
import type { DemoSession } from "../../types";

type SessionResponse = {
  user_id: string;
  email: string;
  full_name: string;
  tenant: {
    id: string;
    slug: string;
    name: string;
    role: string;
  };
  expires_at: string;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export async function login(payload: LoginPayload) {
  const session = await apiRequest<SessionResponse>("/auth/login", {
    method: "POST",
    body: payload,
  });
  return mapSession(session);
}

export async function loadCurrentSession() {
  const session = await apiRequest<SessionResponse>("/auth/me");
  return mapSession(session);
}

export async function logout() {
  await apiRequest<{ ok: boolean }>("/auth/logout", {
    method: "POST",
  });
}

function mapSession(session: SessionResponse): DemoSession {
  return {
    userId: session.user_id,
    fullName: session.full_name,
    email: session.email,
    tenantId: session.tenant.id,
    tenantSlug: session.tenant.slug,
    tenantName: session.tenant.name,
    role: session.tenant.role,
    expiresAt: session.expires_at,
  };
}
