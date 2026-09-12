import type { RouteDetail, AlertCurrentResponse } from "@/types";

interface Props {
  routes: RouteDetail[];
  alert: AlertCurrentResponse | null;
}

export default function TvRightBar({ routes, alert }: Props) {
  return (
    <div className="w-[320px] border-l border-[var(--border)] bg-[var(--surface)] flex flex-col shrink-0 h-full overflow-hidden">
      {/* Watchlist Header */}
      <div className="px-5 py-4 border-b border-[var(--border)]">
        <h2 className="font-bold text-sm text-[var(--text)]">Watchlist & Details</h2>
      </div>

      {/* Routes List */}
      <div className="flex-1 overflow-y-auto border-b border-[var(--border)]">
        <div className="grid grid-cols-[3fr,2fr,2fr] px-5 py-3 text-xs font-semibold text-[var(--muted)] bg-[var(--bg)]">
          <span>Symbol</span>
          <span className="text-right">Last</span>
          <span className="text-right">Chg%</span>
        </div>
        {routes.map(r => (
          <div key={r.id} className="grid grid-cols-[3fr,2fr,2fr] px-5 py-2.5 text-xs hover:bg-[var(--border)] cursor-pointer transition-colors border-b border-[var(--border)]/30">
            <span className="font-bold text-[var(--text)]">{r.origin}-{r.destination}</span>
            <span className="text-right font-mono">{r.current_index.toFixed(2)}</span>
            <span className={`text-right font-mono font-semibold ${r.wow_change >= 0 ? 'text-tv-up' : 'text-tv-down'}`}>
              {r.wow_change >= 0 ? "+" : ""}{r.wow_change.toFixed(2)}%
            </span>
          </div>
        ))}
      </div>

      {/* Alert Summary Panel */}
      <div className="h-1/3 flex flex-col p-5 bg-gradient-to-br from-black/5 to-transparent dark:from-white/5 dark:to-transparent">
        <h3 className="text-xs font-bold text-[var(--muted)] mb-4 tracking-wide uppercase">Current Alert</h3>
        {alert ? (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-xs font-medium text-[var(--muted)]">Severity</span>
              <span className={`text-xs font-bold px-3 py-1 rounded-full ${
                alert.severity === 'HIGH' ? 'bg-red-500/20 text-red-500 border border-red-500/30' :
                alert.severity === 'ELEVATED' ? 'bg-orange-500/20 text-orange-500 border border-orange-500/30' :
                alert.severity === 'WATCH' ? 'bg-yellow-500/20 text-yellow-500 border border-yellow-500/30' :
                'bg-emerald-500/20 text-emerald-500 border border-emerald-500/30'
              }`}>
                {alert.severity}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs font-medium text-[var(--muted)]">Z-Score</span>
              <span className="text-xs font-mono font-semibold text-[var(--text)]">{alert.z_score.toFixed(2)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs font-medium text-[var(--muted)]">ML Anomaly</span>
              <span className="text-xs font-mono font-semibold text-[var(--text)]">{alert.anomaly_score.toFixed(2)}</span>
            </div>
            <p className="text-xs mt-3 text-[var(--muted)] leading-relaxed border-t border-[var(--border)] pt-3">
              {alert.message}
            </p>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-xs text-[var(--muted)]">
            Loading...
          </div>
        )}
      </div>
    </div>
  );
}
