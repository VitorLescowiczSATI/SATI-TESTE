import type { ReactNode } from "react";

export type RuntimeTabKey = "geral" | "states" | "policies" | "crm" | "preview";
export type AppViewKey = "dashboard" | "inbox" | "leads" | "runtime" | "settings";

export interface DemoSession {
  fullName: string;
  email: string;
  tenantName: string;
  role: string;
}

export interface TenantConfig {
  id: string;
  tenantName: string;
  city: string;
  operationType: string;
  template: string;
  strategy: string;
  runtimeStatus: string;
  greetingStyle: string;
  qualificationDepth: string;
  humanPause: boolean;
  dashboardAfterValidation: boolean;
  audioEnabled: boolean;
  autoSummary: boolean;
  firstFollowupMinutes: number;
  secondFollowupMinutes: number;
  maxAttempts: number;
  maxParcelPercent: number;
  hotThreshold: number;
  crmProvider: string;
  crmStage: string;
  mediaPack: string;
  lastPublished: string;
  owner: string;
  requiredFields: Record<string, boolean>;
  actions: Record<string, boolean>;
  fieldMappings: Record<string, string>;
}

export interface EngineCore {
  engineVersion: string;
  stateMachineVersion: string;
  queueModel: string;
  actionsCatalog: string[];
  guardrails: string[];
}

export interface StateMeta {
  key: string;
  title: string;
  goal: string;
  configurable: string[];
  protected: string[];
}

export interface TransitionMeta {
  next: string;
  strategy: string;
  policies: string[];
  actions: string[];
  explanation: string;
}

export type TransitionMap = Record<string, Record<string, TransitionMeta>>;
export type EventMap = Record<string, string[]>;

export interface TabDefinition {
  key: RuntimeTabKey;
  label: string;
}

export interface SectionBadge {
  label: string;
  className?: string;
}

export interface SectionCardProps {
  title: string;
  subtitle?: string;
  badge?: SectionBadge;
  actions?: ReactNode;
  children: ReactNode;
}
