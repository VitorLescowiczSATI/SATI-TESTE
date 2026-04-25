import { useEffect, useMemo, useState } from "react";
import { Icon } from "../components/Icons";
import { RuntimeCard } from "../components/RuntimeCard";
import { SectionCard } from "../components/SectionCard";
import {
  deleteAdminLead,
  getAdminLeadDetail,
  getAdminRuntimeConfig,
  listAdminLeads,
  refreshAdminLeadAnalysis,
  updateAdminRuntimeConfig,
  type AdminLeadDetail,
  type AdminLeadSummary,
  type AdminRuntimeConfig,
} from "../features/admin/adminApi";

export function AdminPage() {
  const [config, setConfig] = useState<AdminRuntimeConfig | null>(null);
  const [leads, setLeads] = useState<AdminLeadSummary[]>([]);
  const [selectedLeadId, setSelectedLeadId] = useState<string | null>(null);
  const [selectedLead, setSelectedLead] = useState<AdminLeadDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [draftPrompt, setDraftPrompt] = useState("");
  const [draftModel, setDraftModel] = useState("gpt-4.1-mini");
  const [draftMaxTokens, setDraftMaxTokens] = useState(700);
  const [draftTools, setDraftTools] = useState<Record<string, boolean>>({});

  useEffect(() => {
    void loadAdmin();
  }, []);

  useEffect(() => {
    if (!selectedLeadId) {
      setSelectedLead(null);
      return;
    }
    void loadLead(selectedLeadId);
  }, [selectedLeadId]);

  async function loadAdmin() {
    setLoading(true);
    setError("");
    try {
      const [nextConfig, nextLeads] = await Promise.all([
        getAdminRuntimeConfig(),
        listAdminLeads(),
      ]);
      setConfig(nextConfig);
      setLeads(nextLeads);
      setDraftPrompt(nextConfig.agent.system_prompt);
      setDraftModel(nextConfig.agent.model);
      setDraftMaxTokens(nextConfig.agent.max_tokens);
      setDraftTools(Object.fromEntries(nextConfig.tools.map((tool) => [tool.key, tool.is_enabled])));
      setSelectedLeadId((current) => current ?? nextLeads[0]?.id ?? null);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Nao foi possivel carregar o admin.");
    } finally {
      setLoading(false);
    }
  }

  async function loadLead(leadId: string) {
    setError("");
    try {
      const detail = await getAdminLeadDetail(leadId);
      setSelectedLead(detail);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Nao foi possivel carregar o lead.");
    }
  }

  async function saveRuntimeConfig() {
    setSaving(true);
    setError("");
    try {
      const nextConfig = await updateAdminRuntimeConfig({
        model: draftModel,
        max_tokens: draftMaxTokens,
        system_prompt: draftPrompt,
        enabled_tools: draftTools,
      });
      setConfig(nextConfig);
      setDraftTools(Object.fromEntries(nextConfig.tools.map((tool) => [tool.key, tool.is_enabled])));
    } catch (error) {
      setError(error instanceof Error ? error.message : "Nao foi possivel salvar a configuracao.");
    } finally {
      setSaving(false);
    }
  }

  async function refreshAnalysis() {
    if (!selectedLeadId) return;
    setSaving(true);
    setError("");
    try {
      const detail = await refreshAdminLeadAnalysis(selectedLeadId);
      setSelectedLead(detail);
      setLeads(await listAdminLeads());
    } catch (error) {
      setError(error instanceof Error ? error.message : "Nao foi possivel atualizar a analise.");
    } finally {
      setSaving(false);
    }
  }

  async function deleteLead() {
    if (!selectedLeadId) return;
    const confirmed = window.confirm("Excluir este lead de teste e todas as conversas dele?");
    if (!confirmed) return;

    setSaving(true);
    setError("");
    try {
      await deleteAdminLead(selectedLeadId);
      const nextLeads = await listAdminLeads();
      setLeads(nextLeads);
      setSelectedLeadId(nextLeads[0]?.id ?? null);
      setSelectedLead(null);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Nao foi possivel excluir o lead.");
    } finally {
      setSaving(false);
    }
  }

  const metrics = useMemo(() => {
    return {
      leads: leads.length,
      hot: leads.filter((lead) => lead.classification === "quente").length,
      scheduled: leads.filter((lead) => lead.classification === "agendado").length,
      cold: leads.filter((lead) => lead.classification === "frio").length,
    };
  }, [leads]);

  return (
    <>
      {error ? <div className="alert alert--error" style={{ marginBottom: 18 }}>{error}</div> : null}

      <div className="top-summary">
        <RuntimeCard label="Leads no workspace" value={loading ? "..." : String(metrics.leads)} note="Somente dados reais do banco" />
        <RuntimeCard label="Quentes" value={loading ? "..." : String(metrics.hot)} note="Sinais de compra/simulacao" />
        <RuntimeCard label="Agendados" value={loading ? "..." : String(metrics.scheduled)} note="Pedido ou registro de visita" />
        <RuntimeCard label="Frios" value={loading ? "..." : String(metrics.cold)} note="Ainda sem dado comercial" />
      </div>

      <div className="dashboard-grid" style={{ alignItems: "start" }}>
        <SectionCard
          title="Configuracao publicada"
          subtitle="Primeira central admin da plataforma: workspace, agente, tools e catalogo."
          badge={{ label: config?.status ?? "carregando", className: "badge--brand" }}
          actions={
            <button className="btn btn--primary btn--sm" onClick={() => void saveRuntimeConfig()} disabled={saving || !config}>
              <Icon.check /> {saving ? "Salvando..." : "Salvar config"}
            </button>
          }
        >
          {!config ? (
            <div className="card card--padded">Carregando configuracao...</div>
          ) : (
            <div style={{ display: "grid", gap: 16 }}>
              <div className="g g-3">
                <div className="field">
                  <label className="field-label">Runtime</label>
                  <input className="input" value={`${config.name} (${config.version})`} readOnly />
                </div>
                <div className="field">
                  <label className="field-label">Modelo GPT</label>
                  <input className="input" value={draftModel} onChange={(event) => setDraftModel(event.target.value)} />
                </div>
                <div className="field">
                  <label className="field-label">Max tokens</label>
                  <input
                    className="input"
                    type="number"
                    min={100}
                    max={4000}
                    value={draftMaxTokens}
                    onChange={(event) => setDraftMaxTokens(Number(event.target.value))}
                  />
                </div>
              </div>

              <div className="field">
                <label className="field-label">Prompt principal da Maju</label>
                <textarea
                  className="textarea"
                  style={{ minHeight: 260, fontFamily: "var(--font-mono)", fontSize: 12 }}
                  value={draftPrompt}
                  onChange={(event) => setDraftPrompt(event.target.value)}
                />
                <span className="field-hint">No proximo passo isso vira versao draft/publicada com historico.</span>
              </div>

              <div>
                <div className="section-subtitle" style={{ marginBottom: 10 }}>Tools habilitadas</div>
                <div className="g g-2">
                  {config.tools.map((tool) => (
                    <label key={tool.key} className="card card--flat" style={{ display: "flex", gap: 10, alignItems: "center" }}>
                      <span
                        className={`switch ${draftTools[tool.key] ? "on" : ""}`}
                        onClick={() => setDraftTools((current) => ({ ...current, [tool.key]: !current[tool.key] }))}
                      />
                      <span>
                        <strong>{tool.name}</strong>
                        <p className="caption" style={{ margin: "4px 0 0" }}>{tool.description}</p>
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <div className="section-subtitle" style={{ marginBottom: 10 }}>Catalogo TendaRJ carregado</div>
                <div className="table-wrap">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Empreendimento</th>
                        <th>Regiao</th>
                        <th>Renda min.</th>
                      </tr>
                    </thead>
                    <tbody>
                      {config.projects.slice(0, 8).map((project) => (
                        <tr key={project.id}>
                          <td className="name-cell">{project.name}</td>
                          <td>{project.region}</td>
                          <td>{project.min_income ? formatCurrency(project.min_income) : "N/I"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </SectionCard>

        <SectionCard
          title="Leads e payload Facilita"
          subtitle="Apague testes, revise classificacao e veja o que seria enviado para o CRM."
          badge={{ label: "Admin", className: "badge--outline" }}
          actions={
            <button className="btn btn--secondary btn--sm" onClick={() => void loadAdmin()} disabled={loading}>
              <Icon.inbox /> Atualizar
            </button>
          }
        >
          <div className="inbox-layout" style={{ gridTemplateColumns: "minmax(240px, .8fr) minmax(0, 1.2fr)" }}>
            <div className="conversation-list">
              {leads.length === 0 ? (
                <div className="card card--padded">
                  <strong>Nenhum lead ainda</strong>
                  <p className="caption" style={{ marginTop: 8 }}>Crie um lead no Playground para ele aparecer aqui.</p>
                </div>
              ) : null}

              {leads.map((lead) => (
                <button
                  key={lead.id}
                  type="button"
                  className={`conversation-item ${lead.id === selectedLeadId ? "active" : ""}`}
                  onClick={() => setSelectedLeadId(lead.id)}
                >
                  <div className="conversation-item-head">
                    <strong>{lead.name || lead.phone}</strong>
                    <span className={`badge ${classificationBadge(lead.classification)}`}>
                      {labelClassification(lead.classification)}
                    </span>
                  </div>
                  <p>{lead.classification_reason || "Ainda sem classificacao calculada."}</p>
                  <span>{lead.message_count} msg - {formatDateTime(lead.updated_at)}</span>
                </button>
              ))}
            </div>

            <div style={{ display: "grid", gap: 14 }}>
              {!selectedLead ? (
                <div className="card card--padded">
                  <strong>Selecione um lead</strong>
                  <p className="caption" style={{ marginTop: 8 }}>Aqui aparece o resumo, perfil e preview Facilita.</p>
                </div>
              ) : (
                <>
                  <div className="card card--padded">
                    <div className="section-title" style={{ marginBottom: 12 }}>
                      <div>
                        <h3 style={{ margin: 0 }}>{selectedLead.name || selectedLead.phone}</h3>
                        <div className="section-subtitle">{selectedLead.phone}</div>
                      </div>
                      <span className={`badge ${classificationBadge(selectedLead.classification)}`}>
                        {labelClassification(selectedLead.classification)}
                      </span>
                    </div>
                    <p style={{ marginTop: 0 }}>{selectedLead.classification_reason || "Sem motivo ainda."}</p>
                    <div className="divider" style={{ margin: "14px 0" }} />
                    <strong>Resumo</strong>
                    <p className="caption" style={{ whiteSpace: "normal", lineHeight: 1.6 }}>
                      {selectedLead.latest_conversation?.summary_text ||
                        String(selectedLead.facilita_payload_preview?.resumo_atendimento || "") ||
                        "Resumo ainda nao gerado."}
                    </p>
                    <div style={{ display: "flex", gap: 8, marginTop: 14, flexWrap: "wrap" }}>
                      <button className="btn btn--secondary btn--sm" onClick={() => void refreshAnalysis()} disabled={saving}>
                        <Icon.spark /> Recalcular analise
                      </button>
                      <button className="btn btn--danger btn--sm" onClick={() => void deleteLead()} disabled={saving}>
                        Excluir lead
                      </button>
                    </div>
                  </div>

                  <div className="card card--padded">
                    <strong>Perfil estruturado</strong>
                    <pre className="json-preview">{JSON.stringify(selectedLead.profile || {}, null, 2)}</pre>
                  </div>

                  <div className="card card--padded">
                    <strong>Preview payload Facilita</strong>
                    <pre className="json-preview">{JSON.stringify(selectedLead.facilita_payload_preview || {}, null, 2)}</pre>
                  </div>
                </>
              )}
            </div>
          </div>
        </SectionCard>
      </div>
    </>
  );
}

function classificationBadge(classification: string | null) {
  if (classification === "agendado") return "badge--sched";
  if (classification === "quente") return "badge--hot";
  if (classification === "frio") return "badge--cold";
  if (classification === "corretor") return "badge--warm";
  return "badge--neutral";
}

function labelClassification(classification: string | null) {
  const labels: Record<string, string> = {
    agendado: "Agendado",
    quente: "Quente",
    frio: "Frio",
    corretor: "Corretor",
  };
  return classification ? labels[classification] || classification : "Sem classe";
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    maximumFractionDigits: 0,
  }).format(value);
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}
