"use client";

// components/DarkModeProvider.tsx — manages <html class="dark"> toggle

import { createContext, useContext, useEffect, useState } from "react";

type DarkModeCtx = { dark: boolean; toggle: () => void };
const Ctx = createContext<DarkModeCtx>({ dark: false, toggle: () => {} });

export function useDarkMode() {
  return useContext(Ctx);
}

export default function DarkModeProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("theme");
    if (stored === "dark") {
      document.documentElement.classList.add("dark");
      setDark(true);
    }
  }, []);

  const toggle = () => {
    setDark((prev) => {
      const next = !prev;
      if (next) {
        document.documentElement.classList.add("dark");
        localStorage.setItem("theme", "dark");
      } else {
        document.documentElement.classList.remove("dark");
        localStorage.setItem("theme", "light");
      }
      return next;
    });
  };

  return <Ctx.Provider value={{ dark, toggle }}>{children}</Ctx.Provider>;
}
