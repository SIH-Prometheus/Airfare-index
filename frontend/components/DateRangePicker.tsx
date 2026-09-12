// components/DateRangePicker.tsx — simple start/end date input pair

interface Props {
  startDate: string;
  endDate:   string;
  onChange:  (start: string, end: string) => void;
}

export default function DateRangePicker({ startDate, endDate, onChange }: Props) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <label className="flex items-center gap-2 text-sm">
        <span className="text-[var(--muted)] font-medium">From</span>
        <input
          type="date"
          value={startDate}
          onChange={(e) => onChange(e.target.value, endDate)}
          className="rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-1.5 text-sm text-[var(--text)] focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
      </label>
      <label className="flex items-center gap-2 text-sm">
        <span className="text-[var(--muted)] font-medium">To</span>
        <input
          type="date"
          value={endDate}
          onChange={(e) => onChange(startDate, e.target.value)}
          className="rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-1.5 text-sm text-[var(--text)] focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
      </label>
    </div>
  );
}
