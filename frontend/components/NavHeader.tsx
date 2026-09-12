"use client";

// components/NavHeader.tsx — responsive navigation header

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useDarkMode } from "@/components/DarkModeProvider";

const NAV_LINKS = [
  { href: "/",        label: "Dashboard" },
  { href: "/history", label: "Index History" },
  { href: "/alerts",  label: "Alerts" },
  { href: "/fares",   label: "Fares" },
];

export default function NavHeader() {
  const pathname = usePathname();
  const { dark, toggle } = useDarkMode();

  return (
    <header className="sticky top-0 z-40 border-b border-[var(--border)] bg-[var(--surface)] shadow-sm">
      <div className="container mx-auto max-w-7xl px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl font-bold text-brand-600">⚡ PROMETHEUS</span>
            <span className="hidden sm:block text-xs text-[var(--muted)] font-mono mt-1">
              Airfare Price Index
            </span>
          </Link>

          {/* Nav links */}
          <nav className="hidden md:flex items-center gap-1">
            {NAV_LINKS.map(({ href, label }) => {
              const active = pathname === href;
              return (
                <Link
                  key={href}
                  href={href}
                  className={`rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                    active
                      ? "bg-brand-50 dark:bg-brand-900/20 text-brand-600"
                      : "text-[var(--muted)] hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-[var(--text)]"
                  }`}
                >
                  {label}
                </Link>
              );
            })}
          </nav>

          {/* Dark mode toggle */}
          <button
            onClick={toggle}
            className="btn-ghost rounded-lg p-2"
            aria-label="Toggle dark mode"
          >
            {dark ? "☀️" : "🌙"}
          </button>
        </div>
      </div>
    </header>
  );
}
