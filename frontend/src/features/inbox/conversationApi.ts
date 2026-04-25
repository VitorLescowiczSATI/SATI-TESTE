import { apiRequest } from "../../lib/apiClient";

export type ConsoleLead = {
  id: string;
  name: string | null;
  phone: string;
  status: string;
  classification: string | null;
  source_campaign: string | null;
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
  delivery_status: string | null;
  created_at: string;
};

export type ConsoleConversationDetail = ConsoleConversationSummary & {
  messages: ConsoleMessage[];
  summary_text: string | null;
  classified_at: string | null;
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
