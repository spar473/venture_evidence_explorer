import { useState } from "react";
import type { HealthtechCoverage, ResearchSubjectsResponse } from "./api-schema";
import { useResource } from "./hooks";
import { Status } from "./shared";
import "./workbench.css";

const tabs = ["Overview", "Evidence", "Outlook"] as const;

export function Workbench() {
  const { data, error, loading } = useResource<HealthtechCoverage>("/research/healthtech/coverage");
  const subjects = useResource<ResearchSubjectsResponse>("/research/subjects?limit=100");
  const names = new Map(subjects.data?.items.map(item => [item.subject_id, item.display_name]));
  const [page, setPage] = useState<"precedents" | "outcomes">("precedents");
  const [tab, setTab] = useState<typeof tabs[number]>("Overview");
  const [subjectId, setSubjectId] = useState("subj_ht_mri");
  const subject = data?.projects.find(project => project.subject_id === subjectId) ?? data?.projects[0];

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
        {data?.projects.map(project => <button key={project.subject_id}
          aria-current={page === "precedents" && project.subject_id === subject?.subject_id ? "true" : undefined}
          onClick={() => { setSubjectId(project.subject_id); setPage("precedents"); }}>{names.get(project.subject_id) ?? project.subject_id}</button>)}
      </nav>
      <div className="wb-sidebar-footer">
        <a href="/?mode=research">Research mode</a>
        <span>Evidence as of {data?.as_of ?? "unavailable"}</span>
      </div>
    </aside>
    <main id="workspace-content" tabIndex={-1} className="wb-content">
      {page === "outcomes" ? <h1>Outcome library</h1> : <>
        <header className="wb-header"><p>Precedents</p><h1>{(subject && names.get(subject.subject_id)) ?? "Precedents"}</h1>
          {subject && <p>University research project · Analogy query</p>}
        </header>
        <nav className="wb-tabs" aria-label="Precedent views">
          {tabs.map(item => <button key={item} aria-current={tab === item ? "page" : undefined} onClick={() => setTab(item)}>
            {item}{item === "Outlook" && <span role="img" aria-label="locked"> 🔒</span>}
          </button>)}
        </nav>
        {loading && <Status>Loading the university watchlist…</Status>}
        {(error || subjects.error) && <Status error>{error || subjects.error}</Status>}
        {tab === "Outlook" && <section className="wb-card"><h2>Outcome rates locked</h2></section>}
        {tab === "Overview" && subject && <section className="wb-card"><h2>Curated precedents</h2>
          {subject.peers.length ? <ul>{subject.peers.map(peer => <li key={peer.subject_id}>{peer.display_name}</li>)}</ul>
            : <p>No supported comparison at the pilot cutoff.</p>}
        </section>}
      </>}
    </main>
  </div>;
}
