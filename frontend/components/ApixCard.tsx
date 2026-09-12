// components/ApixCard.tsx — Large KPI card for the current APIx value

import type { IndexCurrentResponse } from "@/types";

interface Props {
  data: IndexCurrentResponse;
}

function ChangeBadge({ value, label }: { value: number; label: string }) {
  const positive = value >= 0;
  return (
    <div className="flex flex-col items-center">
      <span
        className={`text-lg font-semibold ${
          positive ? "text-red-500" : "text-emerald-500"
        }`}
      >
        {positive ? "▲" : "▼"} {Math.abs(value).toFixed(2)}%
      </span>
      <span className="text-xs text-[var(--muted)]">{label}</span>
    </div>
  );
}

export default function ApixCard({ data }: Props) {
  return (
    <div className="card flex flex-col sm:flex-row items-start sm:items-center gap-6">
      {/* Main value */}
      <div className="flex-1">
        <p className="text-sm font-medium text-[var(--muted)] uppercase tracking-wide">
          Current APIx
        </p>
        <p className="text-6xl font-bold text-brand-600 leading-none mt-1">
          {data.index_value.toFixed(2)}
        </p>
        <p className="text-xs text-[var(--muted)] mt-2">
          as of {new Date(data.date).toLocaleDateString("en-IN", {
            day: "numeric",
            month: "long",
            year: "numeric",
          })}
        </p>
      </div>

      {/* Divider */}
      <div className="hidden sm:block w-px h-20 bg-[var(--border)]" />

      {/* Changes */}
      <div className="flex gap-8">
        <ChangeBadge value={data.wow_change} label="Week-over-Week" />
        <ChangeBadge value={data.mom_change} label="Month-over-Month" />
      </div>
    </div>
  );
}
