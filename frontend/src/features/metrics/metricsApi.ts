import { apiRequest } from "../../lib/apiClient";

export type ToolCallStat = {
  name: string;
  count: number;
};

export type TodayMetrics = {
  leads_today: number;
  leads_total: number;
  conversations_active: number;
  messages_inbound_today: number;
  messages_outbound_today: number;
  classification_distribution: Record<string, number>;
  tool_calls_today: ToolCallStat[];
  last_inbound_at: string | null;
  generated_at: string;
};

export function getTodayMetrics() {
  return apiRequest<TodayMetrics>("/metrics/today");
}
