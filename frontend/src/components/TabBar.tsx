import { TABS } from "../data/runtimeConfig";
import type { RuntimeTabKey } from "../types";

export function TabBar({
  activeTab,
  onChange,
}: {
  activeTab: RuntimeTabKey;
  onChange: (tab: RuntimeTabKey) => void;
}) {
  return (
    <div className="tabs tabs-panel">
      {TABS.map((tab) => (
        <button
          key={tab.key}
          type="button"
          className={`tab ${activeTab === tab.key ? "active" : ""}`}
          onClick={() => onChange(tab.key)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
