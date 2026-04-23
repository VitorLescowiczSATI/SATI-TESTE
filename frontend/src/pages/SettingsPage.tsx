import { Icon } from "../components/Icons";
import { SectionCard } from "../components/SectionCard";
import type { DemoSession } from "../types";

type SettingsPageProps = {
  session: DemoSession | null;
};

/**
 * SettingsPage - configuracao da operacao do gestor.
 * Tom: linguagem do operador, sem refs internas de arquitetura.
 */
export function SettingsPage({ session }: SettingsPageProps) {
  return (
    <div className="settings-grid">
      <SectionCard
        title="Sua operação"
        subtitle="Dados da empresa e do produto que a Sati está atendendo."
        badge={{ label: "Operação", className: "badge--brand" }}
      >
        <div className="form-grid">
          <div className="field-block">
            <label>Empresa</label>
            <input className="input" value={session?.tenantName ?? "Tenda RJ"} readOnly />
          </div>
          <div className="field-block">
            <label>Praça de atuação</label>
            <input className="input" value="Rio de Janeiro" readOnly />
          </div>
          <div className="field-block">
            <label>Produto principal</label>
            <input className="input" value="MCMV · Minha Casa Minha Vida" readOnly />
          </div>
          <div className="field-block">
            <label>CRM conectado</label>
            <input className="input" value="Facilita" readOnly />
          </div>
        </div>
      </SectionCard>

      <SectionCard
        title="Sua conta"
        subtitle="Como você acessa a plataforma."
        badge={{ label: "Acesso", className: "badge--outline" }}
      >
        <div className="settings-list">
          <div className="settings-row">
            <strong>Nome</strong>
            <span>{session?.fullName ?? "—"}</span>
          </div>
          <div className="settings-row">
            <strong>Email</strong>
            <span>{session?.email ?? "—"}</span>
          </div>
          <div className="settings-row">
            <strong>Perfil</strong>
            <span>Administrador da operação</span>
          </div>
          <div className="settings-row">
            <strong>Equipe</strong>
            <span>3 usuários incluídos no plano</span>
          </div>
        </div>
      </SectionCard>

      <SectionCard
        title="Integrações"
        subtitle="Os canais e sistemas que sua operação já está conectada."
        badge={{ label: "Conectado", className: "badge--outline" }}
      >
        <div className="signal-grid">
          <div className="signal-card">
            <strong><Icon.whats /> WhatsApp</strong>
            <p>API oficial do WhatsApp Business respondendo 24/7 pela sua empresa.</p>
          </div>
          <div className="signal-card">
            <strong><Icon.building /> Facilita CRM</strong>
            <p>Cada lead qualificado chega organizado na esteira do corretor certo.</p>
          </div>
          <div className="signal-card">
            <strong><Icon.layers /> Meta Ads</strong>
            <p>Conversões e públicos qualificados retornam automaticamente para a campanha.</p>
          </div>
          <div className="signal-card">
            <strong><Icon.database /> Relatórios</strong>
            <p>Performance de mídia, atendimento e agendamentos em um só lugar.</p>
          </div>
        </div>
      </SectionCard>
    </div>
  );
}
