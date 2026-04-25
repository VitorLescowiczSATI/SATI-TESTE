import { Icon } from "../components/Icons";
import { SectionCard } from "../components/SectionCard";

export function GuiaPage() {
  return (
    <>
      <section className="hero-panel">
        <div className="hero-grid">
          <div>
            <div className="badge badge--brand" style={{ marginBottom: 14 }}>
              Como funciona a Maju da SATI
            </div>
            <h1 style={{ margin: 0, fontSize: 30, letterSpacing: "-0.03em" }}>
              Mesma logica do Nicochat, agora rodando no nucleo da SATI.
              <br />
              <span style={{ color: "rgba(255,255,255,.82)" }}>
                Esta pagina e o seu mapa pra entender e testar.
              </span>
            </h1>
            <p className="caption" style={{ marginTop: 14, fontSize: 15, lineHeight: 1.6 }}>
              Leia uma vez aqui, depois va no Playground e converse como se fosse um lead. Cada
              passo abaixo e exatamente o que acontece nos bastidores.
            </p>
            <div className="hero-actions" style={{ marginTop: 18 }}>
              <span className="hero-chip"><Icon.spark /> GPT + tools</span>
              <span className="hero-chip"><Icon.database /> Tudo gravado no banco</span>
              <span className="hero-chip"><Icon.checkCircle /> Comportamento Nicochat</span>
            </div>
          </div>
        </div>
      </section>

      <SectionCard
        title="O pipeline em 6 passos"
        subtitle="O que acontece quando o lead manda uma mensagem (Playground ou WhatsApp real)."
        badge={{ label: "Pipeline", className: "badge--brand" }}
      >
        <div className="timeline-list">
          <div className="timeline-step">
            <span className="timeline-index">1</span>
            <div>
              <strong>Mensagem entra</strong>
              <p>
                Pelo Playground (chat in-app) ou pelo webhook do WhatsApp Cloud. A SATI grava
                o lead se for novo, ou recupera o existente pelo telefone.
              </p>
            </div>
          </div>
          <div className="timeline-step">
            <span className="timeline-index">2</span>
            <div>
              <strong>Strategy decide o "como"</strong>
              <p>
                A conversa e roteada pra <code>MCMVTendaRJStrategy</code>: o conjunto de
                regras, prompt e tools especifico do MCMV da Tenda RJ. Outras strategies
                podem coexistir no futuro.
              </p>
            </div>
          </div>
          <div className="timeline-step">
            <span className="timeline-index">3</span>
            <div>
              <strong>OpenAI responde com texto OU pede uma tool</strong>
              <p>
                A SATI manda pro GPT o prompt da Maju + historico + as 4 tools disponiveis.
                Se o GPT precisa registrar simulacao, agendamento ou material, ele pede a tool
                em vez de inventar a resposta.
              </p>
            </div>
          </div>
          <div className="timeline-step">
            <span className="timeline-index">4</span>
            <div>
              <strong>SATI executa a tool de verdade</strong>
              <p>
                A tool valida os dados (Pydantic), salva no perfil estruturado do lead
                (renda, FGTS, agendamento...) e devolve um recibo pro GPT. O GPT entao
                escreve a resposta natural pro lead.
              </p>
            </div>
          </div>
          <div className="timeline-step">
            <span className="timeline-index">5</span>
            <div>
              <strong>Resposta sai</strong>
              <p>
                No Playground aparece direto na tela. No WhatsApp, sai via WhatsApp Cloud API.
                Tudo fica gravado em <code>Message</code> com o tipo (texto ou tool_call).
              </p>
            </div>
          </div>
          <div className="timeline-step">
            <span className="timeline-index">6</span>
            <div>
              <strong>Classificacao automatica</strong>
              <p>
                A cada troca, a SATI re-classifica o lead em
                <em> frio / quente / agendado / corretor</em> com base nos sinais coletados.
                Aparece no painel lateral do Playground e no Dashboard.
              </p>
            </div>
          </div>
        </div>
      </SectionCard>

      <SectionCard
        title="Ritmo humano: debounce e splitting"
        subtitle="Igual o Nicochat: a Maju espera o lead terminar de digitar e responde em mensagens curtas."
        badge={{ label: "Comportamento", className: "badge--brand" }}
      >
        <div className="dashboard-grid">
          <div className="card card--padded">
            <strong>Espera de 7 segundos (debounce)</strong>
            <p className="caption" style={{ marginTop: 6, lineHeight: 1.6 }}>
              Quando o lead manda uma mensagem no WhatsApp, a SATI espera 7 segundos antes
              de chamar o GPT. Se o lead manda outra mensagem nesse intervalo, o timer
              reinicia. Resultado: 3 mensagens curtas em sequencia viram UMA chamada ao
              GPT, com todo o contexto junto - e a Maju nao responde por partes
              cortando o raciocinio do lead.
            </p>
            <p className="caption" style={{ marginTop: 8, fontSize: 12 }}>
              <strong>No Playground:</strong> a resposta sai imediatamente (e ambiente de
              teste, nao adianta esperar). No WhatsApp real: 7s sempre.
            </p>
          </div>
          <div className="card card--padded">
            <strong>Splitting de resposta</strong>
            <p className="caption" style={{ marginTop: 6, lineHeight: 1.6 }}>
              O prompt instrui a Maju a separar respostas em blocos de 1-2 frases curtas,
              divididos por linha em branco. A SATI le isso e envia cada bloco como uma
              mensagem WhatsApp separada, com 1.5s de pausa entre elas.
              Maximo: 3 mensagens por turno.
            </p>
            <p className="caption" style={{ marginTop: 8, fontSize: 12 }}>
              No Playground voce ve as bolhas aparecerem progressivamente, simulando o
              ritmo de digitacao.
            </p>
          </div>
        </div>
      </SectionCard>

      <SectionCard
        title="As 4 tools da Maju"
        subtitle="Cada tool e um contrato direto, sem bloquinho. Mesmas que a Maju usa hoje no Nicochat."
        badge={{ label: "Function calling", className: "badge--outline" }}
      >
        <div className="dashboard-grid">
          <div className="card card--padded">
            <strong>simula</strong>
            <p className="caption" style={{ marginTop: 6 }}>
              Registra a simulacao inicial: tipo de comprovacao de renda, uso de FGTS e renda
              familiar. E o gatilho que move o lead pra "quente".
            </p>
          </div>
          <div className="card card--padded">
            <strong>simula_completo</strong>
            <p className="caption" style={{ marginTop: 6 }}>
              Complementa com tempo de carteira, estado civil, data de nascimento e
              dependentes. Necessario pra simulacao real de credito.
            </p>
          </div>
          <div className="card card--padded">
            <strong>schedule_time</strong>
            <p className="caption" style={{ marginTop: 6 }}>
              Registra data e horario de pre-agendamento com corretor. Move o lead pra
              "agendado" automaticamente.
            </p>
          </div>
          <div className="card card--padded">
            <strong>send_media</strong>
            <p className="caption" style={{ marginTop: 6 }}>
              Envia material do empreendimento (planta, fachada, decorado). No MVP-demo
              retorna placeholder; no MVP-real puxa do bucket de midias.
            </p>
          </div>
        </div>
      </SectionCard>

      <SectionCard
        title="Como rodar a simulacao com o Aristeu"
        subtitle="Roteiro pratico de 5 minutos pra demonstrar."
        badge={{ label: "Demo", className: "badge--brand" }}
      >
        <div className="timeline-list">
          <div className="timeline-step">
            <span className="timeline-index">1</span>
            <div>
              <strong>Abra o Playground</strong>
              <p>Aba ao lado. Clique em "Novo lead de teste" pra criar um lead vazio.</p>
            </div>
          </div>
          <div className="timeline-step">
            <span className="timeline-index">2</span>
            <div>
              <strong>Comece como um lead real</strong>
              <p>
                Algo como "oi, vi um anuncio de apartamento em Madureira". A Maju vai
                responder em uma pergunta por vez, igual no Nicochat.
              </p>
            </div>
          </div>
          <div className="timeline-step">
            <span className="timeline-index">3</span>
            <div>
              <strong>Caminhe pela simulacao</strong>
              <p>
                Conte renda, FGTS, comprovacao. No momento certo a Maju chama
                <code> simula</code> e voce ve a tool aparecer no painel direito com o
                payload exato.
              </p>
            </div>
          </div>
          <div className="timeline-step">
            <span className="timeline-index">4</span>
            <div>
              <strong>Peca pra agendar</strong>
              <p>
                Quando topar uma visita, a Maju chama <code>schedule_time</code> e o lead
                vira "agendado". Painel direito atualiza na hora.
              </p>
            </div>
          </div>
          <div className="timeline-step">
            <span className="timeline-index">5</span>
            <div>
              <strong>Mostre o que mudou</strong>
              <p>
                Painel direito mostra: classificacao, perfil estruturado, function calls
                disparadas e resumo. Volte no Dashboard pra ver o KPI subiu.
              </p>
            </div>
          </div>
        </div>
      </SectionCard>

      <SectionCard
        title="O que esta dentro e o que esta fora deste demo"
        subtitle="Pra alinhar expectativa antes da call."
        badge={{ label: "Escopo", className: "badge--outline" }}
      >
        <div className="dashboard-grid">
          <div className="card card--padded">
            <strong style={{ color: "var(--brand-700)" }}>DENTRO do MVP-demo</strong>
            <ul style={{ marginTop: 10, paddingLeft: 18, lineHeight: 1.7, fontSize: 14 }}>
              <li>Conversa real com GPT + as 4 tools funcionando</li>
              <li>Persistencia de lead, conversa, mensagens e tool calls</li>
              <li>Classificacao automatica (frio/quente/agendado)</li>
              <li>Webhook de WhatsApp Cloud pronto (responde se credenciais setadas)</li>
              <li>Configuracao de prompt, modelo e tools pela aba Configuracao</li>
            </ul>
          </div>
          <div className="card card--padded">
            <strong style={{ color: "var(--text-tertiary)" }}>FORA do MVP-demo (vem depois)</strong>
            <ul style={{ marginTop: 10, paddingLeft: 18, lineHeight: 1.7, fontSize: 14 }}>
              <li>Adapter Facilita real (so preview do payload aqui)</li>
              <li>Catalogo de midias real no R2</li>
              <li>Follow-ups automaticos 15min/1h/22h</li>
              <li>HSM templates aprovados pela Meta</li>
              <li>Migracao de leads ativos do Nicochat</li>
              <li>Inbox com takeover humano</li>
            </ul>
          </div>
        </div>
      </SectionCard>
    </>
  );
}
