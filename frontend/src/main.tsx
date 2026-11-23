import { lazy, StrictMode, Suspense } from "react";
import { createRoot } from "react-dom/client";
import { AnalyticsViews } from "./analytics-views/shell";
import { STATIC } from "./analytics-views/data";
import "./style.css";

const ResearchApp = lazy(() => import("./research-app"));
const Workbench = lazy(() =>
  import("./workbench").then(({ Workbench }) => ({ default: Workbench })),
);
const params = new URLSearchParams(location.search);
const mode = params.get("mode");
const compatibility =
  !params.has("view") && document.querySelector('meta[name="vee-legacy-routes"]');
const root = createRoot(document.getElementById("root")!);

root.render(
  <StrictMode>
    <Suspense fallback={<p role="status">Loading workspace…</p>}>
      {mode === "research" && STATIC ? (
        <main>
          <h1>Research workspace</h1>
          <p>The research workspace runs on the local VEE server.</p>
          <a href="https://github.com/spar473/venture_evidence_explorer#run-it">
            Run it locally
          </a> · <a href="?view=profile">Analytics views</a>
        </main>
      ) : mode === "research" ? (
        <ResearchApp />
      ) : !STATIC && (mode === "workbench" || compatibility) ? (
        <Workbench />
      ) : (
        <AnalyticsViews />
      )}
    </Suspense>
  </StrictMode>,
);
