/**
 * HomePage - landing institucional da Sati IA.
 * Copy oficial extraida de "Sati IA - Marketing + Qualificacao JAN26.pdf".
 * Ver vault: 01 - Contexto/Copy Oficial - Site e Marketing.md
 */

type HomePageProps = {
  onOpenLogin: () => void;
};

export function HomePage({ onOpenLogin }: HomePageProps) {
  return (
    <div className="brand-surface">
      <div className="b-shell">
        {/* ======================== TOPBAR ======================== */}
        <header className="b-topbar">
          <div className="b-container b-topbar-inner">
            <a className="b-logo" href="#top">
              <img src="/logo-sati-dark-bg.png" alt="Sati" />
            </a>

            <nav className="b-topnav">
              <a href="#problema">Problema</a>
              <a href="#solucao">Solução</a>
              <a href="#metodologia">Metodologia</a>
              <a href="#case">Case</a>
              <a href="#proposta">Proposta</a>
            </nav>

            <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
              <a href="https://wa.me/551148630701" target="_blank" rel="noreferrer" className="b-btn b-btn--ghost b-btn--sm">
                Falar no WhatsApp
              </a>
              <button type="button" className="b-btn b-btn--primary b-btn--sm" onClick={onOpenLogin}>
                Entrar
              </button>
            </div>
          </div>
        </header>

        {/* ======================== HERO ======================== */}
        <section className="b-hero" id="top">
          <div className="b-container b-hero-inner">
            <div>
              <span className="b-kicker">
                <span className="dot" />
                IA para vendas imobiliárias
              </span>

              <h1>
                O elo que faltava entre <span className="b-grad-text">marketing e vendas</span>
              </h1>

              <p className="b-lede">
                Pela primeira vez, sua mídia paga aprende com cada atendimento — e cada real
                investido retorna em mais resultados para sua empresa.
              </p>

              <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                <a
                  href="https://wa.me/551148630701"
                  target="_blank"
                  rel="noreferrer"
                  className="b-btn b-btn--grad b-btn--lg"
                >
                  Experimente a IA agora
                </a>
                <a href="#metodologia" className="b-btn b-btn--ghost b-btn--lg">
                  Ver como funciona
                </a>
              </div>

              <div className="b-tagline">Clareza · Coerência · Conversão</div>
            </div>

            <div style={{ display: "grid", gap: 14 }}>
              <div className="b-stat">
                <div className="v grad">9h33</div>
                <div className="k">Tempo médio de resposta no mercado imobiliário hoje. Lead esfria, mídia vai pro ralo.</div>
              </div>
              <div className="b-stat">
                <div className="v grad">23,8%</div>
                <div className="k">Dos leads gerados por campanhas nunca recebem resposta. Você está pagando por quem nunca foi atendido.</div>
              </div>
              <div className="b-stat" style={{ borderColor: "rgba(34,211,238,0.35)", boxShadow: "0 0 30px rgba(34,211,238,0.15)" }}>
                <div className="v" style={{ color: "#22d3ee" }}>&lt; 3 segundos</div>
                <div className="k">Tempo de resposta da Sati IA, 24 horas por dia, 7 dias por semana.</div>
              </div>
            </div>
          </div>
        </section>

        {/* ======================== PROBLEMA ======================== */}
        <section className="b-section" id="problema">
          <div className="b-container">
            <div className="b-section-head">
              <span className="b-eyebrow">O que acontece hoje no seu comercial</span>
              <h2>Sem integração, o ciclo se quebra</h2>
              <p>
                Leads cada vez mais caros. Atendimento lento e manual que perde oportunidades.
                Marketing sem retorno automático do que acontece com cada lead. Resultado: campanhas
                que não aprendem, performance que estagna, investimento desperdiçado.
              </p>
            </div>

            <div className="b-pillars">
              <div className="b-pillar">
                <span className="num">01</span>
                <h4>Lead esfria</h4>
                <p>Em 9h33 a janela de interesse já fechou. Quem chega depois é só ruído.</p>
              </div>
              <div className="b-pillar">
                <span className="num">02</span>
                <h4>Mídia desperdiçada</h4>
                <p>Cada lead não atendido é dinheiro de Meta Ads e Google Ads jogado fora.</p>
              </div>
              <div className="b-pillar">
                <span className="num">03</span>
                <h4>Campanhas no escuro</h4>
                <p>Sem dados de qualificação voltando, a otimização vira chute do gestor.</p>
              </div>
              <div className="b-pillar">
                <span className="num">04</span>
                <h4>Corretor sobrecarregado</h4>
                <p>Vendedor caçando lead frio em vez de atender quem está pronto pra comprar.</p>
              </div>
            </div>
          </div>
        </section>

        {/* ======================== SOLUÇÃO / ANTES DEPOIS ======================== */}
        <section className="b-section" id="solucao" style={{ background: "rgba(255,255,255,0.015)" }}>
          <div className="b-container">
            <div className="b-section-head">
              <span className="b-eyebrow">A virada</span>
              <h2>E se cada lead fosse respondido em segundos?</h2>
            </div>

            <div className="b-vs">
              <div className="b-vs-col">
                <span className="b-vs-tag">Antes — mercado hoje</span>
                <h3>Sem Sati</h3>
                <ul>
                  <li><span className="mark x">×</span><span><strong>9h33</strong> para responder o primeiro contato</span></li>
                  <li><span className="mark x">×</span><span><strong>23%</strong> dos leads sem resposta</span></li>
                  <li><span className="mark x">×</span><span>Conversão travada em <strong>12%</strong></span></li>
                  <li><span className="mark x">×</span><span>Corretor priorizando lead errado</span></li>
                  <li><span className="mark x">×</span><span>Campanhas sem retorno qualitativo</span></li>
                </ul>
              </div>

              <div className="b-vs-col b-vs-col--hot">
                <span className="b-vs-tag">Depois — com Sati IA</span>
                <h3>Com Sati</h3>
                <ul>
                  <li><span className="mark v">✓</span><span>Resposta imediata <strong>24/7</strong> no WhatsApp</span></li>
                  <li><span className="mark v">✓</span><span><strong>100%</strong> dos leads atendidos</span></li>
                  <li><span className="mark v">✓</span><span>Conversão sobe para <strong>25%</strong></span></li>
                  <li><span className="mark v">✓</span><span>Corretor recebe só lead qualificado</span></li>
                  <li><span className="mark v">✓</span><span>Mídia paga otimizada por dados reais de venda</span></li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* ======================== CASE ======================== */}
        <section className="b-section" id="case">
          <div className="b-container">
            <div className="b-section-head">
              <span className="b-eyebrow">Case real</span>
              <h2>Em 1 mês de operação</h2>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 18, marginBottom: 56 }} className="b-case-grid">
              <div className="b-stat">
                <div className="v grad">4.233</div>
                <div className="k">Leads atendidos pela IA, sem fila, sem horário comercial.</div>
              </div>
              <div className="b-stat">
                <div className="v grad">1.049</div>
                <div className="k">Agendamentos confirmados — sem intervenção humana.</div>
              </div>
              <div className="b-stat">
                <div className="v grad">12 → 25%</div>
                <div className="k">Salto de conversão, com o mesmo investimento em mídia.</div>
              </div>
            </div>

            <div className="b-quote">
              <blockquote>
                "Estamos impressionados com a velocidade dos resultados! O produto estava parado,
                e agora temos um fluxo constante de leads qualificados e visitas agendadas."
              </blockquote>
              <cite>Thiago — Diretor Comercial</cite>
            </div>
          </div>
        </section>

        {/* ======================== METODOLOGIA ======================== */}
        <section className="b-section" id="metodologia" style={{ background: "rgba(255,255,255,0.015)" }}>
          <div className="b-container">
            <div className="b-section-head">
              <span className="b-eyebrow">Nossa metodologia</span>
              <h2>O ciclo virtuoso da performance</h2>
              <p>
                Campanhas geram leads. A IA atende, qualifica e agenda em segundos. O CRM recebe
                tudo organizado. Os dados voltam pro marketing — e as campanhas ficam mais
                inteligentes a cada semana.
              </p>
            </div>

            <div className="b-pillars">
              <div className="b-pillar">
                <span className="num">CENÁRIO ATUAL</span>
                <h4>Diagnóstico</h4>
                <p>
                  Análise do processo e da integração entre marketing e vendas. Estudo do público
                  do próximo lançamento.
                </p>
              </div>
              <div className="b-pillar">
                <span className="num">MÍDIA PAGA</span>
                <h4>Geração</h4>
                <p>
                  Gestão de campanhas Meta Ads e Google Ads, otimizadas por agendamentos e vendas —
                  não só por cliques.
                </p>
              </div>
              <div className="b-pillar">
                <span className="num">PRÉ-VENDAS</span>
                <h4>Atendimento</h4>
                <p>
                  Atendimento ágil 24/7 pelo WhatsApp. Qualificação com foco em agendamento.
                  Follow-up, prospecção e atuação no CRM.
                </p>
              </div>
              <div className="b-pillar">
                <span className="num">DADOS + IA</span>
                <h4>Otimização</h4>
                <p>
                  IA analisa cada conversa, classifica o lead, retroalimenta as campanhas e cria
                  públicos qualificados.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ======================== O QUE ISSO SIGNIFICA ======================== */}
        <section className="b-section" id="resultados">
          <div className="b-container">
            <div className="b-section-head b-section-head--left">
              <span className="b-eyebrow">O que isso significa para sua empresa</span>
              <h2>Mais tempo pra vender, menos tempo caçando lead</h2>
            </div>

            <div className="b-pillars">
              <div className="b-card">
                <div className="b-card-icon"><IconBriefcase /></div>
                <h3>Mais agendamentos</h3>
                <p>Visitas ao stand entram na agenda dos corretores automaticamente, todos os dias.</p>
              </div>
              <div className="b-card">
                <div className="b-card-icon"><IconHandshake /></div>
                <h3>Mais contratos fechados</h3>
                <p>Corretor recebe lead pronto, com resumo da conversa e contexto comercial completo.</p>
              </div>
              <div className="b-card">
                <div className="b-card-icon"><IconTrendingUp /></div>
                <h3>ROI visível em cada campanha</h3>
                <p>Cada real investido em mídia retorna em dado, em conversa qualificada e em venda.</p>
              </div>
              <div className="b-card">
                <div className="b-card-icon"><IconBolt /></div>
                <h3>Até duplicar as vendas</h3>
                <p>Mesmo investimento de mídia, resposta imediata, qualificação automática. A conta fecha.</p>
              </div>
            </div>
          </div>
        </section>

        {/* ======================== PROPOSTA ======================== */}
        <section className="b-section" id="proposta" style={{ background: "rgba(255,255,255,0.015)" }}>
          <div className="b-container">
            <div className="b-section-head">
              <span className="b-eyebrow">Proposta</span>
              <h2>Um time de IA + mídia, por menos que um corretor</h2>
            </div>

            <div style={{ maxWidth: 720, margin: "0 auto" }}>
              <div
                className="b-card"
                style={{
                  padding: 48,
                  background: "linear-gradient(180deg, rgba(139,92,246,0.10), rgba(34,211,238,0.04))",
                  borderColor: "rgba(139,92,246,0.40)",
                }}
              >
                <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", flexWrap: "wrap", gap: 16, marginBottom: 28 }}>
                  <div>
                    <div style={{ fontSize: 13, color: "#a78bfa", fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 6 }}>
                      Mensalidade
                    </div>
                    <div style={{ fontFamily: "var(--b-font-display)", fontSize: 56, fontWeight: 700, lineHeight: 1, letterSpacing: "-0.03em" }}>
                      R$ 1.500<span style={{ fontSize: 22, color: "var(--b-text-muted)", fontWeight: 400 }}>/mês</span>
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: 13, color: "var(--b-text-muted)", fontWeight: 500, marginBottom: 6 }}>
                      Implantação única
                    </div>
                    <div style={{ fontFamily: "var(--b-font-display)", fontSize: 28, fontWeight: 600 }}>
                      R$ 3.500
                    </div>
                  </div>
                </div>

                <div style={{ borderTop: "1px solid var(--b-border-subtle)", paddingTop: 24, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
                  <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 12 }}>
                    <li style={{ display: "flex", gap: 10, fontSize: 14, color: "var(--b-text-muted)" }}>
                      <span style={{ color: "var(--b-success)" }}>✓</span> 1 Agente de IA dedicado
                    </li>
                    <li style={{ display: "flex", gap: 10, fontSize: 14, color: "var(--b-text-muted)" }}>
                      <span style={{ color: "var(--b-success)" }}>✓</span> Qualificação + Agendamento + Follow-up
                    </li>
                    <li style={{ display: "flex", gap: 10, fontSize: 14, color: "var(--b-text-muted)" }}>
                      <span style={{ color: "var(--b-success)" }}>✓</span> Plataforma de Atendimento (3 usuários)
                    </li>
                    <li style={{ display: "flex", gap: 10, fontSize: 14, color: "var(--b-text-muted)" }}>
                      <span style={{ color: "var(--b-success)" }}>✓</span> Integração com seu CRM
                    </li>
                    <li style={{ display: "flex", gap: 10, fontSize: 14, color: "var(--b-text-muted)" }}>
                      <span style={{ color: "var(--b-success)" }}>✓</span> Relatórios de Performance
                    </li>
                  </ul>
                  <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 12 }}>
                    <li style={{ display: "flex", gap: 10, fontSize: 14, color: "var(--b-text-muted)" }}>
                      <span style={{ color: "var(--b-success)" }}>✓</span> Gestão de Mídia Paga (Meta + Google)
                    </li>
                    <li style={{ display: "flex", gap: 10, fontSize: 14, color: "var(--b-text-muted)" }}>
                      <span style={{ color: "var(--b-success)" }}>✓</span> Planejamento e otimização contínua
                    </li>
                    <li style={{ display: "flex", gap: 10, fontSize: 14, color: "var(--b-text-muted)" }}>
                      <span style={{ color: "var(--b-success)" }}>✓</span> Públicos qualificados a partir das conversas
                    </li>
                    <li style={{ display: "flex", gap: 10, fontSize: 14, color: "var(--b-text-muted)" }}>
                      <span style={{ color: "var(--b-success)" }}>✓</span> Conversões enviadas para Meta + Google
                    </li>
                    <li style={{ display: "flex", gap: 10, fontSize: 14, color: "var(--b-text-muted)" }}>
                      <span style={{ color: "var(--b-success)" }}>✓</span> Relatórios consolidados
                    </li>
                  </ul>
                </div>

                <div style={{ marginTop: 28, fontSize: 12, color: "var(--b-text-faint)", lineHeight: 1.6 }}>
                  Custo de mensagens pela API do WhatsApp é de responsabilidade do cliente.
                  Mensalidade válida para orçamento de mídia de até R$ 10.000.
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ======================== CTA FINAL ======================== */}
        <section className="b-section" style={{ borderBottom: "none" }}>
          <div className="b-container">
            <div className="b-cta-band">
              <span className="b-eyebrow">Próximo passo</span>
              <h2>Pronto pra elevar a performance de vendas da sua empresa?</h2>
              <div className="b-cta-actions">
                <a
                  href="https://wa.me/551148630701"
                  target="_blank"
                  rel="noreferrer"
                  className="b-btn b-btn--grad b-btn--lg"
                >
                  Iniciar conversa em 11 4863-0701
                </a>
                <button type="button" className="b-btn b-btn--ghost b-btn--lg" onClick={onOpenLogin}>
                  Já sou cliente — entrar
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* ======================== FOOTER ======================== */}
        <footer className="b-footer">
          <div className="b-container b-footer-inner">
            <div className="b-logo" style={{ opacity: 0.6 }}>
              <img src="/logo-sati-dark-bg.png" alt="Sati" />
            </div>
            <div>Sati IA · 2026 · Clareza. Coerência. Conversão.</div>
            <div>
              <a href="https://wa.me/551148630701">11 4863-0701</a>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}

/* ---- Inline icons (small, scoped) ---- */
function IconBriefcase() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="7" width="18" height="13" rx="2" />
      <path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2" />
    </svg>
  );
}
function IconHandshake() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <path d="M11 17l-2-2 4-4 5 5-2 2-3-3-2 2z" />
      <path d="M14 6l4 4M3 13l4-4 3 3" />
    </svg>
  );
}
function IconTrendingUp() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="3 17 9 11 13 15 21 7" />
      <polyline points="14 7 21 7 21 14" />
    </svg>
  );
}
function IconBolt() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
    </svg>
  );
}
