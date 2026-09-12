import { useState } from "react";
import type { FareObservation, AlertHistoryResponse } from "@/types";

interface Props {
  fares: FareObservation[];
  alerts: AlertHistoryResponse | null;
}

export default function TvBottomPanel({ fares, alerts }: Props) {
  const [tab, setTab] = useState<"Fares" | "Alerts">("Fares");

  return (
    <div className="h-[220px] border-t border-[var(--border)] bg-[var(--surface)] flex flex-col shrink-0 w-full overflow-hidden">
      {/* Tabs */}
      <div className="flex items-center gap-6 px-5 pt-3 border-b border-[var(--border)]">
        {["Fares", "Alerts"].map(t => (
          <button
            key={t}
            onClick={() => setTab(t as any)}
            className={`pb-3 text-xs font-semibold transition-colors ${tab === t 
              ? "text-tv-blue border-b-2 border-tv-blue" 
              : "text-[var(--muted)] hover:text-[var(--text)]"}`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {tab === "Fares" && (
          <table className="w-full text-xs text-left">
            <thead className="sticky top-0 bg-[var(--surface)] border-b border-[var(--border)] text-[var(--muted)]">
              <tr>
                <th className="px-5 py-2.5 font-normal">Date</th>
                <th className="px-5 py-2.5 font-normal">Route</th>
                <th className="px-5 py-2.5 font-normal">Airline</th>
                <th className="px-5 py-2.5 font-normal text-right">Total Fare</th>
              </tr>
            </thead>
            <tbody>
              {fares.slice(0, 20).map(f => (
                <tr key={f.id} className="hover:bg-[var(--border)] transition-colors border-b border-[var(--border)]/30">
                  <td className="px-5 py-2 text-[var(--text)]">{f.observation_date}</td>
                  <td className="px-5 py-2 font-bold text-tv-blue">{f.origin}-{f.destination}</td>
                  <td className="px-5 py-2">{f.airline}</td>
                  <td className="px-5 py-2 font-mono text-tv-text text-right">₹{f.total_fare.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {tab === "Alerts" && alerts && (
          <table className="w-full text-xs text-left">
            <thead className="sticky top-0 bg-[var(--surface)] border-b border-[var(--border)] text-[var(--muted)]">
              <tr>
                <th className="px-5 py-2.5 font-normal">Date</th>
                <th className="px-5 py-2.5 font-normal">Severity</th>
                <th className="px-5 py-2.5 font-normal text-right">Z-Score</th>
                <th className="px-5 py-2.5 font-normal text-right">WoW%</th>
              </tr>
            </thead>
            <tbody>
              {alerts.items.map(a => (
                <tr key={a.id} className="hover:bg-[var(--border)] transition-colors border-b border-[var(--border)]/30">
                  <td className="px-5 py-2 text-[var(--text)]">{new Date(a.created_at).toLocaleDateString()}</td>
                  <td className={`px-5 py-2 font-bold ${
                    a.severity === 'HIGH' ? 'text-tv-down' : 
                    a.severity === 'ELEVATED' ? 'text-orange-500' :
                    a.severity === 'WATCH' ? 'text-yellow-500' :
                    'text-tv-up'
                  }`}>{a.severity}</td>
                  <td className="px-5 py-2 font-mono text-right">{a.z_score.toFixed(2)}</td>
                  <td className={`px-5 py-2 font-mono text-right ${a.wow_change >= 0 ? 'text-tv-up' : 'text-tv-down'}`}>
                    {a.wow_change >= 0 ? "+" : ""}{a.wow_change.toFixed(2)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
