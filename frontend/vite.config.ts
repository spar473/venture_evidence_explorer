import { defineConfig } from "vite";
export default defineConfig(({ mode }) => ({
  base: mode === "static" ? "./" : "/",
  server: { host: "127.0.0.1", proxy: { "/api": "http://127.0.0.1:8000" } },
}));
