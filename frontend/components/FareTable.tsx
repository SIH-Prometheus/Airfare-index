"use client";

// components/FareTable.tsx — paginated fare observations table

import type { FareObservation } from "@/types";

interface Props {
  fares:    FareObservation[];
  total:    number;
  page:     number;
  pages:    number;
  onPage:   (p: number) => void;
}

export default function FareTable({ fares, total, page, pages, onPage }: Props) {
  return (
    <div className="card">
      {/* Count */}
      <p className="text-xs text-[var(--muted)] mb-3">{total} observations total</p>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="border-b border-[var(--border)]">
            <tr>
              {[
                "Airline", "Route", "Obs. Date", "Dep. Date",
                "Advance", "Base", "Taxes", "Total",
              ].map((h) => (
                <th
                  key={h}
                  className="px-3 py-3 text-left text-xs font-semibold text-[var(--muted)] uppercase tracking-wide"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--border)]">
            {fares.map((f) => (
              <tr key={f.id} className="table-row-hover">
                <td className="px-3 py-2.5">
                  <span className="badge bg-brand-50 dark:bg-brand-900/20 text-brand-600 font-mono">
                    {f.airline_code}
                  </span>{" "}
                  {f.airline}
                </td>
                <td className="px-3 py-2.5 font-mono text-brand-500">
                  {f.origin}→{f.destination}
                </td>
                <td className="px-3 py-2.5 text-[var(--muted)]">{f.observation_date}</td>
                <td className="px-3 py-2.5 text-[var(--muted)]">{f.departure_date}</td>
                <td className="px-3 py-2.5">
                  <span className="badge bg-slate-100 dark:bg-slate-800 text-[var(--text)]">
                    T+{f.advance_days}
                  </span>
                </td>
                <td className="px-3 py-2.5">₹{f.base_fare.toLocaleString("en-IN")}</td>
                <td className="px-3 py-2.5 text-[var(--muted)]">₹{f.taxes.toLocaleString("en-IN")}</td>
                <td className="px-3 py-2.5 font-semibold">
                  ₹{f.total_fare.toLocaleString("en-IN")}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between mt-4 pt-4 border-t border-[var(--border)]">
        <p className="text-xs text-[var(--muted)]">
          Page {page} of {pages}
        </p>
        <div className="flex gap-2">
          <button
            onClick={() => onPage(page - 1)}
            disabled={page <= 1}
            className="btn-ghost text-sm disabled:opacity-40"
          >
            ← Prev
          </button>
          <button
            onClick={() => onPage(page + 1)}
            disabled={page >= pages}
            className="btn-ghost text-sm disabled:opacity-40"
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  );
}
