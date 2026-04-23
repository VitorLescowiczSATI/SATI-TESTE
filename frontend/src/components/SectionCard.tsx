import type { SectionCardProps } from "../types";

export function SectionCard({ title, subtitle, badge, actions, children }: SectionCardProps) {
  return (
    <section className="card card--padded">
      <div className="section-title">
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <h3>{title}</h3>
            {badge ? <span className={`badge ${badge.className || "badge--brand"}`}>{badge.label}</span> : null}
          </div>
          {subtitle ? <div className="section-subtitle">{subtitle}</div> : null}
        </div>
        {actions ? <div style={{ display: "flex", gap: 8 }}>{actions}</div> : null}
      </div>
      {children}
    </section>
  );
}
