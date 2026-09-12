// app/layout.tsx — Root layout (no nav bar — landing and app each manage their own)
import type { Metadata } from "next";
import "./globals.css";
import DarkModeProvider from "@/components/DarkModeProvider";

export const metadata: Metadata = {
  title:       "PROMETHEUS | Airfare Price Index",
  description: "Real-time APIx monitoring for Indian aviation — SIH 2026",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen bg-[var(--bg)] text-[var(--text)]">
        <DarkModeProvider>
          {children}
        </DarkModeProvider>
      </body>
    </html>
  );
}
