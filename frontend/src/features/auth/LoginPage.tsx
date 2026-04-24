/**
 * LoginPage - entrada para o app autenticado.
 * Visual: brand dark (Sati Design System oficial).
 * Apos submit, usuario passa do dark vibrant para o light B2B operacional.
 */

import { useState } from "react";
import type { DemoSession } from "../../types";

type LoginPageProps = {
  onBack: () => void;
  onLogin: (email: string, password: string) => Promise<DemoSession>;
};

export function LoginPage({ onBack, onLogin }: LoginPageProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!email.trim() || !password.trim()) {
      setError("Preencha email e senha pra continuar.");
      return;
    }

    setError("");
    setLoading(true);

    try {
      await onLogin(email, password);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Nao foi possivel entrar.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="brand-surface">
      <div className="b-shell">
        <div className="b-login">
          {/* ======================== Lado esquerdo: pitch ======================== */}
          <aside className="b-login-pitch">
            <div className="b-logo">
              <img src="/logo-sati-dark-bg.png" alt="Sati" />
            </div>

            <div>
              <span className="b-eyebrow">Plataforma de atendimento</span>
              <p className="b-login-quote">
                Cada lead respondido em segundos.
                <br />
                Cada conversa virando agendamento.
                <br />
                Cada real de mídia voltando em venda.
              </p>
            </div>

            <div className="b-login-pitch-foot">
              <span>Clareza · Coerência · Conversão</span>
              <span style={{ opacity: 0.5 }}>·</span>
              <span>satiia.com.br</span>
            </div>
          </aside>

          {/* ======================== Lado direito: form ======================== */}
          <main className="b-login-form">
            <button type="button" className="b-login-back" onClick={onBack} aria-label="Voltar">
              ← Voltar pro site
            </button>

            <h1>Entrar na sua operação</h1>
            <p className="lede">
              Acesse a plataforma da sua imobiliária pra acompanhar atendimentos, leads
              qualificados e agendamentos em tempo real.
            </p>

            <form onSubmit={handleSubmit}>
              <div className="b-field">
                <label htmlFor="login-email">Email</label>
                <input
                  id="login-email"
                  className="b-input"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="voce@suaempresa.com.br"
                />
              </div>

              <div className="b-field">
                <label htmlFor="login-password">Senha</label>
                <input
                  id="login-password"
                  className="b-input"
                  type="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Sua senha"
                />
              </div>

              {error ? <div className="b-alert">{error}</div> : null}

              <button
                type="submit"
                className="b-btn b-btn--grad b-btn--lg"
                style={{ width: "100%", marginTop: 12 }}
                disabled={loading}
              >
                {loading ? "Entrando..." : "Entrar"}
              </button>
            </form>

            <div
              style={{
                marginTop: 28,
                paddingTop: 24,
                borderTop: "1px solid var(--b-border-subtle)",
                fontSize: 13,
                color: "var(--b-text-muted)",
                display: "flex",
                justifyContent: "space-between",
                gap: 12,
                flexWrap: "wrap",
              }}
            >
              <span>Ainda não é cliente?</span>
              <a
                href="https://wa.me/551148630701"
                target="_blank"
                rel="noreferrer"
                style={{ color: "var(--b-purple-300)", fontWeight: 600 }}
              >
                Falar com a Sati no WhatsApp →
              </a>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
