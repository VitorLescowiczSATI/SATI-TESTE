import { useEffect, useMemo, useState } from "react";
import { Icon } from "../components/Icons";
import { SectionCard } from "../components/SectionCard";
import {
  createPlaygroundConversation,
  getConversationDetail,
  listActiveConversations,
  sendPlaygroundMessage,
  type ConsoleConversationDetail,
  type ConsoleConversationSummary,
  type ConsoleLeadProfile,
  type ConsoleMessage,
} from "../features/inbox/conversationApi";

export function PlaygroundPage() {
  const [conversations, setConversations] = useState<ConsoleConversationSummary[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<ConsoleConversationDetail | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [sending, setSending] = useState(false);
  const [draftMessage, setDraftMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    void refreshConversations();
  }, []);

  useEffect(() => {
    if (!selectedId) {
      setSelectedConversation(null);
      return;
    }

    let cancelled = false;
    getConversationDetail(selectedId)
      .then((conversation) => {
        if (!cancelled) setSelectedConversation(conversation);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Nao foi possivel carregar a conversa.");
        }
      });

    return () => {
      cancelled = true;
    };
  }, [selectedId]);

  async function refreshConversations() {
    setLoading(true);
    setError("");
    try {
      const next = await listActiveConversations();
      setConversations(next);
      setSelectedId((current) => current ?? next[0]?.id ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel carregar as conversas.");
    } finally {
      setLoading(false);
    }
  }

  async function createTestLead() {
    setCreating(true);
    setError("");
    try {
      const conversation = await createPlaygroundConversation();
      setSelectedConversation(conversation);
      setSelectedId(conversation.id);
      await refreshConversations();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel criar o lead de teste.");
    } finally {
      setCreating(false);
    }
  }

  async function submitMessage(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = draftMessage.trim();
    if (!message || !selectedId) return;

    setSending(true);
    setError("");
    try {
      setDraftMessage("");
      const conversation = await sendPlaygroundMessage(selectedId, message);
      setSelectedConversation(conversation);
      await refreshConversations();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel enviar a mensagem.");
      setDraftMessage(message);
    } finally {
      setSending(false);
    }
  }

  const toolCalls = useMemo<ConsoleMessage[]>(
    () => (selectedConversation?.messages ?? []).filter((message) => message.tool_name),
    [selectedConversation],
  );

  return (
    <SectionCard
      title="Playground da Maju"
      subtitle="Simule um lead, converse com o GPT e acompanhe perfil + tool calls em tempo real."
      badge={{ label: "GPT + tools", className: "badge--brand" }}
      actions={
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <button className="btn btn--secondary btn--sm" onClick={() => void refreshConversations()} disabled={loading}>
            <Icon.inbox /> Atualizar
          </button>
          <button className="btn btn--primary btn--sm" onClick={() => void createTestLead()} disabled={creating}>
            <Icon.users /> {creating ? "Criando..." : "Novo lead de teste"}
          </button>
        </div>
      }
    >
      {error ? <div className="alert alert--error" style={{ marginBottom: 16 }}>{error}</div> : null}

      <div className="playground-layout">
        <aside className="conversation-list">
          {loading && conversations.length === 0 ? (
            <div className="card card--padded">
              <strong>Carregando conversas...</strong>
            </div>
          ) : null}

          {!loading && conversations.length === 0 ? (
            <div className="card card--padded">
              <strong>Nenhum lead de teste ainda</strong>
              <p className="caption" style={{ marginTop: 8 }}>
                Crie um lead de teste e mande a primeira mensagem para a Maju responder.
              </p>
            </div>
          ) : null}

          {conversations.map((item) => {
            const displayName = item.lead.name || item.lead.phone;
            return (
              <button
                key={item.id}
                type="button"
                className={`conversation-item ${item.id === selectedId ? "active" : ""}`}
                onClick={() => setSelectedId(item.id)}
              >
                <div className="conversation-item-head">
                  <strong>{displayName}</strong>
                  <span className="badge badge--neutral">{humanizeState(item.runtime_state)}</span>
                </div>
                <p>{item.last_message_preview || "Mensagem sem texto."}</p>
                <span>
                  {item.message_count} msg - {formatDateTime(item.updated_at)}
                  {item.lead.classification ? ` - ${item.lead.classification}` : ""}
                </span>
              </button>
            );
          })}
        </aside>

        <section className="card card--padded playground-chat">
          <div className="section-title" style={{ marginBottom: 10 }}>
            <div>
              <h3 style={{ margin: 0 }}>
                {selectedConversation?.lead.name || selectedConversation?.lead.phone || "Conversa"}
              </h3>
              <div className="section-subtitle">
                {selectedConversation
                  ? `${selectedConversation.lead.phone} - ${humanizeState(selectedConversation.runtime_state)}`
                  : "Selecione uma conversa para ver as mensagens."}
              </div>
            </div>
          </div>

          <div className="chat" style={{ minHeight: 360 }}>
            {!selectedConversation ? <div className="bubble system">Crie um lead de teste para comecar</div> : null}

            {selectedConversation?.messages.map((message) => {
              if (message.tool_name) {
                return (
                  <div key={message.id} className="bubble system tool">
                    <span className="tag">tool</span>
                    <strong>{message.tool_name}</strong>
                    <code style={{ display: "block", marginTop: 6, fontSize: 12 }}>
                      {JSON.stringify(message.tool_payload ?? {}, null, 2)}
                    </code>
                    {message.tool_result_text ? (
                      <p style={{ margin: "6px 0 0", fontSize: 12, opacity: 0.8 }}>
                        {message.tool_result_text}
                      </p>
                    ) : null}
                    <span className="time">{formatTime(message.created_at)}</span>
                  </div>
                );
              }
              return (
                <div
                  key={message.id}
                  className={`bubble ${message.sent_by_ai ? "ai" : message.direction === "inbound" ? "in" : "out"}`}
                >
                  {message.sent_by_ai ? <span className="tag">SATI</span> : null}
                  {message.content_text || labelMessageType(message.message_type)}
                  <span className="time">{formatTime(message.created_at)}</span>
                </div>
              );
            })}
          </div>

          <form onSubmit={submitMessage} style={{ display: "flex", gap: 10, marginTop: 14 }}>
            <input
              className="input"
              value={draftMessage}
              onChange={(event) => setDraftMessage(event.target.value)}
              placeholder={
                selectedConversation
                  ? "Digite como se voce fosse o lead..."
                  : "Crie um lead de teste para comecar"
              }
              disabled={!selectedConversation || sending}
            />
            <button
              type="submit"
              className="btn btn--primary"
              disabled={!selectedConversation || sending || !draftMessage.trim()}
            >
              {sending ? "Enviando..." : "Enviar"}
            </button>
          </form>
        </section>

        <aside className="card card--padded playground-side">
          <h3 style={{ margin: "0 0 12px" }}>Painel da Maju</h3>

          <div style={{ marginBottom: 18 }}>
            <div className="section-subtitle" style={{ marginBottom: 6 }}>Classificacao</div>
            {selectedConversation ? (
              <>
                <span className={`badge ${classificationBadge(selectedConversation.lead.classification)}`}>
                  {selectedConversation.lead.classification ?? "sem classificacao"}
                </span>
                {selectedConversation.lead.classification_reason ? (
                  <p className="caption" style={{ marginTop: 8 }}>{selectedConversation.lead.classification_reason}</p>
                ) : null}
              </>
            ) : (
              <p className="caption">Aguardando conversa.</p>
            )}
          </div>

          <div style={{ marginBottom: 18 }}>
            <div className="section-subtitle" style={{ marginBottom: 6 }}>Perfil coletado</div>
            <ProfileList profile={selectedConversation?.lead_profile ?? null} />
          </div>

          <div>
            <div className="section-subtitle" style={{ marginBottom: 6 }}>
              Function calls disparadas ({toolCalls.length})
            </div>
            {toolCalls.length === 0 ? (
              <p className="caption">Nenhuma tool acionada ainda.</p>
            ) : (
              <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 10 }}>
                {toolCalls.map((call) => (
                  <li key={call.id} className="card card--flat" style={{ padding: 10 }}>
                    <strong>{call.tool_name}</strong>
                    <span className="caption" style={{ display: "block", marginTop: 2 }}>
                      {formatTime(call.created_at)}
                    </span>
                    <code style={{ display: "block", marginTop: 6, fontSize: 11, whiteSpace: "pre-wrap" }}>
                      {JSON.stringify(call.tool_payload ?? {}, null, 2)}
                    </code>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {selectedConversation?.summary_text ? (
            <div style={{ marginTop: 18 }}>
              <div className="section-subtitle" style={{ marginBottom: 6 }}>Resumo</div>
              <p className="caption">{selectedConversation.summary_text}</p>
            </div>
          ) : null}
        </aside>
      </div>
    </SectionCard>
  );
}

function ProfileList({ profile }: { profile: ConsoleLeadProfile | null }) {
  if (!profile) return <p className="caption">Sem perfil ainda.</p>;
  const rows: Array<[string, string | null]> = [
    ["Comprovacao renda", profile.proof_of_income_type],
    ["Usa FGTS", profile.uses_fgts === null ? null : profile.uses_fgts ? "sim" : "nao"],
    ["Renda familiar", profile.family_income !== null ? `R$ ${profile.family_income.toLocaleString("pt-BR")}` : null],
    ["Tempo carteira", profile.employment_history_months !== null ? `${profile.employment_history_months} meses` : null],
    ["Estado civil", profile.marital_status],
    ["Nascimento", profile.birth_date],
    ["Dependentes", profile.dependents_summary],
    ["Empreendimento", profile.interest_project],
    ["Regiao", profile.interest_region],
    ["Agendamento", profile.scheduled_at ? formatDateTime(profile.scheduled_at) : null],
  ];
  const filled = rows.filter(([, value]) => value !== null && value !== "");
  if (filled.length === 0) return <p className="caption">Sem dados estruturados ainda.</p>;
  return (
    <dl style={{ margin: 0, display: "grid", gridTemplateColumns: "1fr 1fr", gap: "6px 12px", fontSize: 13 }}>
      {filled.map(([label, value]) => (
        <div key={label}>
          <dt className="caption" style={{ margin: 0 }}>{label}</dt>
          <dd style={{ margin: 0, fontWeight: 500 }}>{value}</dd>
        </div>
      ))}
    </dl>
  );
}

function humanizeState(state: string) {
  const labels: Record<string, string> = {
    novo: "novo",
    em_atendimento: "em atendimento",
    aguardando_dados: "aguardando dados",
    aguardando_resposta: "aguardando resposta",
    handoff_humano: "humano",
  };
  return labels[state] || state.replace(/_/g, " ");
}

function classificationBadge(classification: string | null) {
  if (classification === "agendado") return "badge--success";
  if (classification === "quente") return "badge--brand";
  if (classification === "corretor") return "badge--outline";
  return "badge--neutral";
}

function labelMessageType(type: string) {
  return `[${type}] Mensagem recebida sem texto visivel.`;
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}
