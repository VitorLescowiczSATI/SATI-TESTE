import { TENANT_PRESETS } from "../data/runtimeConfig";

export function TenantLibrary({
  currentTenantId,
  onSelect,
}: {
  currentTenantId: string;
  onSelect: (tenantId: string) => void;
}) {
  const tenants = Object.values(TENANT_PRESETS);

  return (
    <div className="tenant-grid">
      {tenants.map((tenant) => (
        <button
          key={tenant.id}
          type="button"
          className={`tenant-card ${currentTenantId === tenant.id ? "active" : ""}`}
          onClick={() => onSelect(tenant.id)}
        >
          <div className="tenant-card-head">
            <strong>{tenant.tenantName}</strong>
            <span className={`badge ${currentTenantId === tenant.id ? "badge--brand" : "badge--neutral"}`}>{tenant.operationType}</span>
          </div>
          <div className="tenant-card-meta">{tenant.city} · {tenant.strategy}</div>
          <div className="tenant-card-meta">Publicacao: {tenant.lastPublished}</div>
          <div className="tenant-card-meta">Owner: {tenant.owner}</div>
        </button>
      ))}
    </div>
  );
}
