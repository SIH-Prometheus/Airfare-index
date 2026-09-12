"use client";

import "./landing.css";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { indexApi, routesApi, alertsApi } from "@/services/api";
import type { IndexCurrentResponse, RouteListResponse, AlertCurrentResponse } from "@/types";

/* ─── Mini spark-line using SVG ─────────────────────────────────────────── */
function SparkLine({ values, color = "#089981" }: { values: number[]; color?: string }) {
  if (!values.length) return null;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const w = 120, h = 40;
  const pts = values
    .map((v, i) => `${(i / (values.length - 1)) * w},${h - ((v - min) / range) * h}`)
    .join(" ");
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <polyline
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        points={pts}
      />
    </svg>
  );
}

/* ─── Aurora beams (hero background) ────────────────────────────────────── */
function AuroraBeams() {
  const beams = [
    { left: "18%",  delay: "0s",   dur: "7s",  color: "#2962ff", w: 2,   h: 220 },
    { left: "22%",  delay: "0.5s", dur: "9s",  color: "#a855f7", w: 1.5, h: 300 },
    { left: "26%",  delay: "1s",   dur: "6s",  color: "#2962ff", w: 1,   h: 180 },
    { left: "35%",  delay: "2s",   dur: "11s", color: "#06b6d4", w: 2,   h: 260 },
    { left: "40%",  delay: "0.3s", dur: "8s",  color: "#a855f7", w: 1,   h: 200 },
    { left: "48%",  delay: "1.5s", dur: "10s", color: "#2962ff", w: 3,   h: 350 },
    { left: "55%",  delay: "0.8s", dur: "7s",  color: "#06b6d4", w: 1.5, h: 240 },
    { left: "62%",  delay: "2.5s", dur: "9s",  color: "#a855f7", w: 1,   h: 190 },
    { left: "68%",  delay: "1.2s", dur: "6s",  color: "#2962ff", w: 2,   h: 280 },
    { left: "74%",  delay: "0.6s", dur: "8s",  color: "#06b6d4", w: 1,   h: 210 },
    { left: "80%",  delay: "3s",   dur: "11s", color: "#a855f7", w: 2.5, h: 320 },
  ];
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {beams.map((b, i) => (
        <div
          key={i}
          className="aurora-beam absolute bottom-1/3"
          style={{
            left: b.left,
            width: b.w,
            height: b.h,
            background: `linear-gradient(to top, ${b.color}cc, ${b.color}44, transparent)`,
            animationDuration: b.dur,
            animationDelay: b.delay,
            borderRadius: "999px",
            filter: `blur(${b.w * 0.5}px)`,
          }}
        />
      ))}
    </div>
  );
}

/* ─── Ticker bar ─────────────────────────────────────────────────────────── */
const TICKER_ITEMS = [
  { sym: "DEL-BOM", val: "107.42", chg: "+1.24%", up: true },
  { sym: "DEL-BLR", val: "104.88", chg: "+0.67%", up: true },
  { sym: "BOM-BLR", val: "102.10", chg: "-0.31%", up: false },
  { sym: "DEL-MAA", val: "105.55", chg: "+2.10%", up: true },
  { sym: "HYD-DEL", val: "103.22", chg: "-0.98%", up: false },
  { sym: "APIx",    val: "104.83", chg: "+0.91%", up: true },
  { sym: "IndiGo",  val: "108.12", chg: "+1.55%", up: true },
  { sym: "AirIndia",val: "101.78", chg: "-0.22%", up: false },
  { sym: "Akasa",   val: "99.34",  chg: "+0.44%", up: true },
];

function TickerBar() {
  const doubled = [...TICKER_ITEMS, ...TICKER_ITEMS];
  return (
    <div className="w-full overflow-hidden bg-[#0d1117] border-y border-[#1e2235] py-2">
      <div className="ticker-track">
        {doubled.map((t, i) => (
          <div key={i} className="flex items-center gap-1.5 px-6 text-xs shrink-0">
            <span className="font-bold text-white">{t.sym}</span>
            <span className="text-[#b2b5be] font-mono">{t.val}</span>
            <span className={`font-semibold ${t.up ? "text-[#089981]" : "text-[#f23645]"}`}>
              {t.chg}
            </span>
            <span className="text-[#2a2e39] mx-2">|</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── Nav ────────────────────────────────────────────────────────────────── */
function LandingNav() {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", fn);
    return () => window.removeEventListener("scroll", fn);
  }, []);

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? "bg-[#0b0e18]/95 backdrop-blur border-b border-[#1e2235]" : "bg-transparent"}`}>
      <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-white font-bold text-xl tracking-tight">⚡ PROMETHEUS</span>
          </Link>
          <div className="hidden md:flex items-center gap-6 text-sm text-[#b2b5be]">
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#index"    className="hover:text-white transition-colors">Index</a>
            <a href="#routes"   className="hover:text-white transition-colors">Routes</a>
            <a href="#alerts"   className="hover:text-white transition-colors">Alerts</a>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/app" className="text-sm text-[#b2b5be] hover:text-white transition-colors px-3 py-1.5">
            Sign in
          </Link>
          <Link
            href="/app"
            className="text-sm font-semibold bg-[#2962ff] hover:bg-[#1e53e5] text-white px-4 py-2 rounded-lg transition-colors"
          >
            Launch App
          </Link>
        </div>
      </div>
    </nav>
  );
}

/* ─── Route Index Card ───────────────────────────────────────────────────── */
function RouteCard({ route, sparkData }: { route: any; sparkData: number[] }) {
  const up = route.wow_change >= 0;
  return (
    <div className="glow-card bg-[#131722] rounded-xl p-4 hover:bg-[#1a1f30] transition-colors cursor-pointer">
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-[#2962ff]/20 flex items-center justify-center text-xs font-bold text-[#2962ff]">
              ✈
            </div>
            <div>
              <p className="text-sm font-bold text-white">{route.origin} → {route.destination}</p>
              <p className="text-xs text-[#787b86]">Route Index</p>
            </div>
          </div>
        </div>
        <span className={`text-xs font-semibold px-2 py-0.5 rounded ${up ? "bg-[#089981]/20 text-[#089981]" : "bg-[#f23645]/20 text-[#f23645]"}`}>
          {up ? "▲" : "▼"} {Math.abs(route.wow_change).toFixed(2)}%
        </span>
      </div>
      <div className="flex items-end justify-between">
        <div>
          <p className="text-2xl font-bold text-white animate-number-glow">
            {route.current_index.toFixed(2)}
          </p>
          <p className="text-xs text-[#787b86]">WoW change</p>
        </div>
        <SparkLine values={sparkData} color={up ? "#089981" : "#f23645"} />
      </div>
    </div>
  );
}

/* ─── Stat Pill ──────────────────────────────────────────────────────────── */
function StatPill({ icon, label, value, sub }: { icon: string; label: string; value: string; sub: string }) {
  return (
    <div className="flex flex-col gap-1 px-6 py-4 rounded-xl bg-white/5 border border-white/10 text-center">
      <span className="text-2xl">{icon}</span>
      <span className="text-2xl font-extrabold text-white">{value}</span>
      <span className="text-sm font-semibold text-[#b2b5be]">{label}</span>
      <span className="text-xs text-[#787b86]">{sub}</span>
    </div>
  );
}

/* ─── Alert Severity Badge ───────────────────────────────────────────────── */
const SEV_STYLES: Record<string, string> = {
  NORMAL:   "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  WATCH:    "bg-yellow-500/20  text-yellow-400  border-yellow-500/30",
  ELEVATED: "bg-orange-500/20  text-orange-400  border-orange-500/30",
  HIGH:     "bg-red-500/20     text-red-400     border-red-500/30",
};

/* ═══════════════════════════════════════════════════════════════════════════
   MAIN PAGE
════════════════════════════════════════════════════════════════════════════ */
export default function LandingPage() {
  const [apix, setApix]     = useState<IndexCurrentResponse | null>(null);
  const [routes, setRoutes] = useState<RouteListResponse | null>(null);
  const [alert, setAlert]   = useState<AlertCurrentResponse | null>(null);
  const [sparkData]         = useState<Record<number, number[]>>(() => {
    // deterministic pseudo-random spark data for 5 routes
    const seed = (s: number) => { let x = Math.sin(s) * 10000; return x - Math.floor(x); };
    return Object.fromEntries(
      [1, 2, 3, 4, 5].map(id => [
        id,
        Array.from({ length: 20 }, (_, i) => 100 + (seed(id * 100 + i) - 0.5) * 10),
      ])
    );
  });

  useEffect(() => {
    indexApi.getCurrent().then(setApix).catch(() => {});
    routesApi.list().then(setRoutes).catch(() => {});
    alertsApi.getCurrent().then(setAlert).catch(() => {});
  }, []);

  const mockAlerts = [
    { id: 1, route: "DEL → BOM", severity: "HIGH",     wow: "+12.7%", z: "3.2",  msg: "Near-term T+1 fares spiking sharply." },
    { id: 2, route: "DEL → BLR", severity: "ELEVATED", wow: "+8.4%",  z: "2.1",  msg: "Sustained pressure over T+7 window." },
    { id: 3, route: "HYD → DEL", severity: "WATCH",    wow: "+5.1%",  z: "1.4",  msg: "Mild WoW inflation, monitor closely." },
    { id: 4, route: "BOM → BLR", severity: "NORMAL",   wow: "+1.2%",  z: "0.3",  msg: "Prices within normal range." },
  ];

  return (
    <div className="min-h-screen bg-[#0b0e18] text-white overflow-x-hidden">
      <LandingNav />

      {/* ── HERO ─────────────────────────────────────────────────────────── */}
      <section className="relative hero-bg min-h-screen flex flex-col items-center justify-center text-center overflow-hidden">
        <AuroraBeams />

        {/* Earth glow at bottom */}
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] rounded-full"
             style={{ background: "radial-gradient(ellipse at 50% 100%, rgba(10,30,80,0.9) 0%, rgba(5,10,30,0.7) 40%, transparent 70%)", filter: "blur(40px)" }} />

        <div className="relative z-10 max-w-4xl mx-auto px-6 pt-20"
             style={{ animation: "fade-up 1s ease 0.2s both" }}>
          <div className="inline-flex items-center gap-2 text-xs font-semibold border border-[#2962ff]/40 bg-[#2962ff]/10 text-[#2962ff] rounded-full px-4 py-1.5 mb-8">
            🇮🇳 India's First Real-time Airfare Price Index
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold leading-tight mb-6 tracking-tight">
            Track First /
            <br />
            <span className="gradient-text">Then Decide.</span>
          </h1>
          <p className="text-lg md:text-xl text-[#b2b5be] mb-10 max-w-2xl mx-auto leading-relaxed">
            PROMETHEUS monitors airfare inflation across India's busiest routes in real-time.
            Powered by the <strong className="text-white">Airfare Price Index (APIx)</strong>, ML anomaly detection,
            and explainable alerts.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/app"
              className="animate-pulse-glow bg-white text-[#0b0e18] font-bold text-base px-8 py-4 rounded-xl hover:bg-[#f0f0f0] transition-all duration-200"
            >
              Launch Dashboard →
            </Link>
            <a
              href="#index"
              className="text-base font-semibold text-[#b2b5be] border border-[#2a2e39] px-8 py-4 rounded-xl hover:border-[#2962ff]/50 hover:text-white transition-all"
            >
              View Live Index ↓
            </a>
          </div>
          {apix && (
            <div className="mt-12 inline-flex items-center gap-6 bg-white/5 border border-white/10 rounded-2xl px-8 py-4 backdrop-blur">
              <div className="text-left">
                <p className="text-xs text-[#787b86] mb-1">Live APIx</p>
                <p className="text-3xl font-extrabold animate-number-glow">{apix.index_value.toFixed(2)}</p>
              </div>
              <div className="w-px h-10 bg-[#2a2e39]" />
              <div className="text-left">
                <p className="text-xs text-[#787b86] mb-1">Week-over-Week</p>
                <p className={`text-xl font-bold ${apix.wow_change >= 0 ? "text-[#f23645]" : "text-[#089981]"}`}>
                  {apix.wow_change >= 0 ? "▲ +" : "▼ "}{apix.wow_change.toFixed(2)}%
                </p>
              </div>
              <div className="w-px h-10 bg-[#2a2e39]" />
              {alert && (
                <div className="text-left">
                  <p className="text-xs text-[#787b86] mb-1">Alert Status</p>
                  <span className={`text-sm font-bold px-3 py-1 rounded-full border ${SEV_STYLES[alert.severity]}`}>
                    {alert.severity}
                  </span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Scroll hint */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1 text-[#787b86] text-xs animate-bounce">
          <span>scroll</span>
          <span>⌄</span>
        </div>
      </section>

      {/* ── TICKER ───────────────────────────────────────────────────────── */}
      <TickerBar />

      {/* ── STATS ────────────────────────────────────────────────────────── */}
      <section className="py-16 bg-[#0d1117]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatPill icon="✈" label="Routes Monitored"  value="5"    sub="Across India" />
            <StatPill icon="📊" label="Fare Observations" value="300+" sub="Daily updated" />
            <StatPill icon="🤖" label="ML Model"          value="91%"  sub="Anomaly detection" />
            <StatPill icon="🚨" label="Alert Signals"     value="3"    sub="WoW · Z-score · ML" />
          </div>
        </div>
      </section>

      {/* ── DASHBOARD PREVIEW ────────────────────────────────────────────── */}
      <section id="features" className="py-24 relative overflow-hidden"
               style={{ background: "radial-gradient(ellipse at 50% 0%, rgba(41,98,255,0.08) 0%, transparent 60%), #0b0e18" }}>
        <div className="max-w-7xl mx-auto px-6 text-center mb-14">
          <h2 className="text-4xl md:text-5xl font-extrabold mb-4">
            Where India monitors <span className="gradient-text">airfare inflation</span>
          </h2>
          <p className="text-[#b2b5be] text-lg max-w-2xl mx-auto">
            A professional-grade dashboard combining real-time price tracking, statistical anomaly
            detection, and explainable AI alerts — all in one view.
          </p>
        </div>

        {/* Mock dashboard screenshot card */}
        <div className="max-w-6xl mx-auto px-6 relative">
          <div className="animate-pulse-glow rounded-2xl overflow-hidden border border-[#2962ff]/30"
               style={{ background: "linear-gradient(135deg, #1a1f30 0%, #131722 100%)" }}>
            {/* Fake chrome bar */}
            <div className="flex items-center gap-2 px-4 py-3 border-b border-[#2a2e39] bg-[#1e222d]">
              <div className="w-3 h-3 rounded-full bg-[#f23645]/60" />
              <div className="w-3 h-3 rounded-full bg-[#f59e0b]/60" />
              <div className="w-3 h-3 rounded-full bg-[#089981]/60" />
              <div className="flex-1 mx-4 bg-[#2a2e39] rounded px-3 py-1 text-xs text-[#787b86]">
                localhost:3000/app — PROMETHEUS Dashboard
              </div>
              <span className="text-xs text-[#2962ff] font-semibold">⚡ Live</span>
            </div>
            {/* Fake chart area */}
            <div className="grid grid-cols-[48px_1fr_280px] h-72">
              {/* Left toolbar */}
              <div className="border-r border-[#2a2e39] flex flex-col items-center pt-4 gap-3">
                {["✛","〰","T","📏"].map((ic, i) => (
                  <div key={i} className="w-7 h-7 rounded bg-[#2a2e39]/60 flex items-center justify-center text-xs text-[#787b86]">{ic}</div>
                ))}
              </div>
              {/* Chart */}
              <div className="relative flex flex-col p-3">
                <div className="text-xs text-[#787b86] mb-1 flex gap-3">
                  <span className="text-white font-bold">APIx</span>
                  <span className="text-[#b2b5be]">104.83</span>
                  <span className="text-[#f23645] font-semibold">▲ +0.91%</span>
                </div>
                <svg className="flex-1 w-full" viewBox="0 0 600 180" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%"   stopColor="#2962ff" stopOpacity="0.3" />
                      <stop offset="100%" stopColor="#2962ff" stopOpacity="0" />
                    </linearGradient>
                  </defs>
                  {/* Grid lines */}
                  {[40,80,120,160].map(y => (
                    <line key={y} x1="0" y1={y} x2="600" y2={y} stroke="#1f2937" strokeWidth="1" />
                  ))}
                  {[100,200,300,400,500].map(x => (
                    <line key={x} x1={x} y1="0" x2={x} y2="180" stroke="#1f2937" strokeWidth="1" />
                  ))}
                  {/* Sparkline */}
                  <polyline
                    fill="none" stroke="#2962ff" strokeWidth="2" strokeLinecap="round"
                    points="0,140 30,138 60,130 90,135 120,120 150,118 180,125 210,110 240,100 270,108 300,95 330,90 360,98 390,85 420,80 450,88 480,75 510,72 540,78 570,68 600,60"
                  />
                  <polygon
                    fill="url(#chartGrad)"
                    points="0,180 0,140 30,138 60,130 90,135 120,120 150,118 180,125 210,110 240,100 270,108 300,95 330,90 360,98 390,85 420,80 450,88 480,75 510,72 540,78 570,68 600,60 600,180"
                  />
                  {/* Crosshair dot */}
                  <circle cx="480" cy="75" r="4" fill="#2962ff" />
                  <line x1="480" y1="0" x2="480" y2="180" stroke="#787b86" strokeWidth="1" strokeDasharray="4,3" />
                  <line x1="0"   y1="75" x2="600" y2="75" stroke="#787b86" strokeWidth="1" strokeDasharray="4,3" />
                </svg>
              </div>
              {/* Right panel */}
              <div className="border-l border-[#2a2e39] p-3">
                <p className="text-[10px] text-[#787b86] font-semibold mb-2">ROUTE WATCHLIST</p>
                {[
                  { r:"DEL-BOM", v:"107.42", c:"+1.24%", up:true },
                  { r:"DEL-BLR", v:"104.88", c:"+0.67%", up:true },
                  { r:"BOM-BLR", v:"102.10", c:"-0.31%", up:false },
                  { r:"DEL-MAA", v:"105.55", c:"+2.10%", up:true },
                  { r:"HYD-DEL", v:"103.22", c:"-0.98%", up:false },
                ].map(r => (
                  <div key={r.r} className="grid grid-cols-[2fr,1.5fr,1.5fr] text-[11px] py-1.5 border-b border-[#2a2e39]/50">
                    <span className="font-bold text-white">{r.r}</span>
                    <span className="text-[#b2b5be] text-right">{r.v}</span>
                    <span className={`text-right font-semibold ${r.up ? "text-[#089981]" : "text-[#f23645]"}`}>{r.c}</span>
                  </div>
                ))}
                <div className="mt-3 p-2 rounded bg-[#f23645]/10 border border-[#f23645]/30">
                  <p className="text-[10px] font-bold text-[#f23645]">🚨 HIGH ALERT</p>
                  <p className="text-[9px] text-[#b2b5be] mt-0.5">Near-term fares spiking on DEL-BOM</p>
                </div>
              </div>
            </div>
            {/* Bottom panel */}
            <div className="border-t border-[#2a2e39] px-4 py-2 flex gap-6 text-[11px] text-[#787b86]">
              <span className="text-[#2962ff] border-b-2 border-[#2962ff] pb-1 font-semibold">Fares</span>
              <span className="hover:text-white cursor-pointer">Alerts</span>
              <span className="hover:text-white cursor-pointer">History</span>
            </div>
          </div>
          {/* Glow under card */}
          <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 w-3/4 h-16 blur-3xl rounded-full bg-[#2962ff]/20 pointer-events-none" />
        </div>
        <div className="text-center mt-12">
          <Link href="/app" className="inline-flex items-center gap-2 text-sm font-semibold border border-[#2a2e39] px-6 py-3 rounded-xl text-[#b2b5be] hover:border-[#2962ff]/50 hover:text-white transition-all">
            Explore features →
          </Link>
        </div>
      </section>

      {/* ── AIRFARE INDEX SUMMARY ─────────────────────────────────────────── */}
      <section id="index" className="py-24 bg-white text-[#131722]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-end justify-between mb-8">
            <div>
              <h2 className="text-3xl font-extrabold">Airfare Index Summary <span className="text-[#787b86]">›</span></h2>
              {apix && (
                <div className="flex items-center gap-3 mt-2">
                  <div className="w-12 h-12 rounded-full bg-[#2962ff] flex items-center justify-center text-white font-extrabold text-lg">
                    Ax
                  </div>
                  <div>
                    <p className="font-extrabold text-2xl">{apix.index_value.toFixed(2)} <span className="text-sm font-normal text-[#787b86]">POINT</span>
                      <span className={`ml-2 text-base ${apix.wow_change >= 0 ? "text-[#f23645]" : "text-[#089981]"}`}>
                        {apix.wow_change >= 0 ? "▲ +" : "▼ "}{apix.wow_change.toFixed(2)}%
                      </span>
                    </p>
                    <p className="text-sm text-[#787b86]">APIx — Base period = 100</p>
                  </div>
                </div>
              )}
            </div>
            <Link href="/app" className="text-sm font-semibold text-[#2962ff] hover:underline">Open chart →</Link>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-[1fr,320px] gap-8">
            {/* Sparkline area */}
            <div className="bg-[#f8fafc] rounded-xl p-6 border border-[#e2e8f0]">
              <svg viewBox="0 0 700 160" className="w-full h-40">
                <defs>
                  <linearGradient id="greenGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%"   stopColor="#089981" stopOpacity="0.3"/>
                    <stop offset="100%" stopColor="#089981" stopOpacity="0"/>
                  </linearGradient>
                </defs>
                {[40,80,120].map(y => <line key={y} x1="0" y1={y} x2="700" y2={y} stroke="#e2e8f0" strokeWidth="1"/>)}
                <polyline fill="none" stroke="#089981" strokeWidth="2" strokeLinecap="round"
                  points="0,130 35,128 70,120 105,125 140,110 175,105 210,112 245,98 280,90 315,100 350,88 385,80 420,92 455,78 490,70 525,82 560,68 595,62 630,70 665,58 700,52" />
                <polygon fill="url(#greenGrad)"
                  points="0,160 0,130 35,128 70,120 105,125 140,110 175,105 210,112 245,98 280,90 315,100 350,88 385,80 420,92 455,78 490,70 525,82 560,68 595,62 630,70 665,58 700,52 700,160"/>
              </svg>
            </div>

            {/* Major routes */}
            <div>
              <p className="text-sm font-bold text-[#131722] mb-3">Top Routes</p>
              {(routes?.items ?? []).map((r) => (
                <div key={r.id} className="flex items-center justify-between py-2.5 border-b border-[#e2e8f0] last:border-0">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-full bg-[#2962ff] flex items-center justify-center text-white text-xs font-bold">{r.origin[0]}</div>
                    <div>
                      <p className="text-sm font-bold">{r.origin}-{r.destination}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-sm">{r.current_index.toFixed(2)} <span className="text-xs font-normal text-[#787b86]">POINT</span></p>
                    <p className={`text-xs font-semibold ${r.wow_change >= 0 ? "text-[#f23645]" : "text-[#089981]"}`}>
                      {r.wow_change >= 0 ? "▲ +" : "▼ "}{r.wow_change.toFixed(2)}%
                    </p>
                  </div>
                </div>
              ))}
              <Link href="/app" className="block text-xs text-[#2962ff] font-semibold mt-3 hover:underline">See all routes ›</Link>
            </div>
          </div>
        </div>
      </section>

      {/* ── ROUTE CARDS ──────────────────────────────────────────────────── */}
      <section id="routes" className="py-24 bg-[#0d1117]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-end justify-between mb-8">
            <h2 className="text-3xl font-extrabold">Route Index Cards</h2>
            <Link href="/app" className="text-sm text-[#2962ff] hover:underline">See all routes ›</Link>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {(routes?.items ?? []).map((r) => (
              <RouteCard key={r.id} route={r} sparkData={sparkData[r.id] ?? []} />
            ))}
            {/* Placeholder card */}
            <Link href="/app"
              className="glow-card bg-[#131722] rounded-xl p-4 flex items-center justify-center min-h-[140px] border-2 border-dashed border-[#2a2e39] hover:border-[#2962ff]/50 transition-colors group"
            >
              <span className="text-[#787b86] group-hover:text-[#2962ff] transition-colors text-sm font-semibold">+ Open full dashboard →</span>
            </Link>
          </div>
        </div>
      </section>

      {/* ── ALERTS SECTION ───────────────────────────────────────────────── */}
      <section id="alerts" className="py-24 relative overflow-hidden"
               style={{ background: "radial-gradient(ellipse at 50% 100%, rgba(242,54,69,0.06) 0%, transparent 60%), #0b0e18" }}>
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-end justify-between mb-8">
            <div>
              <h2 className="text-3xl font-extrabold">Active Alerts <span className="text-[#787b86]">›</span></h2>
              <p className="text-[#b2b5be] mt-1 text-sm">ML-powered + statistical anomaly detection across all routes</p>
            </div>
            <Link href="/app" className="text-sm text-[#2962ff] hover:underline">See all alerts ›</Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {mockAlerts.map((a) => (
              <div key={a.id} className="glow-card bg-[#131722] rounded-xl p-5 hover:bg-[#1a1f30] transition-colors cursor-pointer">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="font-bold text-base">{a.route}</p>
                    <p className="text-xs text-[#787b86]">Route Alert</p>
                  </div>
                  <span className={`text-xs font-bold px-2.5 py-1 rounded-full border ${SEV_STYLES[a.severity]}`}>
                    {a.severity}
                  </span>
                </div>
                <p className="text-[#b2b5be] text-sm mb-4 italic">"{a.msg}"</p>
                <div className="flex gap-6 text-xs text-[#787b86]">
                  <div>
                    <p className="text-white font-semibold text-base">{a.wow}</p>
                    <p>WoW Change</p>
                  </div>
                  <div>
                    <p className="text-white font-semibold text-base">{a.z}</p>
                    <p>Z-Score</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ──────────────────────────────────────────────────────────── */}
      <section className="py-24 text-center"
               style={{ background: "linear-gradient(180deg, #0b0e18 0%, #0d1240 50%, #0b0e18 100%)" }}>
        <div className="max-w-3xl mx-auto px-6">
          <h2 className="text-4xl md:text-5xl font-extrabold mb-4">
            Ready to monitor <span className="gradient-text">airfare inflation?</span>
          </h2>
          <p className="text-[#b2b5be] text-lg mb-10">
            Launch the PROMETHEUS dashboard and get real-time APIx data,<br className="hidden md:block" />
            ML-powered alerts, and explainable insights.
          </p>
          <Link
            href="/app"
            className="animate-pulse-glow inline-block bg-[#2962ff] hover:bg-[#1e53e5] text-white font-bold text-lg px-10 py-4 rounded-xl transition-colors"
          >
            Launch App — Free →
          </Link>
          <p className="text-[#787b86] text-sm mt-4">SIH 2026 · Problem Statement SIH26056</p>
        </div>
      </section>

      {/* ── FOOTER ───────────────────────────────────────────────────────── */}
      <footer className="border-t border-[#1e2235] py-8 bg-[#0b0e18]">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-[#787b86]">
          <div className="flex items-center gap-2">
            <span className="font-bold text-white">⚡ PROMETHEUS</span>
            <span>— Real-time Airfare Price Index for India</span>
          </div>
          <div className="flex gap-6">
            <Link href="/app"     className="hover:text-white transition-colors">Dashboard</Link>
            <Link href="/app"     className="hover:text-white transition-colors">Alerts</Link>
            <span className="text-[#2a2e39]">|</span>
            <span>© 2026 SIH26056 Team</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
