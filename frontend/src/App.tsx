import { useMemo, useState } from "react";
import { AppShell } from "./components/AppShell";
import { LoginPage } from "./features/auth/LoginPage";
import { useSession } from "./features/auth/useSession";
import { RuntimeWorkspace } from "./features/runtime/RuntimeWorkspace";
import { DashboardPage } from "./pages/DashboardPage";
import { HomePage } from "./pages/HomePage";
import { InboxPage } from "./pages/InboxPage";
import { LeadsPage } from "./pages/LeadsPage";
import { SettingsPage } from "./pages/SettingsPage";
import type { AppViewKey } from "./types";

const PAGE_META: Record<AppViewKey, { title: string; subtitle: string }> = {
  dashboard: {
    title: "Dashboard",
    subtitle: "Leads atendidos, agendamentos e tempo de resposta da sua operação em tempo real.",
  },
  inbox: {
    title: "Console WhatsApp",
    subtitle: "Mensagens reais recebidas pelo webhook antes da IA responder.",
  },
  leads: {
    title: "Leads",
    subtitle: "Sua fila de leads qualificados, com origem da mídia e prioridade para o corretor.",
  },
  runtime: {
    title: "Atendimento da IA",
    subtitle: "Como a Sati conversa com seus leads, qualifica e agenda visitas.",
  },
  settings: {
    title: "Configurações",
    subtitle: "Sua operação, equipe, WhatsApp e integração com o CRM.",
  },
};

function App() {
  const { session, status, loginWithPassword, logoutCurrentSession } = useSession();
  const [activeView, setActiveView] = useState<AppViewKey>("dashboard");
  const [publicView, setPublicView] = useState<"home" | "login">("home");

  const page = PAGE_META[activeView];

  const content = useMemo(() => {
    switch (activeView) {
      case "dashboard":
        return <DashboardPage session={session} onOpenRuntime={() => setActiveView("runtime")} />;
      case "inbox":
        return <InboxPage />;
      case "leads":
        return <LeadsPage />;
      case "runtime":
        return <RuntimeWorkspace />;
      case "settings":
        return <SettingsPage session={session} />;
      default:
        return null;
    }
  }, [activeView, session]);

  if (status === "loading") {
    return (
      <div className="brand-surface">
        <div className="b-shell">
          <div className="b-login-form" style={{ minHeight: "100vh", display: "grid", placeItems: "center" }}>
            <p className="lede">Carregando sua sessao...</p>
          </div>
        </div>
      </div>
    );
  }

  if (session === null) {
    if (publicView === "home") {
      return <HomePage onOpenLogin={() => setPublicView("login")} />;
    }

    return (
      <LoginPage
        onBack={() => setPublicView("home")}
        onLogin={async (email, password) => {
          const nextSession = await loginWithPassword(email, password);
          setPublicView("home");
          return nextSession;
        }}
      />
    );
  }

  return (
    <AppShell
      active={activeView}
      onNavigate={setActiveView}
      title={page.title}
      subtitle={page.subtitle}
      session={session}
      onLogout={async () => {
        await logoutCurrentSession();
        setActiveView("dashboard");
        setPublicView("home");
      }}
    >
      {content}
    </AppShell>
  );
}

export default App;
