"use client";

// app/app/page.tsx — TradingView Style Chart Dashboard

import { useEffect, useState } from "react";
import TvTopBar from "@/components/TvTopBar";
import TvLeftBar from "@/components/TvLeftBar";
import TvRightBar from "@/components/TvRightBar";
import TvBottomPanel from "@/components/TvBottomPanel";
import TrendChart from "@/components/TrendChart";
import { indexApi, alertsApi, routesApi, faresApi } from "@/services/api";
import type {
  IndexHistoryResponse,
  AlertCurrentResponse,
  RouteListResponse,
  AlertHistoryResponse,
  FareListResponse
} from "@/types";

export default function AppPage() {
  const [apixHistory,   setApixHistory]   = useState<IndexHistoryResponse | null>(null);
  const [alert,         setAlert]         = useState<AlertCurrentResponse | null>(null);
  const [alertHistory,  setAlertHistory]  = useState<AlertHistoryResponse | null>(null);
  const [routes,        setRoutes]        = useState<RouteListResponse | null>(null);
  const [fares,         setFares]         = useState<FareListResponse | null>(null);
  const [loading,       setLoading]       = useState(true);
  const [error,         setError]         = useState<string | null>(null);

  useEffect(() => {
    // Force dark mode for TV look
    document.documentElement.classList.add("dark");
    localStorage.setItem("theme", "dark");

    Promise.all([
      indexApi.getHistory(),
      alertsApi.getCurrent(),
      alertsApi.getHistory(),
      routesApi.list(),
      faresApi.list({ limit: 50 })
    ])
      .then(([hist, al, alHist, rt, fr]) => {
        setApixHistory(hist);
        setAlert(al);
        setAlertHistory(alHist);
        setRoutes(rt);
        setFares(fr);
      })
      .catch((e) => setError(e.message ?? "Failed to load data"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="flex-1 w-full h-screen bg-tv-bg flex items-center justify-center text-tv-text">
      <div className="flex flex-col items-center gap-4">
        <div className="w-8 h-8 border-4 border-tv-blue border-t-transparent rounded-full animate-spin" />
        <p className="font-semibold tracking-widest text-sm">LOADING PROMETHEUS</p>
      </div>
    </div>
  );

  if (error) return (
    <div className="flex-1 w-full h-screen bg-tv-bg flex items-center justify-center p-4">
      <div className="bg-red-900/20 border border-red-500/50 p-6 rounded text-red-400 max-w-md w-full text-center">
        <h2 className="font-bold text-lg mb-2">⚠ API Connection Error</h2>
        <p className="text-sm mb-3">{error}</p>
        <p className="text-xs text-[var(--muted)]">Make sure the FastAPI backend is running:</p>
        <code className="text-xs bg-black/40 px-3 py-1 rounded mt-1 block">
          uvicorn prometheus.api.main:app --reload --port 8000
        </code>
      </div>
    </div>
  );

  return (
    <div className="flex flex-col w-full h-screen bg-tv-bg text-tv-text overflow-hidden font-sans">
      <TvTopBar />

      <div className="flex flex-1 overflow-hidden">
        <TvLeftBar />

        <div className="flex-1 flex flex-col min-w-0 h-full border-r border-[var(--border)]">
          {/* Main Chart Area */}
          <div className="flex-1 relative flex flex-col bg-tv-bg overflow-hidden p-2">
            <div className="absolute top-3 left-4 z-10 flex gap-3 items-end select-none pointer-events-none">
              <span className="text-xl font-bold text-[var(--text)]">APIx</span>
              <span className="text-xs font-semibold text-[var(--muted)] mb-0.5">Airfare Price Index · India</span>
              {alert && (
                <>
                  <span className="text-xl font-bold text-white mb-0.5">
                    {alert.apix_value.toFixed(2)}
                  </span>
                  <span className={`text-sm font-semibold mb-0.5 ${alert.wow_change >= 0 ? "text-[#f23645]" : "text-[#089981]"}`}>
                    {alert.wow_change >= 0 ? "▲ +" : "▼ "}{alert.wow_change.toFixed(2)}%
                  </span>
                </>
              )}
            </div>

            {apixHistory && (
              <div className="flex-1 w-full mt-8">
                <TrendChart
                  series={[{ name: "APIx", data: apixHistory.items, color: "#2962ff" }]}
                  height={0}
                />
              </div>
            )}
          </div>

          <TvBottomPanel fares={fares?.items ?? []} alerts={alertHistory} />
        </div>

        <TvRightBar routes={routes?.items ?? []} alert={alert} />
      </div>
    </div>
  );
}
