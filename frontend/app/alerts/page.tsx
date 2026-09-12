"use client";

// app/alerts/page.tsx — Alerts page: current banner + history table with filters

import { useEffect, useState } from "react";
import AlertBanner from "@/components/AlertBanner";
import { alertsApi } from "@/services/api";
import type { AlertCurrentResponse, AlertHistoryResponse, AlertSeverity } from "@/types";

const SEVERITIES: AlertSeverity[] = ["NORMAL", "WATCH", "ELEVATED", "HIGH"];

const SEVERITY_BADGE: Record<AlertSeverity, string> = {
  NORMAL:   "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300",
  WATCH:    "bg-yellow-100  text-yellow-700  dark:bg-yellow-900/30  dark:text-yellow-300",
  ELEVATED: "bg-orange-100  text-orange-700  dark:bg-orange-900/30  dark:text-orange-300",
  HIGH:     "bg-red-100     text-red-700     dark:bg-red-900/30     dark:text-red-300",
};

export default function AlertsPage() {
  const [current,  setCurrent]  = useState<AlertCurrentResponse  | null>(null);
  const [history,  setHistory]  = useState<AlertHistoryResponse  | null>(null);
  const [severity, setSeverity] = useState<string>("");
  const [loading,  setLoading]  = useState(true);

  useEffect(() => {
    alertsApi.getCurrent().then(setCurrent);
  }, []);

  useEffect(() => {
    setLoading(true);
    alertsApi
      .getHistory({ severity: severity || undefined })
      .then(setHistory)
      .finally(() => setLoading(false));
  }, [severity]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Alerts</h1>
        <p className="text-sm text-[var(--muted)]">
          Current alert status and historical alert records
        </p>
      </div>

      {/* Current Alert */}
      {current && <AlertBanner alert={current} />}

      {/* Severity breakdown cards */}
      {history && <SeverityBreakdown items={history.items} />}

      {/* Filter */}
      <div className="flex flex-wrap items-center gap-3">
        <span className="text-sm font-medium text-[var(--muted)]">Filter by severity:</span>
        <button
          onClick={() => setSeverity("")}
          className={`badge cursor-pointer ${severity === "" ? "bg-brand-600 text-white" : "bg-slate-100 dark:bg-slate-800 text-[var(--text)]"}`}
        >
          All
        </button>
        {SEVERITIES.map((s) => (
          <button
            key={s}
            onClick={() => setSeverity(s)}
            className={`badge cursor-pointer ${severity === s ? "bg-brand-600 text-white" : SEVERITY_BADGE[s]}`}
          >
            {s}
          </button>
        ))}
      </div>

      {/* History Table */}
      <div className="card overflow-x-auto">
        <h2 className="text-base font-semibold mb-4">
          Alert History {history ? `(${history.total})` : ""}
        </h2>
        {loading ? (
          <div className="h-40 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg" />
        ) : (
          <table className="w-full text-sm">
            <thead className="border-b border-[var(--border)]">
              <tr>
                {["Date", "Severity", "Score", "WoW %", "Z-Score", "Anomaly", "APIx"].map((h) => (
                  <th
                    key={h}
                    className="px-3 py-2 text-left text-xs font-semibold text-[var(--muted)] uppercase"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border)]">
              {history?.items.map((a) => (
                <tr key={a.id} className="table-row-hover">
                  <td className="px-3 py-2.5 text-[var(--muted)]">
                    {new Date(a.created_at).toLocaleDateString("en-IN")}
                  </td>
                  <td className="px-3 py-2.5">
                    <span className={`badge ${SEVERITY_BADGE[a.severity]}`}>
                      {a.severity}
                    </span>
                  </td>
                  <td className="px-3 py-2.5 font-semibold">{a.score.toFixed(2)}</td>
                  <td className="px-3 py-2.5">
                    <span
                      className={a.wow_change >= 0 ? "text-red-500" : "text-emerald-500"}
                    >
                      {a.wow_change >= 0 ? "+" : ""}{a.wow_change.toFixed(2)}%
                    </span>
                  </td>
                  <td className="px-3 py-2.5">{a.z_score.toFixed(2)}</td>
                  <td className="px-3 py-2.5">{(a.anomaly_score * 100).toFixed(1)}%</td>
                  <td className="px-3 py-2.5">{a.apix_value.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function SeverityBreakdown({ items }: { items: { severity: AlertSeverity }[] }) {
  const counts = SEVERITIES.reduce(
    (acc, s) => ({ ...acc, [s]: items.filter((a) => a.severity === s).length }),
    {} as Record<AlertSeverity, number>
  );

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      {SEVERITIES.map((s) => (
        <div key={s} className={`card border-l-4 ${BORDER_MAP[s]}`}>
          <p className="text-2xl font-bold">{counts[s]}</p>
          <p className={`text-xs font-semibold uppercase mt-1 ${TEXT_MAP[s]}`}>{s}</p>
        </div>
      ))}
    </div>
  );
}

const BORDER_MAP: Record<AlertSeverity, string> = {
  NORMAL:   "border-emerald-400",
  WATCH:    "border-yellow-400",
  ELEVATED: "border-orange-500",
  HIGH:     "border-red-600",
};
const TEXT_MAP: Record<AlertSeverity, string> = {
  NORMAL:   "text-emerald-600 dark:text-emerald-400",
  WATCH:    "text-yellow-600 dark:text-yellow-400",
  ELEVATED: "text-orange-600 dark:text-orange-400",
  HIGH:     "text-red-600 dark:text-red-400",
};
