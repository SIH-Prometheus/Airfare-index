/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        tv: {
          bg: "#131722",
          panel: "#1e222d",
          border: "#2a2e39",
          text: "#d1d4dc",
          muted: "#b2b5be",
          up: "#089981",
          down: "#f23645",
          blue: "#2962ff",
          blueHover: "#1e53e5",
          crosshair: "#787b86",
          grid: "#1f2937",
        },
        brand: {
          50:  "#eff6ff",
          100: "#dbeafe",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
          900: "#1e3a8a",
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui"],
        mono: ["JetBrains Mono", "ui-monospace"],
      },
    },
  },
  plugins: [],
};
