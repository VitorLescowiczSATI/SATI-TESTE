import { useEffect, useState } from "react";
import { Icon } from "../components/Icons";
import { SectionCard } from "../components/SectionCard";
import {
  getConversationDetail,
  listActiveConversations,
  type ConsoleConversationDetail,
  type ConsoleConversationSummary,
} from "../features/inbox/conversationApi";

export function InboxPage() {
  const [conversations, setConversations] = useState<ConsoleConversationSummary[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<ConsoleConversationDetail | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
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

  return (
    <SectionCard
      title="Playground WhatsApp"
      subtitle="Use esta tela para acompanhar mensagens reais do numero de teste e validar a Maju com calma."
      badge={{ label: "Webhook real", className: "badge--brand" }}
      actions={
        <button className="btn btn--secondary btn--sm" onClick={() => void refreshConversations()} disabled={loading}>
          <Icon.inbox /> Atualizar
        </button>
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
              <strong>Nenhuma conversa ainda</strong>
              <p className="caption" style={{ marginTop: 8 }}>
                Assim que uma mensagem bater no webhook do WhatsApp, ela aparece aqui.
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

          <div className="chat">
            {!selectedConversation ? <div className="bubble system">Aguardando mensagens do webhook</div> : null}

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
