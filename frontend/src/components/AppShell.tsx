import type { ReactNode } from "react";
import type { AppViewKey, DemoSession } from "../types";
import { Icon, SatiLogo } from "./Icons";

type AppShellProps = {
  children: ReactNode;
  active: AppViewKey;
  onNavigate: (view: AppViewKey) => void;
  title: string;
  subtitle: string;
  session: DemoSession;
  onLogout: () => void | Promise<void>;
};

export function AppShell({
  children,
  active,
  onNavigate,
  title,
  subtitle,
  session,
  onLogout,
}: AppShellProps) {
  const items: Array<{ key: AppViewKey; label: string; iconKey: string }> = [
    { key: "dashboard", label: "Dashboard", iconKey: "home" },
    { key: "playground", label: "Playground", iconKey: "inbox" },
  ];

  const initials = session.fullName
    .split(" ")
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");

  return (
    <div className="runtime-screen">
      <div style={{ display: "flex", minHeight: "100vh" }}>
        <aside className="sidebar" style={{ width: 238 }}>
          <div className="logo">
            <SatiLogo size={24} /> SATI
            <span
              style={{
                fontSize: 10,
                fontWeight: 500,
                color: "var(--text-tertiary)",
                letterSpacing: ".1em",
                textTransform: "uppercase",
                marginLeft: 4,
              }}
            >
              IA
            </span>
          </div>

          <div className="group">MVP-demo</div>
          {items.map((item) => {
            const ItemIcon = Icon[item.iconKey];
            return (
              <button
                key={item.key}
                type="button"
                className={`item ${active === item.key ? "active" : ""}`}
                onClick={() => onNavigate(item.key)}
              >
                <ItemIcon />
                {item.label}
              </button>
            );
          })}

          <div
            style={{
              marginTop: "auto",
              padding: 14,
              border: "1px solid var(--border)",
              borderRadius: 12,
              background: "var(--gradient-brand-soft)",
            }}
          >
            <div
              style={{
                fontSize: 10,
                fontWeight: 700,
                color: "var(--brand-700)",
                letterSpacing: ".08em",
                textTransform: "uppercase",
                marginBottom: 4,
              }}
            >
              Operacao ativa
            </div>
            <div style={{ fontSize: 14, fontWeight: 700 }}>{session.tenantName}</div>
            <div className="caption" style={{ marginTop: 4 }}>
              MVP-demo em validacao
            </div>
          </div>
        </aside>

        <main style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column" }}>
          <header className="topbar">
            <div className="topbar-title">
              <strong>{title}</strong>
              <span>{subtitle}</span>
            </div>
            <div className="topbar-spacer" />
            <span className="config-chip active">
              <Icon.spark /> Playground GPT
            </span>
            <span className="config-chip">
              <Icon.building /> {session.tenantName}
            </span>
            <button className="btn btn--ghost btn--sm" onClick={onLogout}>
              <Icon.logout /> Sair
            </button>
            <div className="avatar">{initials}</div>
          </header>
          <div className="runtime-content">{children}</div>
        </main>
      </div>
    </div>
  );
}
