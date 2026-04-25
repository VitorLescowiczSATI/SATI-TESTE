import { apiRequest } from "../../lib/apiClient";
import type { ConsoleConversationDetail } from "../inbox/conversationApi";

export type AdminRuntimeTool = {
  id: string;
  key: string;
  name: string;
  description: string | null;
  is_enabled: boolean;
  is_core: boolean;
};

export type AdminKnowledgeProject = {
  id: string;
  slug: string;
  name: string;
  region: string;
  city_neighborhood: string | null;
  status: string | null;
  min_income: number | null;
  typology: string | null;
  highlights: unknown[];
  is_active: boolean;
};

export type AdminRuntimeConfig = {
  id: string;
  key: string;
  name: string;
  version: string;
  status: string;
  channel_mode: string;
  notes: string | null;
  agent: {
    id: string;
    key: string;
    name: string;
    description: string | null;
    model: string;
    max_tokens: number;
    temperature: number;
    status: string;
    system_prompt: string;
  };
  tools: AdminRuntimeTool[];
  projects: AdminKnowledgeProject[];
};

export type AdminLeadSummary = {
  id: string;
  name: string | null;
  phone: string;
  status: string;
  classification: string | null;
  classification_reason: string | null;
  source_channel: string;
  source_campaign: string | null;
  conversation_count: number;
  message_count: number;
  updated_at: string;
};

export type AdminLeadDetail = AdminLeadSummary & {
  profile: Record<string, unknown> | null;
  latest_conversation: ConsoleConversationDetail | null;
  facilita_payload_preview: Record<string, unknown> | null;
};

export type RuntimeConfigPatch = {
  model?: string;
  max_tokens?: number;
  temperature?: number;
  system_prompt?: string;
  enabled_tools?: Record<string, boolean>;
};

export function getAdminRuntimeConfig() {
  return apiRequest<AdminRuntimeConfig>("/admin/runtime-config");
}

export function updateAdminRuntimeConfig(payload: RuntimeConfigPatch) {
  return apiRequest<AdminRuntimeConfig>("/admin/runtime-config", {
    method: "PATCH",
    body: payload,
  });
}

export function listAdminLeads() {
  return apiRequest<AdminLeadSummary[]>("/admin/leads");
}

export function getAdminLeadDetail(leadId: string) {
  return apiRequest<AdminLeadDetail>(`/admin/leads/${leadId}`);
}

export function refreshAdminLeadAnalysis(leadId: string) {
  return apiRequest<AdminLeadDetail>(`/admin/leads/${leadId}/refresh-analysis`, {
    method: "POST",
  });
}

export function deleteAdminLead(leadId: string) {
  return apiRequest<void>(`/admin/leads/${leadId}`, {
    method: "DELETE",
  });
}
