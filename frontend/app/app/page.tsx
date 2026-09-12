"use client";

/**
 * app/app/page.tsx — PROMETHEUS MVP Dashboard
 * DEL → BOM Airfare Price Index (APIx)
 *
 * Pipeline: Next.js → POST /api/scrape → FastAPI → Scraper → MinIO → ETL → PostgreSQL → Index → here
 */

import dynamic from "next/dynamic";
import { useCallback, useEffect, useRef, useState } from "react";
import { mvpApi } from "@/services/api";
import type {
  AirfareIndexResponse,
  TrendPoint,
  AirlineFare,
  ScrapeResponse,
  ScrapeMetrics,
} from "@/types";

// ── ECharts: dynamic import to avoid SSR window errors ───────────────────────
const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

// ── Helpers ───────────────────────────────────────────────────────────────────

function inr(amount: number): string {
  return `₹${Math.round(amount).toLocaleString("en-IN")}`;
}

// ── Sub-components ────────────────────────────────────────────────────────────

function DataSourceBadge({ source }: { source: string }) {
  const isLive = source === "live";
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${
        isLive
          ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
          : "bg-amber-500/15 text-amber-400 border-amber-500/30"
      }`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${isLive ? "bg-emerald-400 animate-pulse" : "bg-amber-400"}`} />
      {isLive ? "Live" : "Sample Fallback"}
    </span>
  );
}

function MetricCard({
  label,
  value,
  sub,
  accent = false,
}: {
  label: string;
  value: string;
  sub?: string;
  accent?: boolean;
}) {
  return (
    <div
      className={`rounded-2xl p-5 border flex flex-col gap-1.5 ${
        accent
          ? "bg-gradient-to-br from-blue-600/20 to-indigo-600/10 border-blue-500/30"
          : "bg-[#131722] border-[#1e2235]"
      }`}
    >
      <p className="text-[11px] font-semibold uppercase tracking-widest text-[#787b86]">
        {label}
      </p>
      <p className={`text-3xl font-black leading-none ${accent ? "text-white" : "text-white"}`}>
        {value}
      </p>
      {sub && (
        <p className="text-[11px] text-[#787b86] mt-0.5">{sub}</p>
      )}
    </div>
  );
}

// ── Pipeline Flow ─────────────────────────────────────────────────────────────

type StepStatus = "ok" | "error" | "pending" | "running";

const STEPS: Array<{ key: keyof ScrapeResponse["pipeline"]; label: string; icon: string }> = [
  { key: "scraper",    label: "Scraper",    icon: "🔍" },
  { key: "minio",      label: "MinIO",      icon: "🗄" },
  { key: "postgresql", label: "PostgreSQL", icon: "🐘" },
  { key: "index",      label: "APIx Index", icon: "📊" },
];

function PipelineFlow({
  pipeline,
  isRunning,
}: {
  pipeline: ScrapeResponse["pipeline"] | null;
  isRunning: boolean;
}) {
  return (
    <div className="flex items-center gap-0 w-full">
      {STEPS.map((step, i) => {
        let status: StepStatus = "pending";
        if (pipeline) {
          const raw = pipeline[step.key] as string;
          status = isRunning && raw === "pending" ? "running" : (raw as StepStatus);
        }

        const colors: Record<StepStatus, string> = {
          ok:      "border-emerald-500/60 bg-emerald-500/10 text-emerald-400",
          error:   "border-red-500/60 bg-red-500/10 text-red-400",
          running: "border-blue-500/60 bg-blue-500/10 text-blue-400",
          pending: "border-[#2a2e39] bg-[#1a1e2a] text-[#787b86]",
        };

        return (
          <div key={step.key} className="flex items-center flex-1 min-w-0">
            {/* Step circle */}
            <div className="flex flex-col items-center flex-shrink-0">
              <div
                className={`w-12 h-12 rounded-full border-2 flex items-center justify-center text-lg ${colors[status]} ${
                  status === "running" ? "animate-pulse" : ""
                }`}
              >
                {status === "ok"      ? "✓"
                 : status === "error" ? "✗"
                 : step.icon}
              </div>
              <p className="text-[10px] text-[#b2b5be] mt-1 whitespace-nowrap">{step.label}</p>
            </div>
            {/* Arrow to next step */}
            {i < STEPS.length - 1 && (
              <div className="flex-1 h-px bg-gradient-to-r from-[#2a2e39] to-[#2a2e39] mx-2" />
            )}
          </div>
        );
      })}
    </div>
  );
}

// ── Trend Chart ───────────────────────────────────────────────────────────────

function TrendChart({ data }: { data: TrendPoint[] }) {
  if (!data.length) {
    return (
      <div className="flex items-center justify-center h-full text-sm text-[#787b86]">
        No trend data yet. Click <span className="text-blue-400 mx-1 font-semibold">✦ Refresh Fares</span> to generate the first observation.
      </div>
    );
  }

  const labels = data.map((d) =>
    new Date(d.calculated_at).toLocaleTimeString("en-IN", {
      hour: "2-digit",
      minute: "2-digit",
    })
  );

  const option = {
    backgroundColor: "transparent",
    grid: { top: 44, right: 60, bottom: 28, left: 66 },
    tooltip: {
      trigger: "axis",
      backgroundColor: "#1e222d",
      borderColor: "#2a2e39",
      textStyle: { color: "#b2b5be", fontSize: 12 },
    },
    legend: {
      data: ["Avg Fare (₹)", "APIx Index"],
      textStyle: { color: "#b2b5be", fontSize: 11 },
      top: 8,
      right: 8,
    },
    xAxis: {
      type: "category",
      data: labels,
      axisLine: { lineStyle: { color: "#2a2e39" } },
      axisLabel: { color: "#787b86", fontSize: 10 },
      splitLine: { show: false },
    },
    yAxis: [
      {
        type: "value",
        name: "₹ Fare",
        nameTextStyle: { color: "#787b86", fontSize: 10 },
        axisLine: { lineStyle: { color: "#2a2e39" } },
        axisLabel: {
          color: "#787b86",
          fontSize: 10,
          formatter: (v: number) => `₹${(v / 1000).toFixed(1)}k`,
        },
        splitLine: { lineStyle: { color: "#1e2235", type: "dashed" } },
      },
      {
        type: "value",
        name: "APIx",
        nameTextStyle: { color: "#787b86", fontSize: 10 },
        axisLine: { lineStyle: { color: "#2a2e39" } },
        axisLabel: { color: "#787b86", fontSize: 10 },
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: "Avg Fare (₹)",
        type: "line",
        data: data.map((d) => d.average_fare),
        smooth: true,
        lineStyle: { color: "#2962ff", width: 2.5 },
        itemStyle: { color: "#2962ff" },
        areaStyle: {
          color: {
            type: "linear", x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: "rgba(41,98,255,0.28)" },
              { offset: 1, color: "rgba(41,98,255,0)" },
            ],
          },
        },
        yAxisIndex: 0,
        symbol: "circle",
        symbolSize: 4,
      },
      {
        name: "APIx Index",
        type: "line",
        data: data.map((d) => d.airfare_index),
        smooth: true,
        lineStyle: { color: "#26a69a", width: 2, type: "dashed" },
        itemStyle: { color: "#26a69a" },
        yAxisIndex: 1,
        symbol: "circle",
        symbolSize: 4,
      },
    ],
  };

  return (
    <ReactECharts
      option={option}
      style={{ width: "100%", height: "100%" }}
      notMerge
    />
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Main Dashboard
// ─────────────────────────────────────────────────────────────────────────────

export default function MVPDashboard() {
  const [isLoading,    setIsLoading]    = useState(false);
  const [hasError,     setHasError]     = useState(false);
  const [errorMsg,     setErrorMsg]     = useState<string | null>(null);
  const [indexData,    setIndexData]    = useState<AirfareIndexResponse | null>(null);
  const [trend,        setTrend]        = useState<TrendPoint[]>([]);
  const [scrapeResult, setScrapeResult] = useState<ScrapeResponse | null>(null);
  const [lastUpdated,  setLastUpdated]  = useState<string | null>(null);
  const busy = useRef(false);

  // On mount — try to load existing data silently
  useEffect(() => {
    (async () => {
      try {
        const [idx, tr] = await Promise.allSettled([
          mvpApi.getAirfareIndex("DEL", "BOM"),
          mvpApi.getTrend("DEL", "BOM"),
        ]);
        if (idx.status === "fulfilled") setIndexData(idx.value);
        if (tr.status === "fulfilled")  setTrend(tr.value);
      } catch {
        /* Silent — no data yet, user will click Refresh */
      }
    })();
  }, []);

  const handleRefresh = useCallback(async () => {
    if (busy.current) return;
    busy.current = true;
    setIsLoading(true);
    setHasError(false);
    setErrorMsg(null);

    try {
      const result = await mvpApi.scrape("DEL", "BOM");
      setScrapeResult(result);
      setLastUpdated(
        new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })
      );

      // Reload chart + index after scrape
      const [idx, tr] = await Promise.allSettled([
        mvpApi.getAirfareIndex("DEL", "BOM"),
        mvpApi.getTrend("DEL", "BOM"),
      ]);
      if (idx.status === "fulfilled") setIndexData(idx.value);
      if (tr.status === "fulfilled")  setTrend(tr.value);
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "Failed to reach the backend. Is FastAPI running on port 8000?";
      setHasError(true);
      setErrorMsg(msg);
    } finally {
      setIsLoading(false);
      busy.current = false;
    }
  }, []);

  // Resolved display values — prefer latest scrape result, fall back to index snapshot
  const metrics:      ScrapeMetrics | null = scrapeResult?.metrics  ?? indexData?.metrics  ?? null;
  const airlineFares: AirlineFare[]        = scrapeResult?.airline_fares ?? indexData?.airline_fares ?? [];
  const dataSource:   string | null        = scrapeResult?.data_source   ?? indexData?.data_source   ?? null;
  const pipeline                           = scrapeResult?.pipeline ?? null;

  return (
    <div className="min-h-screen bg-[#0b0e18] text-white font-sans antialiased">

      {/* ── Top Navigation Bar ───────────────────────────────────────────── */}
      <nav className="border-b border-[#1e2235] bg-[#0d1017]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <a
              href="/"
              className="font-black text-lg text-blue-400 hover:text-blue-300 transition tracking-tight"
            >
              ⚡ PROMETHEUS
            </a>
            <span className="text-[#1e2235]">|</span>
            <div>
              <p className="font-bold text-white text-sm leading-tight">
                Airfare Price Index
              </p>
              <p className="text-[11px] text-[#787b86]">
                ✈ DEL → BOM · MVP Dashboard
              </p>
            </div>
            {dataSource && <DataSourceBadge source={dataSource} />}
          </div>

          <div className="flex items-center gap-3">
            {lastUpdated && (
              <p className="text-xs text-[#787b86] hidden sm:block">
                Updated {lastUpdated}
              </p>
            )}
            <button
              id="refresh-btn"
              onClick={handleRefresh}
              disabled={isLoading}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold px-5 py-2 rounded-lg transition-all text-sm active:scale-95"
            >
              {isLoading ? (
                <>
                  <span className="w-3.5 h-3.5 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                  Scraping…
                </>
              ) : (
                <>✦ Refresh Fares</>
              )}
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-8 space-y-6">

        {/* ── Error Banner ─────────────────────────────────────────────────── */}
        {hasError && errorMsg && (
          <div className="bg-red-950/40 border border-red-500/30 rounded-xl p-4 flex gap-3 items-start">
            <span className="text-red-400 text-xl flex-shrink-0">⚠</span>
            <div>
              <p className="text-red-300 font-semibold text-sm">Pipeline error</p>
              <p className="text-red-400 text-xs mt-0.5">{errorMsg}</p>
              <p className="text-[#787b86] text-xs mt-1">
                Make sure the backend is running:{" "}
                <code className="bg-black/30 px-1 rounded text-[#b2b5be]">
                  http://localhost:8000/health
                </code>
              </p>
            </div>
          </div>
        )}

        {/* ── Headline Metric Cards ─────────────────────────────────────────── */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            label="Airfare Index (APIx)"
            value={metrics ? metrics.airfare_index.toFixed(2) : "—"}
            sub={`Baseline: ₹4,500 · Index = avg / baseline × 100`}
            accent
          />
          <MetricCard
            label="Average Fare"
            value={metrics ? inr(metrics.average_fare) : "—"}
            sub="DEL → BOM"
          />
          <MetricCard
            label="Minimum Fare"
            value={metrics ? inr(metrics.minimum_fare) : "—"}
          />
          <MetricCard
            label="Maximum Fare"
            value={metrics ? inr(metrics.maximum_fare) : "—"}
          />
        </div>

        {/* ── Main Content ──────────────────────────────────────────────────── */}
        <div className="grid grid-cols-1 xl:grid-cols-[1fr_330px] gap-6">

          {/* Left: Chart */}
          <div className="bg-[#131722] border border-[#1e2235] rounded-2xl p-5 flex flex-col">
            <div className="flex items-center justify-between mb-2">
              <h2 className="font-bold text-white text-sm">
                Average Fare &amp; APIx Trend
              </h2>
              <p className="text-xs text-[#787b86]">
                {trend.length} observation{trend.length !== 1 ? "s" : ""}
              </p>
            </div>
            <div className="flex-1 min-h-[300px]">
              <TrendChart data={trend} />
            </div>
          </div>

          {/* Right column */}
          <div className="flex flex-col gap-4">

            {/* Airline fares table */}
            <div className="bg-[#131722] border border-[#1e2235] rounded-2xl p-5 flex-1">
              <h2 className="font-bold text-white text-sm mb-4">
                Airline-wise Average Fares
              </h2>
              {airlineFares.length > 0 ? (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-[#787b86] text-[11px] uppercase tracking-wider">
                      <th className="text-left pb-2 font-semibold">Airline</th>
                      <th className="text-right pb-2 font-semibold">Avg Fare</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#1e2235]">
                    {airlineFares.map((af) => (
                      <tr
                        key={af.airline}
                        className="hover:bg-[#1a1f30] transition-colors"
                      >
                        <td className="py-2.5 flex items-center gap-2">
                          <span className="w-7 h-7 rounded-full bg-blue-600/20 text-blue-400 text-xs font-bold flex items-center justify-center flex-shrink-0">
                            {af.airline.charAt(0)}
                          </span>
                          <span className="font-medium text-white truncate">
                            {af.airline}
                          </span>
                        </td>
                        <td className="py-2.5 text-right font-bold text-white">
                          {inr(af.average_fare)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p className="text-sm text-[#787b86] text-center py-4">
                  No data yet. Click <strong className="text-blue-400">Refresh Fares</strong>.
                </p>
              )}
            </div>

            {/* Pipeline status */}
            <div className="bg-[#131722] border border-[#1e2235] rounded-2xl p-5">
              <h2 className="font-bold text-white text-sm mb-4">
                Pipeline Status
              </h2>
              <PipelineFlow pipeline={pipeline} isRunning={isLoading} />

              {scrapeResult && (
                <div className="mt-4 pt-3 border-t border-[#1e2235] grid grid-cols-2 gap-x-4 gap-y-1.5">
                  <div>
                    <p className="text-[11px] text-[#787b86]">Records inserted</p>
                    <p className="text-white font-bold text-sm">
                      {scrapeResult.metrics.etl_inserted}
                    </p>
                  </div>
                  <div>
                    <p className="text-[11px] text-[#787b86]">Sample size</p>
                    <p className="text-white font-bold text-sm">
                      {scrapeResult.metrics.sample_size} flights
                    </p>
                  </div>
                  <div className="col-span-2">
                    <p className="text-[11px] text-[#787b86]">Data source</p>
                    <p
                      className={`font-semibold text-sm ${
                        scrapeResult.data_source === "live"
                          ? "text-emerald-400"
                          : "text-amber-400"
                      }`}
                    >
                      {scrapeResult.data_source === "live"
                        ? "✓ Live scrape"
                        : "⚠ Sample fallback (live scrape blocked by Google)"}
                    </p>
                  </div>
                </div>
              )}

              {!scrapeResult && (
                <p className="text-xs text-[#787b86] mt-3">
                  Press "Refresh Fares" to run the full pipeline.
                </p>
              )}
            </div>
          </div>
        </div>

        {/* ── Footer Info Bar ───────────────────────────────────────────────── */}
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-[#787b86] border-t border-[#1e2235] pt-4">
          <span>⚡ PROMETHEUS APIx v1.0.0-mvp</span>
          <span className="text-[#1e2235]">·</span>
          <span>SIH Problem Statement 26056</span>
          <span className="text-[#1e2235]">·</span>
          <span>Formula: APIx = (Avg Fare / ₹4,500) × 100</span>
          <span className="text-[#1e2235]">·</span>
          <span className="text-amber-500/80">ML/Forecasting → Phase 2</span>
        </div>

      </main>
    </div>
  );
}
