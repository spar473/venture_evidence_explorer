import { defineConfig } from "@playwright/test";

const testPort = process.env.VEE_TEST_PORT || "8138";
const baseURL = process.env.VEE_URL || `http://127.0.0.1:${testPort}`;

export default defineConfig({
  testDir: "./e2e",
  // Mutable draft tests share one disposable service; serialize corpus snapshots.
  workers: 1,
  timeout: 30000,
  use: {
    baseURL,
    headless: true,
    // Bundled Chromium is portable; explicitly opt in to a local binary if needed.
    launchOptions: process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {},
  },
  webServer: process.env.VEE_URL ? undefined : {
    command: process.env.VEE_STATIC
      ? [process.env.VEE_PYTHON || "python3", "-m http.server", testPort, "--bind 127.0.0.1 --directory dist"].join(" ")
      : "node e2e/server.mjs",
    url: baseURL + (process.env.VEE_STATIC ? "/" : "/api/health"),
    reuseExistingServer: false,
    timeout: 30000,
  },
  reporter: "list",
  outputDir: "../outputs/browser-tests",
});
