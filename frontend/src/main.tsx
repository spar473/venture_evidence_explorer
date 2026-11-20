import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import type { Venture, VentureSummary, Facets } from "./types";
import type { Filters } from "./filters";
import { Directory, type DirectorySession } from "./directory";
import { EvidenceDrawer } from "./drawer";
import { ComparisonWorkspace } from "./comparison";
import { AnalyticsWorkspace } from "./analytics";
import { DiscoveryWorkspace } from "./discovery";
import { IntakeWorkspace } from "./intake";
import { ResearchWorkspace } from "./research";
import { Status } from "./shared";
import { useResource, type ComparisonSession } from "./hooks";
import "./style.css";
import { Workbench } from "./workbench";

function ResearchApp() {
  const [tab, setTab] = useState<"browse" | "compare" | "analytics" | "research" | "intake" | "discovery">("browse");
  const {data: facets, error: facetsError} = useResource<Facets>("/facets");
  const [filters, updateFilters] = useState<Filters>({programme: "", year: "", connection: ""});
  const [selected, setSelected] = useState<VentureSummary | Venture | null>(null);
  const [directorySession, setDirectorySession] = useState<DirectorySession>({q: "", offset: 0, limit: 25});
  const [comparisonSession, setComparisonSession] = useState<ComparisonSession>({subject: "", subjectName: "", subjectSearch: "", subjectOffset: 0, description: "", mode: "product_customer", comparison: null, comparisonKey: null});
  function setFilters(value: Filters) {
    updateFilters(value);
    setDirectorySession(s => ({...s, offset: 0}));
  }
  function investigate(v: Venture) {
    setSelected(null); setComparisonSession(s => ({...s, subject: v.venture_id, subjectName: v.display_name, description: "", comparison: null, comparisonKey: null})); setTab("compare"); window.scrollTo(0, 0);
  }
  return (
    <>
      <a className="skip-link" href="#workspace-content">
        Skip to workspace
      </a>
      <header className="topbar">
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            setTab("browse");
          }}
        >
          <span className="brand-name">Venture Evidence Explorer</span>
          <span className="brand-context">Independent research workspace</span>
        </a>
        <nav aria-label="Main navigation">
          {(["browse", "compare", "analytics", "research", "intake", "discovery"] as const).map((t) => (
            <button
              key={t}
              aria-current={tab === t ? "page" : undefined}
              onClick={() => setTab(t)}
            >
              {t === "browse"
                ? "Explore ventures"
                : t === "compare"
                  ? "Find comparisons"
                  : t === "research" ? "Research dossiers" : t === "intake" ? "Add venture" : t === "discovery" ? "Discovery queue" : "Data & exports"}
            </button>
          ))}
        </nav>
        <a className="local" href="/">Precedent workbench</a>
      </header>
      <main id="workspace-content" tabIndex={-1}>
        <div className="page-heading">
          <div>
            <h1>
              {tab === "browse"
                ? "Venture directory"
                : tab === "compare"
                  ? "Find a comparison"
                  : tab === "research" ? "Research dossiers" : tab === "intake" ? "Add venture" : tab === "discovery" ? "Discovery queue" : "Data & exports"}
            </h1>
            <p className="lede">
              {tab === "browse"
                ? "Historical product descriptions and University of Auckland relationships."
                : tab === "compare"
                  ? "Choose a subject and an investigation. Compare the sourced evidence."
                  : tab === "research" ? "Inspect atomic claims, prospective targets and question-specific evidence gaps." : tab === "intake" ? "Save local assertions and compare without promoting them into trusted evidence." : tab === "discovery" ? "Review research leads without accepting identity, NZ scope or outcomes." : "Inspect the sample’s coverage and download the underlying analytical tables."}
            </p>
          </div>
          <details className="sample-notice">
            <summary>About this sample</summary>
            <p>
              Selected historical sample. Current status, funding and outcomes
              remain unverified. Awards establish recorded recognition. This
              independent project is not endorsed by the University or its
              programmes.
            </p>
          </details>
        </div>
        {facetsError && <Status error>{facetsError}</Status>}
        {tab === "browse" && <Directory session={directorySession} setSession={setDirectorySession} facets={facets} filters={filters} setFilters={setFilters} onOpen={setSelected} selectedId={selected?.venture_id} />}
        {tab === "browse" && selected && <EvidenceDrawer v={selected} onCompare={investigate} onClose={() => setSelected(null)} />}
        {tab === "compare" && <ComparisonWorkspace session={comparisonSession} setSession={setComparisonSession} filters={filters} setFilters={setFilters} facets={facets} onOpen={v => { setSelected(v); setTab("browse"); }} />}
        {tab === "analytics" && <AnalyticsWorkspace />}
        {tab === "research" && <ResearchWorkspace />}
        {tab === "intake" && <IntakeWorkspace />}
        {tab === "discovery" && <DiscoveryWorkspace />}
      </main>
      <footer>
        <span>Venture Evidence Explorer · Independent local project</span>
        <span>Historical reports; current company status unverified.</span>
      </footer>
    </>
  );
}
createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    {new URLSearchParams(window.location.search).get("mode") === "research" ? <ResearchApp /> : <Workbench />}
  </React.StrictMode>,
);
