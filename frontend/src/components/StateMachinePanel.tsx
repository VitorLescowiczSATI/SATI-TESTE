import { EVENTS, STATES, TRANSITIONS } from "../data/runtimeConfig";

export function StateMachinePanel({
  currentState,
  currentEvent,
  onStateChange,
  onEventChange,
}: {
  currentState: string;
  currentEvent: string;
  onStateChange: (stateKey: string) => void;
  onEventChange: (event: string) => void;
}) {
  const stateMeta = STATES.find((state) => state.key === currentState)!;
  const transition = (TRANSITIONS[currentState] || {})[currentEvent];
  const nextStateLabel = transition
    ? (STATES.find((state) => state.key === transition.next)?.title || transition.next)
    : "sem mudanca";

  return (
    <div className="state-machine-layout">
      <div className="state-column">
        <div className="field-block">
          <label>Em que momento a conversa esta</label>
          <select className="select" value={currentState} onChange={(e) => onStateChange(e.target.value)}>
            {STATES.map((state) => <option key={state.key} value={state.key}>{state.title}</option>)}
          </select>
        </div>

        <div className="state-list">
          {STATES.map((state) => (
            <div key={state.key} className={`state-item ${state.key === currentState ? "active" : ""}`}>
              <strong>{state.title}</strong>
              <p>{state.goal}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="transition-column">
        <div className="field-block">
          <label>O que aconteceu agora</label>
          <select className="select" value={currentEvent} onChange={(e) => onEventChange(e.target.value)}>
            {(EVENTS[currentState] || []).map((event) => <option key={event} value={event}>{event}</option>)}
          </select>
        </div>

        <div className="transition-card">
          <h4>{stateMeta.title} {"->"} {nextStateLabel}</h4>
          <p>{transition ? transition.explanation : "Para esse acontecimento, a conversa nao muda de etapa."}</p>

          {transition ? (
            <>
              <div className="pill-row" style={{ marginTop: 12 }}>
                <span className="config-chip active">Como a SATI conduz: {transition.strategy}</span>
              </div>
              <h5>Regras usadas nessa decisao</h5>
              <div className="pill-row">
                {transition.policies.map((policy) => <span key={policy} className="config-chip">{policy}</span>)}
              </div>
              <h5>O que o sistema faz depois disso</h5>
              <div className="pill-row">
                {transition.actions.map((action) => <span key={action} className="config-chip">{action}</span>)}
              </div>
            </>
          ) : null}
        </div>

        <div className="transition-card">
          <h4>Traduzindo para uma linguagem mais simples</h4>
          <p>
            Aqui a ideia e responder tres perguntas:
            em que etapa a conversa esta, o que aconteceu agora e o que a SATI faz em seguida.
          </p>
        </div>

        <div className="transition-card">
          <h4>O que voce pode ajustar nessa etapa</h4>
          <div className="detail-list">
            <div>
              <strong>Voce pode mexer</strong>
              <ul>
                {stateMeta.configurable.map((item) => <li key={item}>{item}</li>)}
              </ul>
            </div>
            <div>
              <strong>Fica fixo na SATI</strong>
              <ul>
                {stateMeta.protected.map((item) => <li key={item}>{item}</li>)}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
