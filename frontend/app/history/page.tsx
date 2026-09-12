"use client";

// app/history/page.tsx — Index History page with date range picker + multi-route chart

import { useEffect, useState, useCallback } from "react";
import DateRangePicker from "@/components/DateRangePicker";
import TrendChart      from "@/components/TrendChart";
import { indexApi, routesApi } from "@/services/api";
import type { IndexHistoryResponse, RouteListResponse, IndexValue } from "@/types";

// Default: last 30 days
function defaultDates(): { start: string; end: string } {
  const end   = new Date();
  const start = new Date();
  start.setDate(start.getDate() - 30);
  return {
    start: start.toISOString().slice(0, 10),
    end:   end.toISOString().slice(0, 10),
  };
}

export default function HistoryPage() {
  const [dates,    setDates]    = useState(defaultDates);
  const [apix,     setApix]     = useState<IndexHistoryResponse | null>(null);
  const [routes,   setRoutes]   = useState<RouteListResponse | null>(null);
  const [routeIdx, setRouteIdx] = useState<Record<number, IndexValue[]>>({});
  const [loading,  setLoading]  = useState(true);

  const fetchData = useCallback(
    async (start: string, end: string) => {
      setLoading(true);
      try {
        const [apixData, routeData] = await Promise.all([
          indexApi.getHistory({ start_date: start, end_date: end }),
          routesApi.list(),
        ]);
        setApix(apixData);
        setRoutes(routeData);

        // Fetch per-route index
        const routeIndexMap: Record<number, IndexValue[]> = {};
        await Promise.all(
          routeData.items.map(async (r) => {
            const rh = await indexApi.getRouteHistory(r.id, {
              start_date: start,
              end_date: end,
            });
            routeIndexMap[r.id] = rh.items;
          })
        );
        setRouteIdx(routeIndexMap);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  useEffect(() => {
    fetchData(dates.start, dates.end);
  }, []);  // eslint-disable-line react-hooks/exhaustive-deps

  const handleDateChange = (start: string, end: string) => {
    setDates({ start, end });
    fetchData(start, end);
  };

  const routeSeries =
    routes?.items.map((r, i) => ({
      name:  `${r.origin}→${r.destination}`,
      data:  routeIdx[r.id] ?? [],
      color: ROUTE_COLORS[i % ROUTE_COLORS.length],
    })) ?? [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Index History</h1>
          <p className="text-sm text-[var(--muted)]">
            APIx historical values and per-route comparison
          </p>
        </div>
        <DateRangePicker
          startDate={dates.start}
          endDate={dates.end}
          onChange={handleDateChange}
        />
      </div>

      {loading && <Skeleton />}

      {!loading && apix && (
        <>
          {/* APIx Chart */}
          <div className="card">
            <h2 className="text-base font-semibold mb-4">
              APIx — {apix.total} data points
            </h2>
            <TrendChart
              series={[{ name: "APIx", data: apix.items }]}
              height={300}
            />
          </div>

          {/* Route Comparison */}
          <div className="card">
            <h2 className="text-base font-semibold mb-4">
              Route Index Comparison
            </h2>
            <TrendChart
              series={routeSeries}
              height={340}
              showLegend
            />
          </div>

          {/* Stats table */}
          <div className="card overflow-x-auto">
            <h2 className="text-base font-semibold mb-4">Period Statistics</h2>
            <table className="w-full text-sm">
              <thead className="border-b border-[var(--border)]">
                <tr>
                  {["Route", "Start", "End", "Change", "Min", "Max"].map((h) => (
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
                {routes?.items.map((r) => {
                  const data = routeIdx[r.id] ?? [];
                  if (!data.length) return null;
                  const first  = data[0].index_value;
                  const last   = data[data.length - 1].index_value;
                  const change = ((last - first) / first) * 100;
                  const min    = Math.min(...data.map((d) => d.index_value));
                  const max    = Math.max(...data.map((d) => d.index_value));
                  return (
                    <tr key={r.id} className="table-row-hover">
                      <td className="px-3 py-2 font-mono font-medium text-brand-600">
                        {r.origin}→{r.destination}
                      </td>
                      <td className="px-3 py-2">{first.toFixed(2)}</td>
                      <td className="px-3 py-2">{last.toFixed(2)}</td>
                      <td className="px-3 py-2">
                        <span
                          className={`badge ${
                            change >= 0
                              ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300"
                              : "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300"
                          }`}
                        >
                          {change >= 0 ? "▲" : "▼"} {Math.abs(change).toFixed(2)}%
                        </span>
                      </td>
                      <td className="px-3 py-2 text-[var(--muted)]">{min.toFixed(2)}</td>
                      <td className="px-3 py-2 text-[var(--muted)]">{max.toFixed(2)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

function Skeleton() {
  return (
    <div className="space-y-4">
      {[300, 340].map((h, i) => (
        <div
          key={i}
          className="card animate-pulse bg-slate-100 dark:bg-slate-800"
          style={{ height: h }}
        />
      ))}
    </div>
  );
}

const ROUTE_COLORS = [
  "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6",
];
