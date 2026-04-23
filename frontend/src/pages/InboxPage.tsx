import { Icon } from "../components/Icons";
import { SectionCard } from "../components/SectionCard";

const conversations = [
  { id: "1", name: "Joao Silva", summary: "Pediu visita no Vista Verde e esta aguardando corretor.", time: "agora", hot: true },
  { id: "2", name: "Marina Costa", summary: "Ja informou FGTS e renda, falta tipologia.", time: "12 min", hot: false },
  { id: "3", name: "Carlos Ramos", summary: "Lead retomado pelo follow-up de 1h.", time: "28 min", hot: false },
];

export function InboxPage() {
  return (
    <SectionCard
      title="Atendimentos em andamento"
      subtitle="Acompanhe as conversas da sua operação no WhatsApp e assuma quando precisar."
      badge={{ label: "WhatsApp", className: "badge--brand" }}
    >
      <div className="inbox-layout">
        <div className="conversation-list">
          {conversations.map((item) => (
            <button key={item.id} type="button" className={`conversation-item ${item.id === "1" ? "active" : ""}`}>
              <div className="conversation-item-head">
                <strong>{item.name}</strong>
                <span className={`badge ${item.hot ? "badge--hot" : "badge--neutral"}`}>{item.hot ? "quente" : "andando"}</span>
              </div>
              <p>{item.summary}</p>
              <span>{item.time}</span>
            </button>
          ))}
        </div>

        <div className="card card--padded">
          <div className="section-title" style={{ marginBottom: 10 }}>
            <div>
              <h3 style={{ margin: 0 }}>Joao Silva</h3>
              <div className="section-subtitle">Vista Verde · Faixa 2 · pronto para o corretor</div>
            </div>
            <button className="btn btn--secondary btn--sm"><Icon.phone /> Assumir atendimento</button>
          </div>

          <div className="chat">
            <div className="bubble system">Hoje · 10:14</div>
            <div className="bubble in">Oi vi o anuncio do Vista Verde, quero saber<span className="time">10:14</span></div>
            <div className="bubble ai">
              <span className="tag">SATI</span>
              Oi! Posso te ajudar a ver se o Vista Verde cabe no seu perfil pelo Minha Casa Minha Vida. Voce mora em Sao Paulo?<span className="time">10:14</span>
            </div>
            <div className="bubble in">Moro sim, em Itaquera.<span className="time">10:15</span></div>
            <div className="bubble ai">
              <span className="tag">SATI</span>
              Perfeito. Antes de te mostrar valores, voce ja tem imovel no seu nome?<span className="time">10:15</span>
            </div>
            <div className="bubble in">Nao, e o primeiro.<span className="time">10:15</span></div>
            <div className="bubble ai">
              <span className="tag">SATI</span>
              Otimo. E qual e a renda familiar de voces por mes?<span className="time">10:16</span>
            </div>
          </div>
        </div>
      </div>
    </SectionCard>
  );
}
