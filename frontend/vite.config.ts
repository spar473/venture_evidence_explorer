import { defineConfig } from "vite";

// Begin the profile data downloads alongside the production bundle on Pages.
const preloadProfile = `
  const url = new URL(location.href);
  const view = url.searchParams.get("view");
  if (url.searchParams.get("mode") !== "research" &&
      (view === "profile" || (!view && url.searchParams.get("page") !== "outcomes"))) {
    const id = url.searchParams.get("company") || url.searchParams.get("company_id") || "public_supie";
    const paths = ["views/cohort"];
    if (/^[a-z0-9_]+$/.test(id)) paths.push("views/overview/" + id, "robustness/" + id);
    for (const path of paths) {
      const link = document.createElement("link");
      link.rel = "preload";
      link.as = "fetch";
      link.crossOrigin = "anonymous";
      link.href = "./analytics-data/" + path + ".json";
      document.head.append(link);
    }
  }
`;

export default defineConfig(({ mode }) => ({
  base: mode === "static" ? "./" : "/",
  plugins:
    mode === "static"
      ? [
          {
            name: "preload-static-profile",
            transformIndexHtml() {
              return [{ tag: "script", children: preloadProfile, injectTo: "head-prepend" }];
            },
          },
        ]
      : [],
  server: { host: "127.0.0.1", proxy: { "/api": "http://127.0.0.1:8000" } },
}));
