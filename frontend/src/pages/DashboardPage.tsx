import { Icon } from "../components/Icons";
import { RuntimeCard } from "../components/RuntimeCard";
import { SectionCard } from "../components/SectionCard";
import type { DemoSession } from "../types";

type DashboardPageProps = {
  session: DemoSession | null;
  onOpenRuntime: () => void;
};

/**
 * DashboardPage - tela operacional do gestor.
 * Tom: numeros do dia, sem jargao tecnico interno.
 * Copy alinhada com Copy Oficial - Site e Marketing.
 */
export function DashboardPage({ session, onOpenRuntime }: DashboardPageProps) {
  return (
    <>
      <section className="hero-panel">
        <div className="hero-grid">
          <div>
            <div className="badge badge--brand" style={{ marginBottom: 14 }}>
              Operação rodando · {session?.tenantName ?? "Tenda RJ"}
            </div>
            <h1 style={{ margin: 0, fontSize: 32, letterSpacing: "-0.03em" }}>
              Hoje sua operação respondeu 100% dos leads
              <br />
              <span style={{ color: "rgba(255,255,255,.82)" }}>
                em segundos, qualificou e agendou visitas sem você precisar tocar.
              </span>
            </h1>
            <p className="caption" style={{ marginTop: 14, fontSize: 15, lineHeight: 1.6 }}>
              Acompanhe abaixo quantos leads chegaram, quantos viraram agendamento e o tempo médio
              de resposta da Sati IA na sua operação.
            </p>
            <div className="hero-actions" style={{ marginTop: 18 }}>
              <span className="hero-chip"><Icon.checkCircle /> Resposta imediata 24/7</span>
              <span className="hero-chip"><Icon.layers /> Qualificação automática</span>
              <span className="hero-chip"><Icon.whats /> Agendamento sem fricção</span>
            </div>
          </div>
          <div className="card card--padded" style={{ background: "rgba(255,255,255,.96)" }}>
            <div className="section-title" style={{ marginBottom: 12 }}>
              <div>
                <h3 style={{ margin: 0 }}>Resumo de hoje</h3>
                <div className="section-subtitle">Atualizado em tempo real.</div>
              </div>
            </div>
            <div className="preview-list">
              <div className="preview-step">
                <strong>37 leads atendidos</strong>
                <p>Todos receberam resposta em menos de 30 segundos.</p>
              </div>
              <div className="preview-step">
                <strong>11 qualificados</strong>
                <p>Renda, perfil MCMV e interesse confirmados pela IA.</p>
              </div>
              <div className="preview-step">
                <strong>8 visitas agendadas</strong>
                <p>Já caíram na agenda do corretor responsável.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="top-summary">
        <RuntimeCard label="Leads do dia" value="37" note="Entrada via WhatsApp e Meta Ads" />
        <RuntimeCard label="Tempo médio de resposta" value="22s" note="Mercado: 9h33" />
        <RuntimeCard label="Taxa de conversão" value="25%" note="Leads que viraram agendamento" />
        <RuntimeCard label="Visitas agendadas" value="8" note="Hoje, sem intervenção humana" />
      </div>

      <div className="dashboard-grid">
        <SectionCard
          title="Como sua operação está performando"
          subtitle="Comparativo entre o mercado e a sua operação com a Sati."
          badge={{ label: "Performance", className: "badge--brand" }}
        >
          <div className="signal-grid">
            <div className="signal-card">
              <strong>Cobertura de leads</strong>
              <p>100% dos leads atendidos. No mercado, 23,8% nunca recebem resposta.</p>
            </div>
            <div className="signal-card">
              <strong>Tempo de resposta</strong>
              <p>22 segundos em média. O mercado responde em 9h33.</p>
            </div>
            <div className="signal-card">
              <strong>Taxa de conversão</strong>
              <p>25% dos leads viram agendamento, contra 12% antes da IA.</p>
            </div>
            <div className="signal-card">
              <strong>Mídia paga</strong>
              <p>Cada real investido volta em mais agendamento e mais venda.</p>
            </div>
          </div>
        </SectionCard>

        <SectionCard
          title="O que precisa do seu olhar"
          subtitle="Pontos onde um humano pode acelerar o resultado."
          badge={{ label: "Ação rápida", className: "badge--outline" }}
          actions={
            <button className="btn btn--secondary btn--sm" onClick={onOpenRuntime}>
              <Icon.settings /> Ver atendimento da IA
            </button>
          }
        >
          <div className="timeline-list">
            <div className="timeline-step">
              <span className="timeline-index">1</span>
              <div>
                <strong>3 leads aguardando corretor</strong>
                <p>Já estão qualificados e prontos para receber o contato humano.</p>
              </div>
            </div>
            <div className="timeline-step">
              <span className="timeline-index">2</span>
              <div>
                <strong>4 visitas a confirmar amanhã</strong>
                <p>A Sati vai mandar lembrete automático 2h antes.</p>
              </div>
            </div>
            <div className="timeline-step">
              <span className="timeline-index">3</span>
              <div>
                <strong>18 leads em follow-up</strong>
                <p>Sem resposta há mais de 1h. A IA já está reengajando.</p>
              </div>
            </div>
          </div>
        </SectionCard>
      </div>
    </>
  );
}
