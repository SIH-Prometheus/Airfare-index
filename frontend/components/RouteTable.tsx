"use client";

// components/RouteTable.tsx — sortable route index table

import { useState } from "react";
import type { RouteDetail } from "@/types";

interface Props {
  routes: RouteDetail[];
}

type SortKey = "origin" | "current_index" | "wow_change" | "weight";

export default function RouteTable({ routes }: Props) {
  const [sortKey, setSortKey]   = useState<SortKey>("current_index");
  const [sortAsc, setSortAsc]   = useState(false);

  const sorted = [...routes].sort((a, b) => {
    const av = a[sortKey] as number | string;
    const bv = b[sortKey] as number | string;
    if (typeof av === "string") return sortAsc ? av.localeCompare(bv as string) : (bv as string).localeCompare(av);
    return sortAsc ? (av as number) - (bv as number) : (bv as number) - (av as number);
  });

  const onSort = (key: SortKey) => {
    if (key === sortKey) setSortAsc(!sortAsc);
    else { setSortKey(key); setSortAsc(false); }
  };

  const Th = ({ label, k }: { label: string; k: SortKey }) => (
    <th
      className="px-4 py-3 text-left text-xs font-semibold text-[var(--muted)] uppercase tracking-wide cursor-pointer select-none hover:text-[var(--text)] transition-colors"
      onClick={() => onSort(k)}
    >
      {label} {sortKey === k ? (sortAsc ? "↑" : "↓") : ""}
    </th>
  );

  return (
    <div className="card overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="border-b border-[var(--border)]">
          <tr>
            <Th label="Route"         k="origin" />
            <Th label="Current Index" k="current_index" />
            <Th label="WoW Change"    k="wow_change" />
            <Th label="Weight"        k="weight" />
          </tr>
        </thead>
        <tbody className="divide-y divide-[var(--border)]">
          {sorted.map((r) => (
            <tr key={r.id} className="table-row-hover">
              <td className="px-4 py-3 font-medium">
                <span className="font-mono text-brand-600">{r.origin}</span>
                <span className="mx-1 text-[var(--muted)]">→</span>
                <span className="font-mono text-brand-600">{r.destination}</span>
              </td>
              <td className="px-4 py-3 font-semibold">
                {r.current_index.toFixed(2)}
              </td>
              <td className="px-4 py-3">
                <span
                  className={`badge ${
                    r.wow_change >= 0
                      ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300"
                      : "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300"
                  }`}
                >
                  {r.wow_change >= 0 ? "▲" : "▼"} {Math.abs(r.wow_change).toFixed(2)}%
                </span>
              </td>
              <td className="px-4 py-3 text-[var(--muted)]">
                {(r.weight * 100).toFixed(0)}%
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
