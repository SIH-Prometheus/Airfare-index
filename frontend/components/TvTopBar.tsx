"use client";
import Link from "next/link";
import { useDarkMode } from "@/components/DarkModeProvider";

export default function TvTopBar() {
  const { dark, toggle } = useDarkMode();
  const [symbol, setSymbol] = useState("APIx");
  const [tf, setTf] = useState("1D");

  return (
    <div className="h-14 border-b border-[var(--border)] bg-[var(--surface)] flex items-center px-5 justify-between shrink-0">
      {/* Left side: Logo & Symbol */}
      <div className="flex items-center gap-6 h-full">
        <Link href="/" className="font-bold text-xl text-tv-blue tracking-tight flex items-center gap-2">
          <span className="text-2xl">⚡</span>
          <span>PROMETHEUS</span>
        </Link>
        
        <div className="flex items-center gap-3 border-l border-[var(--border)] pl-6 h-3/4">
          <button className="font-bold text-lg hover:text-tv-blue transition-colors px-3 py-1.5 rounded hover:bg-[var(--border)]">
            {symbol}
          </button>
          <div className="flex items-center gap-1 font-semibold text-xs">
            {["1D", "1W", "1M", "3M", "1Y"].map(t => (
              <button 
                key={t}
                onClick={() => setTf(t)}
                className={`px-3 py-1.5 rounded transition-colors ${tf === t ? 'text-tv-blue bg-tv-blue/10' : 'text-[var(--muted)] hover:text-[var(--text)] hover:bg-[var(--border)]'}`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>
        
        <div className="flex items-center gap-2 border-l border-[var(--border)] pl-6 h-3/4">
          <button className="px-4 py-1.5 rounded text-xs font-semibold text-[var(--muted)] hover:text-[var(--text)] hover:bg-[var(--border)] transition-colors flex items-center gap-2">
            <span className="text-sm">ƒx</span> Indicators
          </button>
          <button className="px-4 py-1.5 rounded text-xs font-semibold text-[var(--muted)] hover:text-[var(--text)] hover:bg-[var(--border)] transition-colors flex items-center gap-2">
            <span className="text-sm">🚨</span> Alerts
          </button>
        </div>
      </div>

      {/* Right side: Tools */}
      <div className="flex items-center gap-3">
        <button className="px-4 py-2 bg-tv-blue hover:bg-tv-blueHover text-white rounded-lg font-semibold text-xs transition-colors shadow-lg shadow-tv-blue/20">
          Publish
        </button>
        <button
          onClick={toggle}
          className="p-2 rounded-lg text-[var(--muted)] hover:text-[var(--text)] hover:bg-[var(--border)] transition-colors"
          aria-label="Toggle dark mode"
        >
          {dark ? "☀️" : "🌙"}
        </button>
      </div>
    </div>
  );
}
