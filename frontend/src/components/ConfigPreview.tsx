import { ENGINE_CORE } from "../data/runtimeConfig";
import { Icon } from "./Icons";
import type { TenantConfig } from "../types";

export function ConfigPreview({
  config,
  generatedConfig,
  currentState,
  currentEvent,
}: {
  config: TenantConfig;
  generatedConfig: object;
  currentState: string;
  currentEvent: string;
}) {
  const steps = [
    { icon: Icon.whats, title: "Mensagem chegou", text: "A SATI recebe a mensagem e abre o contexto do lead." },
    { icon: Icon.layers, title: "Etapa da conversa", text: `Agora estamos em: ${currentState}. O que aconteceu foi: ${currentEvent}.` },
    { icon: Icon.spark, title: "Como a SATI conduz", text: `${config.strategy} define a proxima pergunta ou acao com base no modelo ${config.template}.` },
    { icon: Icon.bolt, title: "Regras do atendimento", text: `Parcela maxima ${config.maxParcelPercent}% e score quente acima de ${config.hotThreshold}.` },
    { icon: Icon.plug, title: "Envio para CRM", text: `Se estiver pronto, o lead segue para ${config.crmProvider} depois da validacao interna.` },
  ];

  return (
    <div className="preview-grid">
      <div className="preview-list">
        {steps.map((step) => {
          const StepIcon = step.icon;
          return (
            <div key={step.title} className="preview-step">
              <strong style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <StepIcon />
                {step.title}
              </strong>
              <p>{step.text}</p>
            </div>
          );
        })}

        <div className="preview-step">
          <strong style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <Icon.database />
            Motor central da SATI
          </strong>
          <p>{ENGINE_CORE.engineVersion} · {ENGINE_CORE.stateMachineVersion} · {ENGINE_CORE.queueModel}</p>
        </div>
      </div>

      <div className="mono-box">{JSON.stringify(generatedConfig, null, 2)}</div>
    </div>
  );
}
