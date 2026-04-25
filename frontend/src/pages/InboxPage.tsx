import { useEffect, useState } from "react";
import { Icon } from "../components/Icons";
import { SectionCard } from "../components/SectionCard";
import {
  createPlaygroundConversation,
  getConversationDetail,
  listActiveConversations,
  sendPlaygroundMessage,
  type ConsoleConversationDetail,
  type ConsoleConversationSummary,
} from "../features/inbox/conversationApi";

export function InboxPage() {
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
        if (!cancelled) {
          setSelectedConversation(conversation);
        }
      })
      .catch((error) => {
        if (!cancelled) {
          setError(error instanceof Error ? error.message : "Nao foi possivel carregar a conversa.");
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
      const nextConversations = await listActiveConversations();
      setConversations(nextConversations);
      setSelectedId((currentId) => currentId ?? nextConversations[0]?.id ?? null);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Nao foi possivel carregar as conversas.");
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
    } catch (error) {
      setError(error instanceof Error ? error.message : "Nao foi possivel criar o lead de teste.");
    } finally {
      setCreating(false);
    }
  }

  async function submitMessage(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = draftMessage.trim();
    if (!message || !selectedId) {
      return;
    }

    setSending(true);
    setError("");

    try {
      setDraftMessage("");
      const conversation = await sendPlaygroundMessage(selectedId, message);
      setSelectedConversation(conversation);
      await refreshConversations();
    } catch (error) {
      setError(error instanceof Error ? error.message : "Nao foi possivel enviar a mensagem.");
      setDraftMessage(message);
    } finally {
      setSending(false);
    }
  }

  return (
    <SectionCard
      title="Playground da Maju"
      subtitle="Simule um lead real, converse com o GPT e salve tudo no banco para aparecer no Dashboard."
      badge={{ label: "GPT integrado", className: "badge--brand" }}
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

      <div className="inbox-layout">
        <div className="conversation-list">
          {loading && conversations.length === 0 ? (
            <div className="card card--padded">
              <strong>Carregando conversas...</strong>
              <p className="caption" style={{ marginTop: 8 }}>Buscando mensagens salvas no backend.</p>
            </div>
          ) : null}

          {!loading && conversations.length === 0 ? (
            <div className="card card--padded">
              <strong>Nenhum lead de teste ainda</strong>
              <p className="caption" style={{ marginTop: 8 }}>
                Crie um lead de teste e mande a primeira mensagem para a Maju responder com GPT.
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
                <p>{item.last_message_preview || "Mensagem sem texto. Pode ser midia, botao ou evento."}</p>
                <span>{item.message_count} msg - {formatDateTime(item.updated_at)}</span>
              </button>
            );
          })}
        </div>

        <div className="card card--padded">
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
            <button className="btn btn--secondary btn--sm" disabled={!selectedConversation}>
              <Icon.phone /> Assumir atendimento
            </button>
          </div>

          <div className="chat" style={{ minHeight: 360 }}>
            {!selectedConversation ? <div className="bubble system">Crie um lead de teste para comecar</div> : null}

            {selectedConversation?.messages.map((message) => (
              <div
                key={message.id}
                className={`bubble ${message.sent_by_ai ? "ai" : message.direction === "inbound" ? "in" : "out"}`}
              >
                {message.sent_by_ai ? <span className="tag">SATI</span> : null}
                {message.content_text || labelMessageType(message.message_type)}
                <span className="time">{formatTime(message.created_at)}</span>
              </div>
            ))}
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
        </div>
      </div>
    </SectionCard>
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
