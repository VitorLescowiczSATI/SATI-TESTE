import { useMemo, useState } from "react";
import { ConfigPreview } from "../../components/ConfigPreview";
import { Icon } from "../../components/Icons";
import { PolicySlider } from "../../components/PolicySlider";
import { RuntimeCard } from "../../components/RuntimeCard";
import { SectionCard } from "../../components/SectionCard";
import { StateMachinePanel } from "../../components/StateMachinePanel";
import { TabBar } from "../../components/TabBar";
import { TenantLibrary } from "../../components/TenantLibrary";
import {
  cloneConfig,
  ENGINE_CORE,
  EVENTS,
  FIELD_DEFINITIONS,
  FOLLOWUP_OPTIONS,
  STATUS_OPTIONS,
  TENANT_PRESETS,
} from "../../data/runtimeConfig";
import type { RuntimeTabKey, TenantConfig } from "../../types";

export function RuntimeWorkspace() {
  const [currentTenantId, setCurrentTenantId] = useState("tenda_rj");
  const [activeTab, setActiveTab] = useState<RuntimeTabKey>("geral");
  const [config, setConfig] = useState<TenantConfig>(cloneConfig(TENANT_PRESETS.tenda_rj));
  const [currentState, setCurrentState] = useState("novo");
  const [currentEvent, setCurrentEvent] = useState(EVENTS.novo[0]);

  function selectTenant(tenantId: string) {
    setCurrentTenantId(tenantId);
    setConfig(cloneConfig(TENANT_PRESETS[tenantId]));
    setCurrentState("novo");
    setCurrentEvent(EVENTS.novo[0]);
  }

  function updateConfig<K extends keyof TenantConfig>(key: K, value: TenantConfig[K]) {
    setConfig((prev) => ({ ...prev, [key]: value }));
  }

  function updateNested(group: "requiredFields" | "actions" | "fieldMappings", key: string, value: boolean | string) {
    setConfig((prev) => ({
      ...prev,
      [group]: {
        ...prev[group],
        [key]: value,
      },
    }));
  }

  function updateState(stateKey: string) {
    setCurrentState(stateKey);
    setCurrentEvent(EVENTS[stateKey][0] || "");
  }

  const enabledFieldCount = useMemo(
    () => Object.values(config.requiredFields).filter(Boolean).length,
    [config.requiredFields]
  );

  const enabledActionCount = useMemo(
    () => Object.values(config.actions).filter(Boolean).length,
    [config.actions]
  );

  const generatedConfig = useMemo(
    () => ({
      tenant: {
        id: config.id,
        name: config.tenantName,
        city: config.city,
        operationType: config.operationType,
        owner: config.owner,
      },
      template: {
        base: config.template,
        strategy: config.strategy,
        runtimeStatus: config.runtimeStatus,
        greetingStyle: config.greetingStyle,
        qualificationDepth: config.qualificationDepth,
      },
      featureFlags: {
        audioEnabled: config.audioEnabled,
        humanPause: config.humanPause,
        dashboardAfterCoreValidation: config.dashboardAfterValidation,
        autoSummary: config.autoSummary,
      },
      followup: {
        firstTouchMinutes: config.firstFollowupMinutes,
        secondTouchMinutes: config.secondFollowupMinutes,
        maxAttempts: config.maxAttempts,
      },
      policies: {
        maxParcelPercent: config.maxParcelPercent,
        hotThreshold: config.hotThreshold,
      },
      collection: Object.entries(config.requiredFields)
        .filter(([, enabled]) => enabled)
        .map(([field]) => field),
      actions: Object.entries(config.actions)
        .filter(([, enabled]) => enabled)
        .map(([action]) => action),
      crm: {
        provider: config.crmProvider,
        stage: config.crmStage,
        fieldMappings: config.fieldMappings,
      },
      assets: {
        mediaPack: config.mediaPack,
      },
      engineCore: ENGINE_CORE,
    }),
    [config]
  );

  const tabContent: Record<RuntimeTabKey, JSX.Element> = {
    geral: (
      <div className="stack">
        <SectionCard
          title="Como essa configuracao esta organizada"
          subtitle="A ideia aqui e separar o que e base da SATI do que muda para cada cliente."
          badge={{ label: "Visao simples", className: "badge--brand" }}
        >
          <div className="layer-grid">
            <div className="layer-card">
              <span className="badge badge--neutral">1. Fixo na SATI</span>
              <strong>Base principal</strong>
              <p>As etapas da conversa, as acoes disponiveis e as regras que evitam erro.</p>
            </div>
            <div className="layer-arrow"><Icon.arrowRight /></div>
            <div className="layer-card">
              <span className="badge badge--neutral">2. Reutilizavel</span>
              <strong>Modelo base de atendimento</strong>
              <p>Define objetivo comercial, tom da conversa e ordem principal da coleta.</p>
            </div>
            <div className="layer-arrow"><Icon.arrowRight /></div>
            <div className="layer-card active">
              <span className="badge badge--brand">3. Ajuste do cliente</span>
              <strong>O que muda por operacao</strong>
              <p>Etapa do Facilita, pacote de imagens, follow-up, dados obrigatorios e limites.</p>
            </div>
          </div>
        </SectionCard>

        <SectionCard
          title="Identidade do cliente"
          subtitle="Essa central existe por cliente e por operacao, como Tenda RJ ou Tenda SP."
          badge={{ label: "Cliente ativo", className: "badge--outline" }}
        >
          <div className="form-grid">
            <div className="field-block">
              <label>Nome do cliente</label>
              <input className="input" value={config.tenantName} onChange={(e) => updateConfig("tenantName", e.target.value)} />
            </div>
            <div className="field-block">
              <label>Cidade / operacao</label>
              <input className="input" value={config.city} onChange={(e) => updateConfig("city", e.target.value)} />
            </div>
          </div>

          <div className="form-grid" style={{ marginTop: 14 }}>
            <div className="field-block">
              <label>Modelo base</label>
              <select className="select" value={config.template} onChange={(e) => updateConfig("template", e.target.value)}>
                <option value="mcmv_tenda_base">mcmv_tenda_base</option>
                <option value="medio_alto_padrao_base">medio_alto_padrao_base</option>
              </select>
            </div>
            <div className="field-block">
              <label>Jeito de conduzir</label>
              <select className="select" value={config.strategy} onChange={(e) => updateConfig("strategy", e.target.value)}>
                <option value="mcmv_tenda_rj">mcmv_tenda_rj</option>
                <option value="mcmv_tenda_sp">mcmv_tenda_sp</option>
                <option value="sandbox_experimental">sandbox_experimental</option>
              </select>
            </div>
          </div>
        </SectionCard>

        <SectionCard
          title="Informacoes obrigatorias da qualificacao"
          subtitle="Em vez de montar um bloquinho por pergunta, voce diz quais dados precisam sair da conversa."
          badge={{ label: `${enabledFieldCount} dados`, className: "badge--brand" }}
        >
          <div className="check-grid">
            {FIELD_DEFINITIONS.map(([key, label, help]) => (
              <label key={key} className="check-card">
                <input
                  type="checkbox"
                  checked={config.requiredFields[key]}
                  onChange={(e) => updateNested("requiredFields", key, e.target.checked)}
                />
                <div>
                  <strong>{label}</strong>
                  <span>{help}</span>
                </div>
              </label>
            ))}
          </div>
        </SectionCard>
      </div>
    ),
    states: (
      <div className="stack">
        <SectionCard
          title="Etapas da conversa"
          subtitle="Aqui voce enxerga em que momento o atendimento esta e o que a SATI faz em seguida."
          badge={{ label: "Base protegida", className: "badge--brand" }}
        >
          <StateMachinePanel
            currentState={currentState}
            currentEvent={currentEvent}
            onStateChange={updateState}
            onEventChange={setCurrentEvent}
          />
        </SectionCard>
      </div>
    ),
    policies: (
      <div className="stack">
        <SectionCard
          title="Regras do atendimento"
          subtitle="Essas regras substituem condicoes espalhadas em varios bloquinhos."
          badge={{ label: "Decisao automatica", className: "badge--brand" }}
        >
          <div className="form-grid form-grid-3">
            <PolicySlider
              label="Parcela maxima da renda"
              value={config.maxParcelPercent}
              min={20}
              max={40}
              suffix="%"
              onChange={(value) => updateConfig("maxParcelPercent", value)}
              helper="Usado para limite basico de capacidade."
            />
            <PolicySlider
              label="Score minimo para quente"
              value={config.hotThreshold}
              min={50}
              max={95}
              onChange={(value) => updateConfig("hotThreshold", value)}
              helper="Ajuda a classificar o lead antes do CRM."
            />
            <PolicySlider
              label="Tentativas maximas"
              value={config.maxAttempts}
              min={1}
              max={5}
              onChange={(value) => updateConfig("maxAttempts", value)}
              helper="Depois disso, o lead pode ir para encerrado."
            />
          </div>

          <div className="form-grid" style={{ marginTop: 18 }}>
            <div className="field-block">
              <label>Primeiro follow-up</label>
              <select className="select" value={config.firstFollowupMinutes} onChange={(e) => updateConfig("firstFollowupMinutes", Number(e.target.value))}>
                {FOLLOWUP_OPTIONS.first.map((value) => <option key={value} value={value}>{value} minutos</option>)}
              </select>
            </div>
            <div className="field-block">
              <label>Segundo follow-up</label>
              <select className="select" value={config.secondFollowupMinutes} onChange={(e) => updateConfig("secondFollowupMinutes", Number(e.target.value))}>
                {FOLLOWUP_OPTIONS.second.map((value) => <option key={value} value={value}>{value} minutos</option>)}
              </select>
            </div>
          </div>
        </SectionCard>

        <SectionCard
          title="Controles de seguranca"
          subtitle="Esses botoes ajudam a ligar ou desligar comportamentos importantes por cliente."
          badge={{ label: "Liga / desliga", className: "badge--outline" }}
        >
          <div className="check-grid">
            <label className="check-card">
              <input type="checkbox" checked={config.humanPause} onChange={(e) => updateConfig("humanPause", e.target.checked)} />
              <div>
                <strong>Pausar IA quando humano assumir</strong>
                <span>Evita conflito no mesmo numero de WhatsApp.</span>
              </div>
            </label>
            <label className="check-card">
              <input type="checkbox" checked={config.dashboardAfterValidation} onChange={(e) => updateConfig("dashboardAfterValidation", e.target.checked)} />
              <div>
                <strong>Dashboard so depois da validacao do core</strong>
                <span>Mantem foco no bloco interno antes da camada cliente.</span>
              </div>
            </label>
            <label className="check-card">
              <input type="checkbox" checked={config.autoSummary} onChange={(e) => updateConfig("autoSummary", e.target.checked)} />
              <div>
                <strong>Resumo e classificacao automaticos</strong>
                <span>Gera output pronto para corretor e Facilita.</span>
              </div>
            </label>
            <label className="check-card">
              <input type="checkbox" checked={config.audioEnabled} onChange={(e) => updateConfig("audioEnabled", e.target.checked)} />
              <div>
                <strong>Audio no atendimento</strong>
                <span>No sandbox pode brincar. No MVP real, continua fora.</span>
              </div>
            </label>
          </div>
        </SectionCard>
      </div>
    ),
    crm: (
      <div className="stack">
        <SectionCard
          title="CRM e saida comercial"
          subtitle="Aqui fica o que sai da conversa e entra no CRM depois da validacao do core."
          badge={{ label: "Facilita", className: "badge--sched" }}
        >
          <div className="form-grid">
            <div className="field-block">
              <label>CRM inicial</label>
              <select className="select" value={config.crmProvider} onChange={(e) => updateConfig("crmProvider", e.target.value)}>
                <option value="facilita">Facilita</option>
                <option value="mock">Mock interno</option>
              </select>
            </div>
            <div className="field-block">
              <label>Etapa de destino</label>
              <input className="input" value={config.crmStage} onChange={(e) => updateConfig("crmStage", e.target.value)} />
            </div>
          </div>

          <div className="form-grid" style={{ marginTop: 14 }}>
            <div className="field-block">
              <label>Pacote de imagens</label>
              <select className="select" value={config.mediaPack} onChange={(e) => updateConfig("mediaPack", e.target.value)}>
                <option value="rio_verde">rio_verde</option>
                <option value="vista_verde">vista_verde</option>
                <option value="reserva_leste">reserva_leste</option>
              </select>
            </div>
            <div className="field-block">
              <label>Status do atendimento</label>
              <select className="select" value={config.runtimeStatus} onChange={(e) => updateConfig("runtimeStatus", e.target.value)}>
                {STATUS_OPTIONS.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
              </select>
            </div>
          </div>
        </SectionCard>

        <SectionCard
          title="Como os dados entram no Facilita"
          subtitle="Essa tabela mostra como o dado coletado na conversa sai da SATI e entra no CRM."
          badge={{ label: "Outbox + mapper", className: "badge--outline" }}
        >
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Origem SATI</th>
                  <th>Campo Facilita</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(config.fieldMappings).map(([source, target]) => (
                  <tr key={source}>
                    <td className="name-cell">{source}</td>
                    <td>
                      <input
                        className="input"
                        value={target}
                        onChange={(e) => updateNested("fieldMappings", source, e.target.value)}
                      />
                    </td>
                    <td><span className="badge badge--sched">mapeado</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </SectionCard>
      </div>
    ),
    preview: (
      <div className="stack">
        <SectionCard
          title="Resumo do funcionamento"
          subtitle="Essa tela tenta mostrar, de forma simples, como essa configuracao vira atendimento real."
          badge={{ label: "Visao final", className: "badge--brand" }}
        >
          <ConfigPreview
            config={config}
            generatedConfig={generatedConfig}
            currentState={currentState}
            currentEvent={currentEvent}
          />
        </SectionCard>
      </div>
    ),
  };

  return (
    <>
      <section className="hero-panel">
        <div className="hero-grid">
          <div>
            <div className="badge badge--brand" style={{ marginBottom: 14 }}>Central de configuracao por cliente</div>
            <h1 style={{ margin: 0, fontSize: 32, letterSpacing: "-0.03em" }}>
              A SATI nao configura bloquinhos.
              <br />
              <span style={{ color: "rgba(255,255,255,.82)" }}>Ela configura o atendimento de cada cliente com base fixa + ajustes operacionais</span>
            </h1>
            <p className="caption" style={{ marginTop: 14, fontSize: 15, lineHeight: 1.6 }}>
              O cliente ativo agora e <strong>{config.tenantName}</strong>. A base principal continua igual para todos.
              O que muda por cliente sao dados obrigatorios, regras do atendimento, CRM, follow-up e ativos comerciais.
            </p>
            <div className="hero-actions" style={{ marginTop: 18 }}>
              <span className="hero-chip"><Icon.layers /> Base fixa da SATI</span>
              <span className="hero-chip"><Icon.spark /> Modelo base reutilizavel</span>
              <span className="hero-chip"><Icon.building /> Ajuste por cliente</span>
              <span className="hero-chip"><Icon.database /> Saida para o Facilita</span>
            </div>
          </div>
          <div className="card card--padded" style={{ background: "rgba(255,255,255,.96)" }}>
            <div className="section-title" style={{ marginBottom: 12 }}>
              <div>
                <h3 style={{ margin: 0 }}>O que este cliente usa hoje</h3>
                <div className="section-subtitle">Leitura rapida para produto, operacao ou comercial.</div>
              </div>
            </div>
            <div className="pill-row">
              <span className="config-chip active">Cliente: {config.tenantName}</span>
              <span className="config-chip active">Modelo: {config.template}</span>
              <span className="config-chip active">Conducao: {config.strategy}</span>
              <span className="config-chip">CRM: {config.crmProvider}</span>
              <span className="config-chip">{enabledFieldCount} dados obrigatorios</span>
              <span className="config-chip">{enabledActionCount} acoes ativas</span>
            </div>
          </div>
        </div>
      </section>

      <SectionCard
        title="Clientes configurados"
        subtitle="Cada cliente nasce de um modelo base e recebe seus proprios ajustes operacionais."
        badge={{ label: "Multitenant", className: "badge--brand" }}
        actions={
          <>
            <button className="btn btn--secondary btn--sm"><Icon.spark /> Duplicar cliente</button>
            <button className="btn btn--primary btn--sm"><Icon.check /> Publicar mock</button>
          </>
        }
      >
        <TenantLibrary currentTenantId={currentTenantId} onSelect={selectTenant} />
      </SectionCard>

      <div className="top-summary">
        <RuntimeCard label="Cliente ativo" value={config.tenantName} note={`${config.city} - ${config.operationType}`} />
        <RuntimeCard label="Modelo base" value={config.template.replace("_base", "")} note="Ponto de partida compartilhado" />
        <RuntimeCard label="Dados obrigatorios" value={String(enabledFieldCount)} note="Informacoes que a conversa precisa obter" />
        <RuntimeCard label="Acoes ativas" value={String(enabledActionCount)} note="O que o sistema pode fazer depois" />
      </div>

      <TabBar activeTab={activeTab} onChange={setActiveTab} />

      <div className="main-grid">
        <div className="stack">{tabContent[activeTab]}</div>

        <div className="sticky-col">
          <SectionCard
            title="Resumo do cliente"
            subtitle="Leitura rapida para gestor, operacao ou para o proprio time SATI."
            badge={{ label: "Snapshot", className: "badge--outline" }}
          >
            <div className="preview-step">
              <strong>{config.tenantName}</strong>
              <p>{config.city} - {config.operationType} - responsavel {config.owner}</p>
            </div>
            <div className="preview-step">
              <strong>Base reutilizada</strong>
              <p>{config.template} com ajuste em {config.strategy}.</p>
            </div>
            <div className="preview-step">
              <strong>Publicacao mais recente</strong>
              <p>{config.lastPublished}</p>
            </div>
            <div className="preview-step">
              <strong>Base protegida pela SATI</strong>
              <p>{ENGINE_CORE.engineVersion} - {ENGINE_CORE.stateMachineVersion} - {ENGINE_CORE.queueModel}</p>
            </div>
          </SectionCard>

          <SectionCard
            title="O que voce ajusta e o que fica fixo"
            subtitle="Atalho conceitual para nao voltar ao pensamento de bloquinhos."
            badge={{ label: "Regra mental", className: "badge--brand" }}
          >
            <div className="detail-list">
              <div>
                <strong>Voce pode ajustar</strong>
                <ul>
                  <li>modelo e conducao do cliente</li>
                  <li>dados obrigatorios</li>
                  <li>thresholds e follow-up</li>
                  <li>mapeamento do Facilita</li>
                  <li>pacote de imagens e alguns textos</li>
                </ul>
              </div>
              <div>
                <strong>Fica fixo na SATI</strong>
                <ul>
                  <li>estrutura das etapas da conversa</li>
                  <li>catalogo central de acoes</li>
                  <li>regras de seguranca do prompt</li>
                  <li>outbox e fila logica</li>
                  <li>criterios de pausa e retomada</li>
                </ul>
              </div>
            </div>
          </SectionCard>

          <SectionCard
            title="Configuracao gerada"
            subtitle="Representacao do que poderia sair dessa tela para banco ou API."
            badge={{ label: "JSON", className: "badge--outline" }}
          >
            <div className="mono-box">{JSON.stringify(generatedConfig, null, 2)}</div>
          </SectionCard>
        </div>
      </div>
    </>
  );
}
