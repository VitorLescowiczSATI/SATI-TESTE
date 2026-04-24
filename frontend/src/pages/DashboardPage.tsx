import { useEffect, useMemo, useState } from "react";
import { Icon } from "../components/Icons";
import { RuntimeCard } from "../components/RuntimeCard";
import { SectionCard } from "../components/SectionCard";
import { listActiveConversations, type ConsoleConversationSummary } from "../features/inbox/conversationApi";
import type { DemoSession } from "../types";

type DashboardPageProps = {
  session: DemoSession | null;
  onOpenPlayground: () => void;
};

export function DashboardPage({ session, onOpenPlayground }: DashboardPageProps) {
  const [conversations, setConversations] = useState<ConsoleConversationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    void loadDashboard();
  }, []);

  async function loadDashboard() {
    setLoading(true);
    setError("");

    try {
      const nextConversations = await listActiveConversations();
      setConversations(nextConversations);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Nao foi possivel carregar o dashboard.");
    } finally {
      setLoading(false);
    }
  }

  const metrics = useMemo(() => {
    const leadIds = new Set(conversations.map((conversation) => conversation.lead.id));
    const messageCount = conversations.reduce((total, conversation) => total + conversation.message_count, 0);
    const latestUpdate = conversations[0]?.updated_at ? formatDateTime(conversations[0].updated_at) : "sem dados";

    return {
      conversations: conversations.length,
      leads: leadIds.size,
      messages: messageCount,
      latestUpdate,
    };
  }, [conversations]);

  return (
    <>
      <section className="hero-panel">
        <div className="hero-grid">
          <div>
            <div className="badge badge--brand" style={{ marginBottom: 14 }}>
              MVP-demo - {session?.tenantName ?? "Tenda RJ"}
            </div>
            <h1 style={{ margin: 0, fontSize: 32, letterSpacing: "-0.03em" }}>
              Dashboard inicial, sem numeros inventados.
              <br />
              <span style={{ color: "rgba(255,255,255,.82)" }}>
                Aqui so aparece o que entrou de verdade pelo backend.
              </span>
            </h1>
            <p className="caption" style={{ marginTop: 14, fontSize: 15, lineHeight: 1.6 }}>
              Primeiro objetivo: validar login, webhook, persistencia e leitura das conversas antes de
              ligar a IA da Maju.
            </p>
            <div className="hero-actions" style={{ marginTop: 18 }}>
              <span className="hero-chip"><Icon.checkCircle /> Login real</span>
              <span className="hero-chip"><Icon.database /> Banco real</span>
              <span className="hero-chip"><Icon.whats /> Webhook em preparacao</span>
            </div>
          </div>

          <div className="card card--padded" style={{ background: "rgba(255,255,255,.96)" }}>
            <div className="section-title" style={{ marginBottom: 12 }}>
              <div>
                <h3 style={{ margin: 0 }}>Estado do MVP</h3>
                <div className="section-subtitle">Leitura real do ambiente atual.</div>
              </div>
            </div>
            <div className="preview-list">
              <div className="preview-step">
                <strong>Autenticacao funcionando</strong>
                <p>O login ja usa sessao real com cookie httpOnly.</p>
              </div>
              <div className="preview-step">
                <strong>Webhook preparado</strong>
                <p>A proxima validacao e receber mensagens reais da Meta.</p>
              </div>
              <div className="preview-step">
                <strong>IA ainda desligada</strong>
                <p>A Maju entra depois que a entrada e o playground estiverem confiaveis.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {error ? <div className="alert alert--error" style={{ marginBottom: 18 }}>{error}</div> : null}

      <div className="top-summary">
        <RuntimeCard label="Conversas reais" value={loading ? "..." : String(metrics.conversations)} note="Criadas pelo webhook ou backend" />
        <RuntimeCard label="Leads unicos" value={loading ? "..." : String(metrics.leads)} note="Telefones identificados no tenant" />
        <RuntimeCard label="Mensagens salvas" value={loading ? "..." : String(metrics.messages)} note="Total persistido no banco" />
        <RuntimeCard label="Ultima entrada" value={loading ? "..." : metrics.latestUpdate} note="Baseado na conversa mais recente" />
      </div>

      <div className="dashboard-grid">
        <SectionCard
          title="Conversas capturadas"
          subtitle="Lista real vinda de /api/conversations/active."
          badge={{ label: "Dados reais", className: "badge--brand" }}
          actions={
            <button className="btn btn--secondary btn--sm" onClick={() => void loadDashboard()} disabled={loading}>
              <Icon.inbox /> Atualizar
            </button>
          }
        >
          {conversations.length === 0 ? (
            <div className="card card--padded card--flat">
              <strong>Nenhuma conversa real ainda</strong>
              <p className="caption" style={{ marginTop: 8 }}>
                Isso e esperado antes de configurar o webhook da Meta. Quando a primeira mensagem chegar,
                os numeros desta tela deixam de ser zero automaticamente.
              </p>
            </div>
          ) : (
            <div className="timeline-list">
              {conversations.slice(0, 5).map((conversation, index) => (
                <div className="timeline-step" key={conversation.id}>
                  <span className="timeline-index">{index + 1}</span>
                  <div>
                    <strong>{conversation.lead.name || conversation.lead.phone}</strong>
                    <p>
                      {conversation.message_count} mensagens - estado {humanizeState(conversation.runtime_state)} -{" "}
                      {conversation.last_message_preview || "sem texto visivel"}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </SectionCard>

        <SectionCard
          title="Proximo teste"
          subtitle="O caminho mais curto para validar com o Aristeu."
          badge={{ label: "Operacional", className: "badge--outline" }}
          actions={
            <button className="btn btn--secondary btn--sm" onClick={onOpenPlayground}>
              <Icon.whats /> Abrir Playground
            </button>
          }
        >
          <div className="timeline-list">
            <div className="timeline-step">
              <span className="timeline-index">1</span>
              <div>
                <strong>Configurar WHATSAPP_VERIFY_TOKEN no Render</strong>
                <p>Esse token e usado pela Meta para validar o webhook.</p>
              </div>
            </div>
            <div className="timeline-step">
              <span className="timeline-index">2</span>
              <div>
                <strong>Apontar webhook na Meta</strong>
                <p>URL: /webhooks/whatsapp no backend do Render.</p>
              </div>
            </div>
            <div className="timeline-step">
              <span className="timeline-index">3</span>
              <div>
                <strong>Enviar primeira mensagem real</strong>
                <p>O Playground deve mostrar a conversa salva no banco.</p>
              </div>
            </div>
          </div>
        </SectionCard>
      </div>
    </>
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

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}
