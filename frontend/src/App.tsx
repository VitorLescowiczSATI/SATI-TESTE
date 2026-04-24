import { useMemo, useState } from "react";
import { AppShell } from "./components/AppShell";
import { LoginPage } from "./features/auth/LoginPage";
import { useSession } from "./features/auth/useSession";
import { DashboardPage } from "./pages/DashboardPage";
import { HomePage } from "./pages/HomePage";
import { InboxPage } from "./pages/InboxPage";
import type { AppViewKey } from "./types";

const PAGE_META: Record<AppViewKey, { title: string; subtitle: string }> = {
  dashboard: {
    title: "Dashboard",
    subtitle: "Primeira leitura real da operacao, baseada no que ja entrou pelo backend.",
  },
  playground: {
    title: "Playground",
    subtitle: "Ambiente de teste para acompanhar mensagens reais e validar a Maju.",
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
        return <DashboardPage session={session} onOpenPlayground={() => setActiveView("playground")} />;
      case "playground":
        return <InboxPage />;
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
