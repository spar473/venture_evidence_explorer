import { useState } from "react";
import type { HealthtechCoverage, PoolDirectory, PrecedentResponse,
  ResearchSubjectsResponse, WorkbenchClaim, WorkbenchGates } from "./api-schema";
import { useResource } from "./hooks";
import { Status } from "./shared";
import { type AnchorKind, ClaimDrawer, GateProgress } from "./workbench-shared";
import { Overview } from "./workbench-overview";
import "./workbench.css";

const tabs = ["Overview", "Evidence", "Outlook"] as const;

export function Workbench() {
  const watchlist = useResource<HealthtechCoverage>("/research/healthtech/coverage");
  const subjects = useResource<ResearchSubjectsResponse>("/research/subjects?limit=100");
  const fixture = useResource<PoolDirectory>("/reference-pool");
  const gates = useResource<WorkbenchGates>("/workbench/gates");
  const names = new Map(subjects.data?.items.map(item => [item.subject_id, item.display_name]));
  const [page, setPage] = useState<"precedents" | "outcomes">("precedents");
  const [tab, setTab] = useState<typeof tabs[number]>("Overview");
  const [subjectId, setSubjectId] = useState("subj_ht_mri");
  const [anchor, setAnchor] = useState<AnchorKind>("first_institutional_round");
  const [cohort, setCohort] = useState<"curated" | "similar">("curated");
  const [selectedDate, setSelectedDate] = useState("");
  const [query, setQuery] = useState("");
  const [claim, setClaim] = useState<WorkbenchClaim | null>(null);
  const asOf = selectedDate || gates.data?.as_of || "";
  const path = asOf ? `/precedents/${encodeURIComponent(subjectId)}?${new URLSearchParams({anchor, as_of: asOf})}` : null;
  const precedent = useResource<PrecedentResponse>(path);
  const data = precedent.data?.subject.company_id === subjectId && precedent.data.as_of === asOf
    && precedent.data.anchor_kind === anchor ? precedent.data : null;
  const watched = watchlist.data?.projects.find(project => project.subject_id === subjectId);
  const search = [...(watchlist.data?.projects ?? []).map(project => ({
    id: project.subject_id, name: names.get(project.subject_id),
  })), ...(fixture.data?.companies ?? []).map(company => ({
    id: company.company_id, name: company.display_name,
  }))].filter(item => item.name && item.name.toLowerCase().includes(query.trim().toLowerCase())).slice(0, 12);
  const subjectName = data?.subject.display_name ?? (watched && names.get(watched.subject_id));
  function openSubject(id: string) {
    setSubjectId(id); setPage("precedents"); setTab("Overview"); setCohort("curated"); setQuery(""); setClaim(null);
  }

  return <div className="workbench">
    <a className="skip-link" href="#workspace-content">Skip to workspace</a>
    <aside className="wb-sidebar" aria-label="Workbench sidebar">
      <a className="wb-brand" href="/">Venture Evidence Explorer</a>
      <nav aria-label="Main navigation">
        <button aria-current={page === "precedents" ? "page" : undefined} onClick={() => setPage("precedents")}>Precedents</button>
        <button aria-current={page === "outcomes" ? "page" : undefined} onClick={() => setPage("outcomes")}>Outcome library</button>
      </nav>
      <nav aria-label="University watchlist">
        <h2>University watchlist</h2>
        {watchlist.data?.projects.map(project => <button key={project.subject_id}
          aria-current={page === "precedents" && project.subject_id === subjectId ? "true" : undefined}
          onClick={() => openSubject(project.subject_id)}>{names.get(project.subject_id) ?? project.subject_id}</button>)}
      </nav>
      <div className="wb-sidebar-footer">
        <a href="/?mode=research">Research mode</a>
        <span>Evidence as of {asOf || "unavailable"}</span>
      </div>
    </aside>
    <main id="workspace-content" tabIndex={-1} className="wb-content">
      {page === "outcomes" ? <h1>Outcome library</h1> : <>
        <div className="wb-toolbar wb-search">
          <div><label>Search ventures<input type="search" value={query} onChange={event => setQuery(event.target.value)} /></label>
            {query.trim() && <div className="wb-search-results" aria-label="Venture search results">
              {search.length ? search.map(item => <button type="button" key={item.id} onClick={() => openSubject(item.id)}>{item.name}</button>)
                : <p>No venture names match.</p>}
            </div>}
          </div>
          <label>As-of date<input type="date" value={asOf} onChange={event => setSelectedDate(event.target.value)} /></label>
        </div>
        <header className="wb-header"><p>Precedents</p><h1>{subjectName ?? "Precedents"}</h1>
          {data && <>
            <p>{data.subject.kind === "research_project" ? "University research project" : "Company"}
              {data.subject.sector && ` · ${data.subject.sector}`}
              {data.subject.anchor && ` · ${data.subject.anchor.claim.date_value}`}</p>
            {data.subject.kind === "research_project" && <p>Analogy query · No verified funding round yet</p>}
            <dl className="wb-metrics">
              <div><dd>{data.curated.length}</dd><dt>Curated precedents</dt></div>
              <div><dd>{data.subject.claims.length}</dd><dt>Cited claims</dt></div>
              <div><dd>{data.subject.gaps.length}</dd><dt>Open gaps</dt></div>
            </dl>
          </>}
        </header>
        <nav className="wb-tabs" aria-label="Precedent views">
          {tabs.map(item => <button key={item} aria-current={tab === item ? "page" : undefined} onClick={() => setTab(item)}>
            {item}{item === "Outlook" && <span role="img" aria-label="locked"> 🔒</span>}
          </button>)}
        </nav>
        {(watchlist.error || subjects.error || precedent.error || gates.error) && <Status error>{watchlist.error || subjects.error || precedent.error || gates.error}</Status>}
        {!data && !precedent.error && !gates.error && tab !== "Outlook" && <Status>Loading precedent evidence…</Status>}
        {tab === "Outlook" && <section className="wb-card"><h2>Outcome rates locked</h2>
          {gates.data ? <GateProgress gates={gates.data}/> : <Status error={Boolean(gates.error)}>{gates.error || "Loading cohort audit…"}</Status>}
        </section>}
        {tab === "Overview" && data && <Overview data={data} gates={gates.data} gateError={gates.error}
          cohort={cohort} onCohort={setCohort} onAnchor={setAnchor} onClaim={setClaim} onOutlook={() => setTab("Outlook")} onEvidence={() => setTab("Evidence")}/>}
      </>}
    </main>
    {claim && <ClaimDrawer claim={claim} onClose={() => setClaim(null)}/>}
  </div>;
}
