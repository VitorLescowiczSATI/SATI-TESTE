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

    const previousIds = new Set((selectedConversation?.messages ?? []).map((m) => m.id));
    setSending(true);
    setError("");
    try {
      setDraftMessage("");
      const conversation = await sendPlaygroundMessage(selectedId, message);
      await revealConversationProgressively(conversation, previousIds, setSelectedConversation);
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
        <aside className="playground-list">
          <div className="playground-section-label">Conversas ({conversations.length})</div>

          {loading && conversations.length === 0 ? (
            <p className="side-empty">Carregando conversas...</p>
          ) : null}

          {!loading && conversations.length === 0 ? (
            <p className="side-empty">
              Nenhum lead ainda. Clique em "Novo lead de teste" pra comecar.
            </p>
          ) : null}

          {conversations.map((item) => {
            const displayName = item.lead.name || formatPhone(item.lead.phone);
            const classification = item.lead.classification;
            return (
              <button
                key={item.id}
                type="button"
                className={`conv-card ${item.id === selectedId ? "is-active" : ""}`}
                onClick={() => setSelectedId(item.id)}
              >
                <div className="conv-card-top">
                  <span className="conv-card-name">{displayName}</span>
                  <span className="badge-state">{humanizeState(item.runtime_state)}</span>
                </div>
                <p className="conv-card-preview">
                  {item.last_message_preview || "Sem texto visivel ainda."}
                </p>
                <div className="conv-card-meta">
                  <span>{item.message_count} msg</span>
                  <span className="conv-card-meta-dot" />
                  <span>{formatDateTime(item.updated_at)}</span>
                  {classification ? (
                    <>
                      <span className="conv-card-meta-dot" />
                      <span className={`badge-class ${classificationBadgeClass(classification)}`}>
                        {classification}
                      </span>
                    </>
                  ) : null}
                </div>
              </button>
            );
          })}
        </aside>

        <section className="playground-chat">
          {selectedConversation ? (
            <header className="chat-header">
              <div className="chat-avatar">{initialsOf(selectedConversation.lead.name || selectedConversation.lead.phone)}</div>
              <div className="chat-header-info">
                <span className="chat-header-name">
                  {selectedConversation.lead.name || formatPhone(selectedConversation.lead.phone)}
                </span>
                <span className="chat-header-meta">
                  {formatPhone(selectedConversation.lead.phone)} - {humanizeState(selectedConversation.runtime_state)}
                </span>
              </div>
            </header>
          ) : null}

          {selectedConversation ? (
            <div className="chat">
              {selectedConversation.messages.length === 0 ? (
                <div className="bubble system">Sem mensagens ainda. Mande a primeira pra Maju responder.</div>
              ) : null}
              {selectedConversation.messages.map((message) => {
                if (message.tool_name) {
                  return (
                    <div key={message.id} className="bubble tool">
                      <span className="tag">tool</span>
                      <strong>{message.tool_name}</strong>
                      <code>{JSON.stringify(message.tool_payload ?? {}, null, 2)}</code>
                      {message.tool_result_text ? (
                        <p style={{ margin: "var(--sp-2) 0 0", fontSize: "var(--fs-xs)", opacity: 0.7 }}>
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
                    {message.sent_by_ai ? <span className="tag">Maju</span> : null}
                    {message.content_text || labelMessageType(message.message_type)}
                    <span className="time">{formatTime(message.created_at)}</span>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="chat-empty">
              <Icon.spark />
              <strong>Selecione uma conversa</strong>
              <p>Crie um novo lead de teste ou escolha um da lista pra comecar a interagir com a Maju.</p>
            </div>
          )}

          <form onSubmit={submitMessage} className="chat-composer">
            <input
              className="input"
              value={draftMessage}
              onChange={(event) => setDraftMessage(event.target.value)}
              placeholder={
                selectedConversation
                  ? "Digite como se voce fosse o lead..."
                  : "Crie um lead de teste pra comecar"
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

        <aside className="playground-side">
          <div className="playground-section-label">Painel da Maju</div>

          <div className="side-block side-classification">
            <div className="playground-section-label">Classificacao</div>
            {selectedConversation ? (
              <>
                <span className={`badge-class ${classificationBadgeClass(selectedConversation.lead.classification)}`}>
                  {selectedConversation.lead.classification ?? "sem classificacao"}
                </span>
                {selectedConversation.lead.classification_reason ? (
                  <p className="side-classification-reason">{selectedConversation.lead.classification_reason}</p>
                ) : null}
              </>
            ) : (
              <p className="side-empty">Aguardando conversa.</p>
            )}
          </div>

          <div className="side-block">
            <div className="playground-section-label">Perfil coletado</div>
            <ProfileGrid profile={selectedConversation?.lead_profile ?? null} />
          </div>

          <div className="side-block">
            <div className="playground-section-label">Function calls ({toolCalls.length})</div>
            {toolCalls.length === 0 ? (
              <p className="side-empty">Nenhuma tool acionada ainda.</p>
            ) : (
              <div className="side-toolcalls">
                {toolCalls.map((call) => (
                  <div key={call.id} className="side-toolcall">
                    <div className="side-toolcall-head">
                      <span className="side-toolcall-name">{call.tool_name}</span>
                      <span className="side-toolcall-time">{formatTime(call.created_at)}</span>
                    </div>
                    <pre className="side-toolcall-payload">
                      {JSON.stringify(call.tool_payload ?? {}, null, 2)}
                    </pre>
                  </div>
                ))}
              </div>
            )}
          </div>

          {selectedConversation?.summary_text ? (
            <div className="side-block">
              <div className="playground-section-label">Resumo</div>
              <p className="side-classification-reason">{selectedConversation.summary_text}</p>
            </div>
          ) : null}
        </aside>
      </div>
    </SectionCard>
  );
}

function ProfileGrid({ profile }: { profile: ConsoleLeadProfile | null }) {
  if (!profile) return <p className="side-empty">Sem perfil ainda.</p>;
  const rows: Array<[string, string | null]> = [
    ["Renda fam.", profile.family_income !== null ? `R$ ${profile.family_income.toLocaleString("pt-BR")}` : null],
    ["FGTS", profile.uses_fgts === null ? null : profile.uses_fgts ? "sim" : "nao"],
    ["Comprovacao", profile.proof_of_income_type],
    ["Carteira", profile.employment_history_months !== null ? `${profile.employment_history_months}m` : null],
    ["Civil", profile.marital_status],
    ["Nascimento", profile.birth_date],
    ["Dependentes", profile.dependents_summary],
    ["Empreend.", profile.interest_project],
    ["Regiao", profile.interest_region],
    ["Agendado", profile.scheduled_at ? formatDateTime(profile.scheduled_at) : null],
  ];
  const filled = rows.filter(([, value]) => value !== null && value !== "");
  if (filled.length === 0) return <p className="side-empty">Sem dados estruturados ainda.</p>;
  return (
    <dl className="side-profile">
      {filled.map(([label, value]) => (
        <div key={label} className="side-profile-item">
          <dt>{label}</dt>
          <dd>{value}</dd>
        </div>
      ))}
    </dl>
  );
}

const CHUNK_REVEAL_DELAY_MS = 1200;

async function revealConversationProgressively(
  full: ConsoleConversationDetail,
  previousIds: Set<string>,
  setter: (next: ConsoleConversationDetail) => void,
): Promise<void> {
  const newAiTextMessages = full.messages.filter(
    (msg) => !previousIds.has(msg.id) && msg.sent_by_ai && !msg.tool_name && msg.message_type === "text",
  );

  if (newAiTextMessages.length <= 1) {
    setter(full);
    return;
  }

  const newAiIds = new Set(newAiTextMessages.map((m) => m.id));
  const baseline = full.messages.filter((msg) => !newAiIds.has(msg.id));
  setter({ ...full, messages: baseline });

  for (let i = 0; i < newAiTextMessages.length; i += 1) {
    await new Promise((resolve) => setTimeout(resolve, CHUNK_REVEAL_DELAY_MS));
    const upTo = newAiTextMessages.slice(0, i + 1);
    setter({ ...full, messages: [...baseline, ...upTo] });
  }

  setter(full);
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

function classificationBadgeClass(classification: string | null | undefined) {
  switch (classification) {
    case "agendado":
      return "badge-class--scheduled";
    case "quente":
      return "badge-class--hot";
    case "morno":
      return "badge-class--warm";
    case "frio":
      return "badge-class--cold";
    default:
      return "badge-class--neutral";
  }
}

function initialsOf(value: string) {
  const cleaned = value.replace(/^playground-/, "Lead ");
  return cleaned
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("") || "L";
}

function formatPhone(phone: string) {
  if (phone.startsWith("playground-")) return phone.replace("playground-", "test ");
  return phone;
}

function labelMessageType(type: string) {
  return `[${type}] Mensagem sem texto visivel.`;
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
