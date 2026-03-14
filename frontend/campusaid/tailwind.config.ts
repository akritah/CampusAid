import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        campusaid: {
          red: "#dc143c",
          blue: "#1a2332"
        }
      }
    }
  },
  plugins: []
};

export default config;
