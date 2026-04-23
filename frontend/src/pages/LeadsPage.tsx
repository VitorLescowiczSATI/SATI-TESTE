import { Icon } from "../components/Icons";
import { SectionCard } from "../components/SectionCard";

const leads = [
  { initials: "JS", name: "Joao Silva", source: "Meta Ads", region: "Itaquera", score: "82", tone: "badge--hot", label: "quente" },
  { initials: "MC", name: "Marina Costa", source: "Formulario", region: "Campo Grande", score: "71", tone: "badge--warm", label: "morno" },
  { initials: "CR", name: "Carlos Ramos", source: "Retomada", region: "Bonsucesso", score: "59", tone: "badge--cold", label: "frio" },
  { initials: "AF", name: "Ana Ferreira", source: "Organico", region: "Taquara", score: "88", tone: "badge--sched", label: "agendado" },
];

export function LeadsPage() {
  return (
    <>
      <div className="top-summary">
        <div className="kpi">
          <div className="kpi-label">Leads do dia</div>
          <div className="kpi-value">37</div>
          <div className="kpi-note">Entrada principal via WhatsApp.</div>
        </div>
        <div className="kpi">
          <div className="kpi-label">Quentes</div>
          <div className="kpi-value">11</div>
          <div className="kpi-note">Prontos para corretor ou agendamento.</div>
        </div>
        <div className="kpi">
          <div className="kpi-label">Aguardando resposta</div>
          <div className="kpi-value">18</div>
          <div className="kpi-note">Candidatos a follow-up.</div>
        </div>
        <div className="kpi">
          <div className="kpi-label">Enviados ao CRM</div>
          <div className="kpi-value">33</div>
          <div className="kpi-note">Já caíram na esteira do corretor.</div>
        </div>
      </div>

      <SectionCard
        title="Fila de leads qualificados"
        subtitle="Quem está pronto para receber contato do corretor agora."
        badge={{ label: "Prioridade", className: "badge--brand" }}
        actions={
          <>
            <button className="btn btn--ghost btn--sm"><Icon.funnel /> Filtrar</button>
            <button className="btn btn--secondary btn--sm"><Icon.spark /> Reordenar</button>
          </>
        }
      >
        <div className="stack">
          {leads.map((lead) => (
            <div key={lead.name} className="lead-card">
              <div className="avatar">{lead.initials}</div>
              <div className="info">
                <div className="name">{lead.name}</div>
                <div className="meta">
                  <span>{lead.source}</span>
                  <span className="sep">•</span>
                  <span>{lead.region}</span>
                  <span className="sep">•</span>
                  <span>Tenda RJ</span>
                </div>
              </div>
              <div className="tail">
                <span className={`badge ${lead.tone}`}>{lead.label}</span>
                <div className="score">{lead.score}<small>/100</small></div>
              </div>
            </div>
          ))}
        </div>
      </SectionCard>
    </>
  );
}
