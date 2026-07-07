/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // Signature palette: deep ink + signal amber (recommendation = "signal"
        // being surfaced from noise), instead of default indigo/blue SaaS look.
        ink: {
          950: "#0B0E14",
          900: "#12161F",
          800: "#1B212D",
          700: "#2A3241",
        },
        signal: {
          400: "#FFB454",
          500: "#F59E3C",
          600: "#DB7F1F",
        },
        mist: {
          100: "#F5F6F8",
          300: "#C9CEDA",
          500: "#7B8496",
        },
      },
      fontFamily: {
        display: ["'Fraunces'", "serif"],
        body: ["'Inter'", "sans-serif"],
      },
      borderRadius: {
        xl2: "1.25rem",
      },
    },
  },
  plugins: [],
}
