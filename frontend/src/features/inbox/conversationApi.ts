import { apiRequest, apiUpload } from "../../lib/apiClient";

export type ConsoleLead = {
  id: string;
  name: string | null;
  phone: string;
  status: string;
  classification: string | null;
  classification_reason: string | null;
  source_campaign: string | null;
};

export type ConsoleLeadProfile = {
  proof_of_income_type: string | null;
  uses_fgts: boolean | null;
  family_income: number | null;
  employment_history_months: number | null;
  marital_status: string | null;
  birth_date: string | null;
  dependents_summary: string | null;
  interest_project: string | null;
  interest_region: string | null;
  schedule_date_raw: string | null;
  schedule_time_raw: string | null;
  scheduled_at: string | null;
};

export type ConsoleConversationSummary = {
  id: string;
  lead: ConsoleLead;
  runtime_state: string;
  status: string;
  last_message_direction: string | null;
  last_message_preview: string | null;
  message_count: number;
  updated_at: string;
};

export type ConsoleMessage = {
  id: string;
  direction: string;
  message_type: string;
  content_text: string | null;
  sent_by_ai: boolean;
  tool_name: string | null;
  tool_payload: Record<string, unknown> | null;
  tool_result_text: string | null;
  delivery_status: string | null;
  created_at: string;
};

export type ConsoleConversationDetail = ConsoleConversationSummary & {
  messages: ConsoleMessage[];
  summary_text: string | null;
  classified_at: string | null;
  lead_profile: ConsoleLeadProfile | null;
};

export function listActiveConversations() {
  return apiRequest<ConsoleConversationSummary[]>("/conversations/active");
}

export function getConversationDetail(conversationId: string) {
  return apiRequest<ConsoleConversationDetail>(`/conversations/${conversationId}`);
}

export function createPlaygroundConversation(leadName?: string) {
  return apiRequest<ConsoleConversationDetail>("/playground/conversations", {
    method: "POST",
    body: { lead_name: leadName || "Lead de Teste" },
  });
}

export function sendPlaygroundMessage(conversationId: string, message: string) {
  return apiRequest<ConsoleConversationDetail>("/playground/messages", {
    method: "POST",
    body: {
      conversation_id: conversationId,
      message,
    },
  });
}

export function sendPlaygroundAudio(conversationId: string, file: File) {
  const formData = new FormData();
  formData.append("conversation_id", conversationId);
  formData.append("audio", file, file.name || "audio.webm");
  return apiUpload<ConsoleConversationDetail>("/playground/audio", formData);
}
