"use client";

// app/fares/page.tsx — Fare observations page with filters + paginated table

import { useEffect, useState, useCallback } from "react";
import FareTable from "@/components/FareTable";
import { faresApi, metadataApi, routesApi } from "@/services/api";
import type { FareListResponse, Airline, RouteDetail } from "@/types";

const ADVANCE_OPTIONS = [
  { label: "All",  value: "" },
  { label: "T+1",  value: "1" },
  { label: "T+7",  value: "7" },
  { label: "T+15", value: "15" },
  { label: "T+30", value: "30" },
];

export default function FaresPage() {
  const [fares,    setFares]    = useState<FareListResponse | null>(null);
  const [airlines, setAirlines] = useState<Airline[]>([]);
  const [routes,   setRoutes]   = useState<RouteDetail[]>([]);
  const [page,     setPage]     = useState(1);
  const [loading,  setLoading]  = useState(true);

  // Filters
  const [airline,  setAirline]  = useState("");
  const [routeId,  setRouteId]  = useState("");
  const [advance,  setAdvance]  = useState("");

  const fetchFares = useCallback(
    async (pg: number) => {
      setLoading(true);
      try {
        const data = await faresApi.list({
          page:     pg,
          limit:    20,
          airline:  airline  || undefined,
          route_id: routeId  ? parseInt(routeId) : undefined,
          advance:  advance  ? parseInt(advance)  : undefined,
        });
        setFares(data);
      } finally {
        setLoading(false);
      }
    },
    [airline, routeId, advance]
  );

  // Load reference data once
  useEffect(() => {
    metadataApi.getAirlines().then(setAirlines);
    routesApi.list().then((r) => setRoutes(r.items));
  }, []);

  // Refetch when filters change
  useEffect(() => {
    setPage(1);
    fetchFares(1);
  }, [airline, routeId, advance, fetchFares]);

  const handlePage = (p: number) => {
    setPage(p);
    fetchFares(p);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Fare Observations</h1>
        <p className="text-sm text-[var(--muted)]">
          Raw scraped fare data across 3 airlines, 5 routes, T+1/7/15/30
        </p>
      </div>

      {/* Filters */}
      <div className="card flex flex-wrap gap-4">
        {/* Airline filter */}
        <div>
          <label className="block text-xs font-medium text-[var(--muted)] mb-1">Airline</label>
          <select
            value={airline}
            onChange={(e) => setAirline(e.target.value)}
            className="rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-1.5 text-sm text-[var(--text)] focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="">All Airlines</option>
            {airlines.map((a) => (
              <option key={a.id} value={a.name}>{a.name}</option>
            ))}
          </select>
        </div>

        {/* Route filter */}
        <div>
          <label className="block text-xs font-medium text-[var(--muted)] mb-1">Route</label>
          <select
            value={routeId}
            onChange={(e) => setRouteId(e.target.value)}
            className="rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-1.5 text-sm text-[var(--text)] focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="">All Routes</option>
            {routes.map((r) => (
              <option key={r.id} value={r.id}>
                {r.origin} → {r.destination}
              </option>
            ))}
          </select>
        </div>

        {/* Advance days filter */}
        <div>
          <label className="block text-xs font-medium text-[var(--muted)] mb-1">
            Advance (lead time)
          </label>
          <div className="flex gap-1">
            {ADVANCE_OPTIONS.map(({ label, value }) => (
              <button
                key={value}
                onClick={() => setAdvance(value)}
                className={`badge cursor-pointer transition-colors ${
                  advance === value
                    ? "bg-brand-600 text-white"
                    : "bg-slate-100 dark:bg-slate-800 text-[var(--text)] hover:bg-brand-50 dark:hover:bg-brand-900/20"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Table */}
      {loading ? (
        <div className="card h-64 animate-pulse bg-slate-100 dark:bg-slate-800" />
      ) : fares ? (
        <FareTable
          fares={fares.items}
          total={fares.total}
          page={fares.page}
          pages={fares.pages}
          onPage={handlePage}
        />
      ) : null}
    </div>
  );
}
