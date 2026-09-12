"use client";

// components/AlertBanner.tsx — colour-coded alert banner with explainable AI details

import type { AlertCurrentResponse, AlertSeverity } from "@/types";

const SEVERITY_CONFIG: Record<
  AlertSeverity,
  { bg: string; border: string; icon: string; text: string; headerBg: string }
> = {
  NORMAL: {
    bg:     "bg-emerald-50 dark:bg-emerald-900/20",
    headerBg: "bg-emerald-100 dark:bg-emerald-900/40",
    border: "border-emerald-400",
    icon:   "✅",
    text:   "text-emerald-700 dark:text-emerald-300",
  },
  WATCH: {
    bg:     "bg-yellow-50 dark:bg-yellow-900/20",
    headerBg: "bg-yellow-100 dark:bg-yellow-900/40",
    border: "border-yellow-400",
    icon:   "⚠️",
    text:   "text-yellow-700 dark:text-yellow-300",
  },
  ELEVATED: {
    bg:     "bg-orange-50 dark:bg-orange-900/20",
    headerBg: "bg-orange-100 dark:bg-orange-900/40",
    border: "border-orange-500",
    icon:   "🔶",
    text:   "text-orange-700 dark:text-orange-300",
  },
  HIGH: {
    bg:     "bg-red-50 dark:bg-red-900/20",
    headerBg: "bg-red-100 dark:bg-red-900/40",
    border: "border-red-600",
    icon:   "🚨",
    text:   "text-red-700 dark:text-red-300",
  },
};

interface Props {
  alert: AlertCurrentResponse;
}

export default function AlertBanner({ alert }: Props) {
  const cfg = SEVERITY_CONFIG[alert.severity] ?? SEVERITY_CONFIG.NORMAL;

  return (
    <div className={`card overflow-hidden p-0 border-l-4 ${cfg.border} ${cfg.bg}`}>
      {/* Header */}
      <div className={`flex items-center gap-3 px-5 py-3 ${cfg.headerBg} border-b border-[var(--border)]`}>
        <span className="text-2xl">{cfg.icon}</span>
        <h2 className={`font-bold uppercase tracking-wider ${cfg.text}`}>
          AIRFARE INFLATION ALERT
        </h2>
      </div>

      <div className="p-5 grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* Left Column: Top Level Metrics */}
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <Metric label="APIx" value={alert.apix_value.toFixed(2)} />
            <Metric 
              label="Weekly change" 
              value={`${alert.wow_change >= 0 ? "+" : ""}${alert.wow_change.toFixed(1)}%`} 
              highlight={alert.wow_change >= 10}
            />
            <Metric label="Alert" value={alert.severity} className={`font-bold ${cfg.text}`} />
          </div>

          <div className="pt-4 border-t border-[var(--border)] grid grid-cols-2 gap-4">
            <Metric label="ML anomaly score" value={alert.anomaly_score.toFixed(2)} />
            <Metric label="Z-score" value={alert.z_score.toFixed(1)} highlight={alert.z_score > 2} />
          </div>
        </div>

        {/* Right Column: Explainability */}
        <div className="space-y-6">
          
          {/* Main Contributors */}
          <div>
            <h3 className="text-xs font-bold text-[var(--muted)] tracking-wider mb-3">MAIN CONTRIBUTORS</h3>
            <div className="space-y-2">
              {alert.contributors_detail?.map((c) => (
                <div key={c.route} className="flex justify-between items-center text-sm">
                  <span className="font-mono text-[var(--text)] font-medium">
                    {c.route.replace("-", " → ")}
                  </span>
                  <span className={`font-semibold ${c.contribution > 0 ? 'text-red-500' : 'text-emerald-500'}`}>
                    {c.contribution > 0 ? "+" : ""}{c.contribution.toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Lead-Time Pressure */}
          <div>
            <h3 className="text-xs font-bold text-[var(--muted)] tracking-wider mb-3">LEAD-TIME PRESSURE</h3>
            <div className="space-y-2">
              {alert.lead_time_pressure && Object.entries(alert.lead_time_pressure).map(([lt, val]) => (
                <div key={lt} className="flex justify-between items-center text-sm">
                  <span className="font-mono text-[var(--text)] font-medium">{lt}</span>
                  <span className={`font-semibold ${val > 10 ? 'text-red-500' : 'text-[var(--text)]'}`}>
                    {val > 0 ? "+" : ""}{val.toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>

      {/* Footer Message */}
      <div className={`px-5 py-3 border-t border-[var(--border)] bg-black/5 dark:bg-white/5`}>
        <p className={`text-sm font-semibold italic ${cfg.text}`}>
          {alert.message}
        </p>
      </div>

    </div>
  );
}

function Metric({ label, value, highlight, className }: { label: string; value: string; highlight?: boolean; className?: string }) {
  return (
    <div>
      <p className="text-sm text-[var(--muted)] mb-1">{label}</p>
      <p className={`text-lg font-semibold ${highlight ? 'text-red-500' : 'text-[var(--text)]'} ${className || ''}`}>
        {value}
      </p>
    </div>
  );
}
