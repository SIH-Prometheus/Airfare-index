import { useState } from "react";

export default function TvLeftBar() {
  const [active, setActive] = useState(0);
  
  const icons = ["✛", "〰", "🖌", "T", "⚑", "📏", "🔍"];
  
  return (
    <div className="w-14 border-r border-[var(--border)] bg-[var(--surface)] flex flex-col items-center py-3 gap-2 shrink-0 h-full">
      {icons.map((icon, i) => (
        <button
          key={i}
          onClick={() => setActive(i)}
          className={`w-10 h-10 rounded-lg flex items-center justify-center text-lg transition-all ${
            active === i 
              ? "text-tv-blue bg-tv-blue/10 shadow-sm" 
              : "text-[var(--muted)] hover:text-[var(--text)] hover:bg-[var(--border)]"
          }`}
        >
          {icon}
        </button>
      ))}
      <div className="flex-1" />
      <button className="w-10 h-10 rounded-lg flex items-center justify-center text-lg text-[var(--muted)] hover:text-red-500 hover:bg-red-500/10 transition-colors">
        🗑
      </button>
    </div>
  );
}
