import { useEffect, useMemo, useState } from "react";
import { Icon } from "../components/Icons";
import { RuntimeCard } from "../components/RuntimeCard";
import { SectionCard } from "../components/SectionCard";
import { listActiveConversations, type ConsoleConversationSummary } from "../features/inbox/conversationApi";
import { getTodayMetrics, type TodayMetrics } from "../features/metrics/metricsApi";
import type { DemoSession } from "../types";

type DashboardPageProps = {
  session: DemoSession | null;
  onOpenPlayground: () => void;
};

const CLASSIFICATION_ORDER: Array<{ key: string; label: string; tone: string }> = [
  { key: "agendado", label: "Agendado", tone: "badge-class--scheduled" },
  { key: "quente", label: "Quente", tone: "badge-class--hot" },
  { key: "morno", label: "Morno", tone: "badge-class--warm" },
  { key: "frio", label: "Frio", tone: "badge-class--cold" },
  { key: "corretor", label: "Corretor", tone: "badge-class--neutral" },
  { key: "sem_classificacao", label: "Sem classif.", tone: "badge-class--neutral" },
];

export function DashboardPage({ session, onOpenPlayground }: DashboardPageProps) {
  const [metrics, setMetrics] = useState<TodayMetrics | null>(null);
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
      const [nextMetrics, nextConversations] = await Promise.all([
        getTodayMetrics(),
        listActiveConversations(),
      ]);
      setMetrics(nextMetrics);
      setConversations(nextConversations);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel carregar o dashboard.");
    } finally {
      setLoading(false);
    }
  }

  const distribution = useMemo(() => {
    if (!metrics) return [];
    const total = Object.values(metrics.classification_distribution).reduce((acc, n) => acc + n, 0);
    return CLASSIFICATION_ORDER.map((entry) => {
      const count = metrics.classification_distribution[entry.key] ?? 0;
      const percent = total > 0 ? Math.round((count / total) * 100) : 0;
      return { ...entry, count, percent };
    });
  }, [metrics]);

  const lastInboundLabel = metrics?.last_inbound_at ? formatDateTime(metrics.last_inbound_at) : "sem inbound ainda";

  return (
    <>
      <section className="hero-panel">
        <div className="hero-grid">
          <div>
            <div className="badge badge--brand" style={{ marginBottom: 14 }}>
              MVP-demo - {session?.tenantName ?? "Tenda RJ"}
            </div>
            <h1 style={{ margin: 0, fontSize: 32, letterSpacing: "-0.03em" }}>
              Dashboard de leitura real.
              <br />
              <span style={{ color: "rgba(255,255,255,.82)" }}>
                Tudo aqui vem direto do banco do MVP.
              </span>
            </h1>
            <p className="caption" style={{ marginTop: 14, fontSize: 15, lineHeight: 1.6 }}>
              Numeros reais do dia: leads que entraram, conversas ativas, classificacao e
              tools que a Maju acionou.
            </p>
            <div className="hero-actions" style={{ marginTop: 18 }}>
              <span className="hero-chip"><Icon.checkCircle /> Login real</span>
              <span className="hero-chip"><Icon.database /> Banco real</span>
              <span className="hero-chip"><Icon.spark /> GPT + tools</span>
            </div>
          </div>
        </div>
      </section>

      {error ? <div className="alert alert--error" style={{ marginBottom: 18 }}>{error}</div> : null}

      <div className="top-summary">
        <RuntimeCard
          label="Leads hoje"
          value={loading ? "..." : String(metrics?.leads_today ?? 0)}
          note={`Total no tenant: ${metrics?.leads_total ?? 0}`}
        />
        <RuntimeCard
          label="Conversas ativas"
          value={loading ? "..." : String(metrics?.conversations_active ?? 0)}
          note="Status ativa no banco"
        />
        <RuntimeCard
          label="Msgs do lead hoje"
          value={loading ? "..." : String(metrics?.messages_inbound_today ?? 0)}
          note={`Maju respondeu: ${metrics?.messages_outbound_today ?? 0}`}
        />
        <RuntimeCard
          label="Ultima entrada"
          value={loading ? "..." : lastInboundLabel}
          note="Mensagem mais recente do lead"
        />
      </div>

      <div className="dashboard-grid">
        <SectionCard
          title="Distribuicao de leads por classificacao"
          subtitle="Estado atual de todos os leads do tenant."
          badge={{ label: "Real-time", className: "badge--brand" }}
          actions={
            <button className="btn btn--secondary btn--sm" onClick={() => void loadDashboard()} disabled={loading}>
              <Icon.inbox /> Atualizar
            </button>
          }
        >
          {distribution.length === 0 ? (
            <p className="side-empty">Sem dados ainda.</p>
          ) : (
            <ul className="dist-list">
              {distribution.map((entry) => (
                <li key={entry.key} className="dist-row">
                  <div className="dist-row-head">
                    <span className={`badge-class ${entry.tone}`}>{entry.label}</span>
                    <span className="dist-row-value">
                      {entry.count} <span className="dist-row-percent">({entry.percent}%)</span>
                    </span>
                  </div>
                  <div className="dist-bar">
                    <div
                      className={`dist-bar-fill ${entry.tone}-fill`}
                      style={{ width: `${entry.percent}%` }}
                    />
                  </div>
                </li>
              ))}
            </ul>
          )}
        </SectionCard>

        <SectionCard
          title="Tools disparadas hoje"
          subtitle="Quantas vezes a Maju chamou cada funcao."
          badge={{ label: "Function calling", className: "badge--outline" }}
        >
          {!metrics || metrics.tool_calls_today.length === 0 ? (
            <p className="side-empty">Nenhuma tool disparada hoje ainda.</p>
          ) : (
            <ul className="tool-stat-list">
              {metrics.tool_calls_today.map((stat) => (
                <li key={stat.name} className="tool-stat-row">
                  <span className="tool-stat-name">{stat.name}</span>
                  <span className="tool-stat-count">{stat.count}</span>
                </li>
              ))}
            </ul>
          )}
        </SectionCard>
      </div>

      <div className="dashboard-grid">
        <SectionCard
          title="Conversas mais recentes"
          subtitle="Ultimas conversas do tenant, ativas ou nao."
          badge={{ label: "Banco real", className: "badge--brand" }}
        >
          {conversations.length === 0 ? (
            <div className="card card--padded card--flat">
              <strong>Nenhuma conversa ainda</strong>
              <p className="caption" style={{ marginTop: 8 }}>
                Crie um lead de teste no Playground pra primeira conversa aparecer aqui.
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
                      {conversation.message_count} mensagens - {humanizeState(conversation.runtime_state)}
                      {conversation.lead.classification ? ` - ${conversation.lead.classification}` : ""}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </SectionCard>

        <SectionCard
          title="Proximo passo"
          subtitle="O que fazer agora."
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
                <strong>Configurar OPENAI_API_KEY no Render</strong>
                <p>Sem ela o Playground retorna 503.</p>
              </div>
            </div>
            <div className="timeline-step">
              <span className="timeline-index">2</span>
              <div>
                <strong>Criar lead de teste</strong>
                <p>Playground cria lead, conversa e primeira linha real no banco.</p>
              </div>
            </div>
            <div className="timeline-step">
              <span className="timeline-index">3</span>
              <div>
                <strong>Conversar com a Maju</strong>
                <p>Cada troca aparece aqui no Dashboard com classificacao e tools.</p>
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
