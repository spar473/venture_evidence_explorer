import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import type { Evidence, Venture, Facets, Comparison } from "./types";
import "./style.css";

const labels: Record<string, string> = {
  velocity_100k: "Velocity $100K Challenge",
  velocity_ideas: "Velocity Ideas Challenge",
  uoa_programme_participation: "Programme participation",
  uoa_student_venture: "Student venture",
  uoa_staff_research_team: "Staff research team",
  uoa_research_origin: "Research origin",
  uoa_spinout: "Spinout",
  uoa_staff_alumni_founders: "Staff / alumni founders",
  product_description: "Product description",
  uoa_connection: "University connection",
  product_customer: "Product / customer",
  commercialisation: "Commercialisation pathway",
  stage_milestone: "Stage / milestone",
  source_checked_owner_review_pending: "Source checked; owner review pending",
  needs_owner_review: "Owner review pending",
  historical_description_at_publication:
    "Historical description at publication",
  relationship_reported_at_publication: "Relationship reported at publication",
  "100k_award": "Recorded $100K recognition",
  ideas_award: "Recorded Ideas recognition",
  uoa_origin: "University origin",
  programme_recognition: "Programme recognition",
  connection_coverage: "University connections",
  source_coverage: "Evidence coverage",
  programme: "Programme",
  award_year: "Year",
  recorded_awards: "Awards",
  distinct_ventures: "Ventures",
  connection_type: "Connection type",
  recorded_connections: "Relationships",
  venture_id: "Record ID",
  display_name: "Venture",
  source_count: "Sources",
  observation_count: "Observations",
  earliest_source_date: "First published",
  latest_source_date: "Last published",
  latest_retrieval_date: "Last retrieved",
  as_of_date: "As of (UTC)",
  latest_source_age_days: "Source age (days)",
  evidence_note: "Coverage note",
};
const label = (s: string) => labels[s] || s.replaceAll("_", " ");
const unknown = (s: string | null | undefined) => s || "Unknown / unverified";
async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch("/api" + path, init);
  if (!res.ok)
    throw new Error(
      res.status === 503
        ? "Database unavailable. Run the bootstrap command and retry."
        : `Request failed (${res.status}). Please retry.`,
    );
  return res.json();
}
function Source({ e }: { e: Evidence }) {
  return (
    <div className="source">
      <a href={e.url} target="_blank" rel="noreferrer">
        {e.source_title}
        <span className="sr-only"> (opens in a new tab)</span>
      </a>
      <div>
        {e.publisher} · Published <strong>{e.published_at}</strong> · Retrieved{" "}
        {e.retrieved_at}
      </div>
      <div>Passage: {e.locator}</div>
      <div className="muted">
        Review: {label(e.review_status)}
        {e.observation_id && (
          <>
            {" "}
            · <code>{e.observation_id}</code>
          </>
        )}
      </div>
      {e.date_basis && (
        <div className="muted">
          Date basis: {label(e.date_basis)} · Effective date:{" "}
          {e.effective_at || "Not recorded"}
        </div>
      )}
    </div>
  );
}
function Observation({ e }: { e: Evidence }) {
  return (
    <article className="evidence" id={e.observation_id}>
      <span className="eyebrow">{label(e.field || "")} · Publisher report</span>
      <p>{e.value_text}</p>
      <Source e={e} />
    </article>
  );
}
function Status({
  children,
  error = false,
}: {
  children: React.ReactNode;
  error?: boolean;
}) {
  return (
    <div
      className={"status " + (error ? "error" : "")}
      role={error ? "alert" : "status"}
    >
      {children}
    </div>
  );
}
function Profile({
  v,
  onCompare,
  onClose,
}: {
  v: Venture;
  onCompare: (v: Venture) => void;
  onClose: () => void;
}) {
  return (
    <section className="profile" aria-label="Venture evidence">
      <div className="section-head">
        <span className="eyebrow">Record {v.venture_id}</span>
        <button className="text" onClick={onClose}>
          Close profile
        </button>
      </div>
      <h2 id="profile-title">{v.display_name}</h2>
      <p className="muted">
        Venture or project · identity: {label(v.identity_review_status)}
        <br />
        Selected for: {label(v.selection_bucket)}
        {v.aliases.length > 0 && (
          <> · Source spellings: {v.aliases.join(", ")}</>
        )}
      </p>
      <button className="primary" onClick={() => onCompare(v)}>
        Compare this venture
      </button>
      <div className="unknown-grid">
        {[
          ["Operating status", v.current_operating_status],
          ["Funding stage", v.current_funding_stage],
          ["Legal name", v.legal_name],
          ["Registration", v.registration_id],
        ].map(([k, x]) => (
          <div key={k}>
            <span>{k}</span>
            <strong>{unknown(x)}</strong>
          </div>
        ))}
      </div>
      <p className="notice">
        Historical descriptions are summaries of publisher reports. Retrieval in
        2026 does not verify current status or historical availability.
      </p>
      <h3>
        Source observations{" "}
        <span className="count">{v.observations.length}</span>
      </h3>
      {v.observations.map((o) => (
        <Observation key={o.observation_id} e={o} />
      ))}
      <h3>
        Recorded awards <span className="count">{v.awards.length}</span>
      </h3>
      {!v.awards.length && (
        <p className="muted">
          No award recorded in this sample. Participation and awards elsewhere
          are unknown.
        </p>
      )}
      {v.awards.map((a) => (
        <article className="evidence" key={a.award_id}>
          <h4>
            {label(a.programme)} · {a.award_year}
          </h4>
          <p>
            {a.award_label} · Placement: {a.place ?? "Unranked / not recorded"}
          </p>
          <p className="muted">
            Event date: {a.event_date || "Not verified"} · Award year is not an
            event date.
          </p>
          <Source e={a} />
        </article>
      ))}
      <h3>
        University relationships{" "}
        <span className="count">{v.connections.length}</span>
      </h3>
      {v.connections.map((c) => (
        <article className="evidence" key={c.connection_id}>
          <h4>{label(c.connection_type)}</h4>
          <p>{c.institution}</p>
          <p>{c.evidence.value_text}</p>
          <Source e={c.evidence} />
        </article>
      ))}
      <details className="proposals">
        <summary>
          Proposed analyst annotations · {v.proposed_annotations.length}{" "}
          proposals
        </summary>
        <p>
          Unreviewed hypotheses and suggested questions. Excluded from
          comparison inputs and curated analytical fields.
        </p>
        {v.proposed_annotations.map((a) => (
          <div className="proposal" key={a.annotation_id}>
            <span className="eyebrow">{label(a.field)} · Proposed</span>
            <p>{a.value_text}</p>
            <small>
              Basis:{" "}
              {a.basis_observation_ids.map((id) => (
                <a key={id} href={`#${id}`}>
                  {id}{" "}
                </a>
              ))}
            </small>
          </div>
        ))}
      </details>
    </section>
  );
}

function EvidenceDrawer({
  v,
  onCompare,
  onClose,
}: {
  v: Venture;
  onCompare: (v: Venture) => void;
  onClose: () => void;
}) {
  const drawer = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const node = drawer.current;
    const opener = document.querySelector<HTMLButtonElement>(
      `.venture-open[data-venture-id="${CSS.escape(v.venture_id)}"]`,
    );
    node?.showModal();
    return () => {
      node?.close();
      opener?.focus({ preventScroll: true });
    };
  }, [v.venture_id]);
  return (
    <dialog
      ref={drawer}
      className="profile-wrap"
      aria-labelledby="profile-title"
      onCancel={(e) => {
        e.preventDefault();
        onClose();
      }}
    >
      <Profile v={v} onCompare={onCompare} onClose={onClose} />
    </dialog>
  );
}

function App() {
  const comparisonRequest = useRef(0);
  const [tab, setTab] = useState<"browse" | "compare" | "analytics">("browse");
  const [facets, setFacets] = useState<Facets | null>(null),
    [all, setAll] = useState<Venture[]>([]),
    [items, setItems] = useState<Venture[]>([]);
  const [q, setQ] = useState(""),
    [programme, setProgramme] = useState(""),
    [year, setYear] = useState(""),
    [connection, setConnection] = useState("");
  const [loading, setLoading] = useState(true),
    [error, setError] = useState(""),
    [retry, setRetry] = useState(0),
    [selected, setSelected] = useState<Venture | null>(null);
  const [subject, setSubject] = useState(""),
    [description, setDescription] = useState(""),
    [mode, setMode] = useState("product_customer"),
    [comparison, setComparison] = useState<Comparison | null>(null),
    [busy, setBusy] = useState(false),
    [compareError, setCompareError] = useState("");
  const [analytics, setAnalytics] = useState<{
      scope: string;
      tables: Record<string, Record<string, string | number | null>[]>;
    } | null>(null),
    [analysisError, setAnalysisError] = useState("");
  useEffect(() => {
    let live = true;
    Promise.all([
      api<Facets>("/facets"),
      api<{ items: Venture[] }>("/ventures"),
    ])
      .then(([f, v]) => {
        if (live) {
          setFacets(f);
          setAll(v.items);
        }
      })
      .catch((e) => {
        if (live) setError(e.message);
      });
    return () => {
      live = false;
    };
  }, [retry]);
  useEffect(() => {
    let live = true;
    setLoading(true);
    setError("");
    const params = new URLSearchParams({
      q,
      programme,
      connection_type: connection,
    });
    if (year) params.set("year", year);
    const timer = setTimeout(
      () =>
        api<{ items: Venture[] }>("/ventures?" + params)
          .then((v) => {
            if (live) setItems(v.items);
          })
          .catch((e) => {
            if (live) setError(e.message);
          })
          .finally(() => {
            if (live) setLoading(false);
          }),
      120,
    );
    return () => {
      live = false;
      clearTimeout(timer);
    };
  }, [q, programme, year, connection, retry]);
  useEffect(() => {
    if (tab !== "analytics") return;
    let live = true;
    setAnalysisError("");
    api<NonNullable<typeof analytics>>("/analytics")
      .then((x) => {
        if (live) setAnalytics(x);
      })
      .catch((e) => {
        if (live) setAnalysisError(e.message);
      });
    return () => {
      live = false;
    };
  }, [tab, retry]);
  useEffect(() => {
    comparisonRequest.current++;
    setComparison(null);
    setBusy(false);
    setCompareError("");
  }, [subject, description, mode, programme, year, connection]);
  function investigate(v: Venture) {
    setSelected(null);
    setSubject(v.venture_id);
    setDescription("");
    setComparison(null);
    setTab("compare");
    window.scrollTo(0, 0);
  }
  async function runCompare(e: React.FormEvent) {
    e.preventDefault();
    const request = ++comparisonRequest.current;
    setBusy(true);
    setCompareError("");
    setComparison(null);
    try {
      const result = await api<Comparison>("/compare", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          subject_id: subject || null,
          query: description,
          mode,
          programme,
          year: year ? Number(year) : null,
          connection_type: connection,
        }),
      });
      if (request === comparisonRequest.current) setComparison(result);
    } catch (e) {
      if (request === comparisonRequest.current)
        setCompareError((e as Error).message);
    } finally {
      if (request === comparisonRequest.current) setBusy(false);
    }
  }
  function reset() {
    setQ("");
    setProgramme("");
    setYear("");
    setConnection("");
    setSelected(null);
  }
  const filterControls = (
    <>
      <label>
        Recorded programme
        <select
          aria-label="Recorded programme"
          value={programme}
          onChange={(e) => setProgramme(e.target.value)}
        >
          <option value="">All recorded programmes</option>
          {facets?.programmes.map((p) => (
            <option key={p.programme} value={p.programme}>
              {label(p.programme)}
            </option>
          ))}
        </select>
      </label>
      <label>
        Award year
        <select
          aria-label="Award year"
          value={year}
          onChange={(e) => setYear(e.target.value)}
        >
          <option value="">All award years</option>
          {facets?.years.map((y) => (
            <option key={y}>{y}</option>
          ))}
        </select>
      </label>
      <label>
        University relationship
        <select
          aria-label="University relationship"
          value={connection}
          onChange={(e) => setConnection(e.target.value)}
        >
          <option value="">All relationship types</option>
          {facets?.connection_types.map((c) => (
            <option key={c.connection_type} value={c.connection_type}>
              {label(c.connection_type)}
            </option>
          ))}
        </select>
      </label>
    </>
  );
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
          {(["browse", "compare", "analytics"] as const).map((t) => (
            <button
              key={t}
              aria-current={tab === t ? "page" : undefined}
              onClick={() => setTab(t)}
            >
              {t === "browse"
                ? "Explore ventures"
                : t === "compare"
                  ? "Find comparisons"
                  : "Data & exports"}
            </button>
          ))}
        </nav>
        <span className="local">Local workspace</span>
      </header>
      <main id="workspace-content" tabIndex={-1}>
        <div className="page-heading">
          <div>
            <h1>
              {tab === "browse"
                ? "Venture directory"
                : tab === "compare"
                  ? "Find a comparison"
                  : "Data & exports"}
            </h1>
            <p className="lede">
              {tab === "browse"
                ? "Historical product descriptions and University of Auckland relationships."
                : tab === "compare"
                  ? "Choose a subject and an investigation. Compare the sourced evidence."
                  : "Inspect the sample’s coverage and download the underlying analytical tables."}
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
        {tab === "browse" && (
          <>
            <div className="stats">
              {[
                ["ventures", "Ventures / projects"],
                ["sources", "Public sources"],
                ["observations", "Sourced observations"],
                ["awards", "Recorded awards"],
              ].map(([k, l]) => (
                <div key={k}>
                  <strong>{facets?.counts[k] ?? "—"}</strong>
                  <span>{l}</span>
                </div>
              ))}
            </div>
            <div className="workspace">
              <section className="filters" aria-label="Directory filters">
                <label className="search-field">
                  Search ventures
                  <input
                    aria-label="Search ventures"
                    placeholder="Search names or product descriptions"
                    value={q}
                    onChange={(e) => setQ(e.target.value)}
                  />
                </label>
                {filterControls}
                <button className="reset-button" onClick={reset}>
                  Reset filters
                </button>
              </section>
              <section
                className="results"
                aria-label="Venture list"
                aria-busy={loading}
              >
                <div className="directory-heading">
                  <h2>
                    Venture records{" "}
                    <span className="result-count" aria-live="polite">
                      {items.length} of {facets?.counts.ventures ?? "—"}{" "}
                      ventures
                    </span>
                  </h2>
                  <span className="muted">Current status unverified</span>
                </div>
                {loading ? (
                  <Status>Loading venture records…</Status>
                ) : error ? (
                  <Status error>
                    {error}{" "}
                    <button onClick={() => setRetry((x) => x + 1)}>
                      Retry
                    </button>
                  </Status>
                ) : !items.length ? (
                  <Status>
                    No ventures match these filters.{" "}
                    <button onClick={reset}>Reset filters</button>
                  </Status>
                ) : (
                  <div className="venture-list">
                    <table className="venture-table">
                      <caption className="sr-only">
                        Historical venture records. Open a venture to inspect
                        its dated evidence.
                      </caption>
                      <thead>
                        <tr>
                          <th scope="col">Venture / reported product</th>
                          <th scope="col">Recorded recognition</th>
                          <th scope="col">University relationship</th>
                          <th scope="col">Source record</th>
                        </tr>
                      </thead>
                      <tbody>
                        {items.map((v) => (
                          <tr
                            key={v.venture_id}
                            className={
                              "venture-card " +
                              (selected?.venture_id === v.venture_id
                                ? "selected"
                                : "")
                            }
                          >
                            <td className="venture-identity">
                              <button
                                className="venture-open"
                                data-venture-id={v.venture_id}
                                onClick={() => setSelected(v)}
                                aria-haspopup="dialog"
                              >
                                {v.display_name}
                              </button>
                              <p>
                                {v.observations.find(
                                  (o) => o.field === "product_description",
                                )?.value_text ||
                                  "No sourced product description recorded."}
                              </p>
                            </td>
                            <td data-label="Recognition">
                              {v.awards.length ? (
                                v.awards.map((a) => (
                                  <div className="recognition" key={a.award_id}>
                                    <span>
                                      {a.programme === "velocity_100k"
                                        ? "$100K Challenge"
                                        : "Ideas Challenge"}
                                    </span>
                                    <span className="date">{a.award_year}</span>
                                  </div>
                                ))
                              ) : (
                                <span className="not-recorded">
                                  Not recorded
                                </span>
                              )}
                            </td>
                            <td data-label="University relationship">
                              {v.connections.length ? (
                                v.connections.map((c) => (
                                  <div
                                    className="relationship"
                                    key={c.connection_id}
                                  >
                                    {label(c.connection_type)}
                                  </div>
                                ))
                              ) : (
                                <span className="not-recorded">
                                  Not recorded
                                </span>
                              )}
                            </td>
                            <td
                              className="record-meta"
                              data-label="Source record"
                            >
                              <span>
                                {
                                  new Set(
                                    v.observations.map((o) => o.source_id),
                                  ).size
                                }{" "}
                                {new Set(v.observations.map((o) => o.source_id))
                                  .size === 1
                                  ? "source"
                                  : "sources"}
                              </span>
                              {[
                                ...new Set(
                                  v.observations.map((o) => o.published_at),
                                ),
                              ].map((d) => (
                                <time key={d} dateTime={d}>
                                  {d}
                                </time>
                              ))}
                              <span className="record-note">Published</span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
                <p className="directory-footnote">
                  Programme and year refer to the same recorded award.
                  University relationships can overlap. “Not recorded” means
                  absent from this sample, not evidence of non-participation.
                </p>
              </section>
            </div>
            {selected && (
              <EvidenceDrawer
                v={selected}
                onCompare={investigate}
                onClose={() => setSelected(null)}
              />
            )}
          </>
        )}
        {tab === "compare" && (
          <div className="comparison-workspace">
            <form className="compare-form" onSubmit={runCompare}>
              <div>
                <label>
                  Subject venture
                  <select
                    aria-label="Subject venture"
                    value={subject}
                    onChange={(e) => {
                      setSubject(e.target.value);
                      setComparison(null);
                    }}
                  >
                    <option value="">Use a description instead</option>
                    {all.map((v) => (
                      <option key={v.venture_id} value={v.venture_id}>
                        {v.display_name}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Investigation mode
                  <select
                    aria-label="Investigation mode"
                    value={mode}
                    onChange={(e) => setMode(e.target.value)}
                  >
                    {[
                      "product_customer",
                      "commercialisation",
                      "stage_milestone",
                    ].map((m) => (
                      <option key={m} value={m}>
                        {label(m)}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
              {subject ? (
                <p className="notice">
                  The subject’s eligible sourced observations form the query.
                  Self-matches are excluded. Proposed annotations are excluded.
                </p>
              ) : (
                <label>
                  Describe the product or challenge
                  <textarea
                    aria-label="Investigation description"
                    value={description}
                    maxLength={5000}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="For example: clinical images software for surgical planning"
                    rows={3}
                  />
                </label>
              )}
              <details>
                <summary>
                  Candidate filters{" "}
                  {programme || year || connection ? "· active" : ""}
                </summary>
                <div className="filter-row">
                  {filterControls}
                  <button type="button" className="text" onClick={reset}>
                    Reset filters
                  </button>
                </div>
              </details>
              <button className="primary" disabled={busy} type="submit">
                {busy ? "Find comparisons — searching…" : "Find comparisons"}
              </button>
            </form>
            {!comparison && !busy && !compareError && (
              <aside className="comparison-guide">
                <h2>Choose the question first</h2>
                <dl>
                  <dt>Product / customer</dt>
                  <dd>
                    Search the reported product descriptions for shared wording.
                  </dd>
                  <dt>Commercialisation pathway</dt>
                  <dd>Also search sourced university-origin descriptions.</dd>
                  <dt>Stage / milestone</dt>
                  <dd>
                    The sample has no eligible commercial milestone data. This
                    mode will explain the evidence gap.
                  </dd>
                </dl>
                <p>
                  Results are investigation candidates. A lexical score is not
                  confidence or investment quality.
                </p>
              </aside>
            )}
            {compareError && <Status error>{compareError}</Status>}
            {busy && <Status>Searching sourced wording…</Status>}
            {comparison && (
              <section className="comparison-results">
                <div className="section-head">
                  <h2>
                    {comparison.results.length} comparison{" "}
                    {comparison.results.length === 1
                      ? "candidate"
                      : "candidates"}
                  </h2>
                  <span className="tag">{comparison.brief_type}</span>
                </div>
                <details className="method">
                  <summary>
                    Method & limitations · {comparison.method.version}
                  </summary>
                  <p>{comparison.method.scoring}</p>
                  <p>{comparison.method.normalization}</p>
                  <p>
                    <strong>Abstention: </strong>
                    {comparison.method.abstention}
                  </p>
                  <p>{comparison.method.limitations}</p>
                  <p>
                    <strong>Eligible query: </strong>
                    {comparison.effective_query ||
                      comparison.query ||
                      "No query supplied"}
                  </p>
                  <p>
                    Proposed annotations used: no. Relevance quality has not
                    been measured.
                  </p>
                </details>
                {comparison.abstention_reason && (
                  <Status>{comparison.abstention_reason}</Status>
                )}
                {comparison.subject && (
                  <div className="subject-evidence">
                    <h3>Subject: {comparison.subject.display_name}</h3>
                    {comparison.subject.observations
                      .filter(
                        (o) =>
                          o.field === "product_description" ||
                          (mode === "commercialisation" &&
                            o.field === "uoa_connection"),
                      )
                      .map((o) => (
                        <Observation key={o.observation_id} e={o} />
                      ))}
                  </div>
                )}
                {comparison.results.map((r, i) => (
                  <article
                    className="comparison-card"
                    key={r.venture.venture_id}
                  >
                    <div className="section-head">
                      <h3>
                        <span className="ordinal">{i + 1}.</span>
                        {r.venture.display_name}
                      </h3>
                      <span>Lexical score {r.ranking_score.toFixed(3)}</span>
                    </div>
                    <p>{r.brief}</p>
                    <div className="tags">
                      {r.matched_terms.map((t) => (
                        <span key={t}>{t}</span>
                      ))}
                    </div>
                    <p className="muted">
                      Query token coverage:{" "}
                      {Math.round(r.query_token_coverage * 100)}% · A ranking
                      score, not confidence or investment quality.
                    </p>
                    <details>
                      <summary>Matching fields & source passages</summary>
                      {r.evidence.map((e) => (
                        <div key={e.observation.observation_id}>
                          <p className="muted">
                            Matched in {label(e.observation.field || "")}:{" "}
                            {e.matched_terms.join(", ")}
                          </p>
                          <Observation e={e.observation} />
                        </div>
                      ))}
                    </details>
                    <div className="difference-grid">
                      <div>
                        <h4>What differs in the record</h4>
                        <p>
                          Query-only wording:{" "}
                          {r.wording_differences.query_only_terms.join(", ") ||
                            "None"}
                        </p>
                        <p>
                          Candidate-only wording:{" "}
                          {r.wording_differences.candidate_only_terms.join(
                            ", ",
                          ) || "None"}
                        </p>
                        <small>{r.wording_differences.meaning}</small>
                      </div>
                      <div>
                        <h4>Evidence unavailable here</h4>
                        <ul>
                          {r.unavailable_evidence.map((x) => (
                            <li key={x}>{x}: unknown</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                    <button
                      className="text"
                      onClick={() => {
                        setSelected(r.venture);
                        setTab("browse");
                      }}
                    >
                      Open venture record
                    </button>
                  </article>
                ))}
                <div className="questions">
                  <h3>Suggested diligence questions</h3>
                  <p className="muted">
                    Generic prompts for investigation, not findings about a
                    company.
                  </p>
                  <ol>
                    {comparison.questions.map((x) => (
                      <li key={x}>{x}</li>
                    ))}
                  </ol>
                </div>
              </section>
            )}
          </div>
        )}
        {tab === "analytics" && (
          <section className="analytics">
            {analysisError ? (
              <Status error>
                {analysisError}{" "}
                <button onClick={() => setRetry((x) => x + 1)}>Retry</button>
              </Status>
            ) : !analytics ? (
              <Status>Loading analytical views…</Status>
            ) : (
              <>
                <p className="notice">
                  {analytics.scope} Empty CSV cells represent unknown or not
                  recorded, never zero. Source age uses the exported as_of_date
                  in UTC.
                </p>
                {Object.entries(analytics.tables).map(([name, rows]) => (
                  <section className="analysis-table" key={name}>
                    <div className="section-head">
                      <div>
                        <h2>{label(name)}</h2>
                        <p className="muted">
                          {name === "programme_recognition"
                            ? "Recorded awards and distinct ventures by programme and year."
                            : name === "connection_coverage"
                              ? "Recorded relationships and distinct ventures; types overlap."
                              : "Observation and source counts per venture, with publication age."}
                        </p>
                      </div>
                      <a
                        className="download"
                        href={`/api/exports/${name}.csv`}
                        download
                      >
                        Download CSV ↓
                      </a>
                    </div>
                    <div
                      className="table-scroll"
                      role="region"
                      aria-label={label(name) + " table"}
                      tabIndex={0}
                    >
                      <table>
                        <thead>
                          <tr>
                            {Object.keys(rows[0] || {}).map((k) => (
                              <th key={k} scope="col">
                                {label(k)}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {rows.map((r, i) => (
                            <tr key={i}>
                              {Object.entries(r).map(([column, v]) => (
                                <td key={column}>
                                  {v === null
                                    ? "Unknown / not recorded"
                                    : column === "programme" ||
                                        column === "connection_type"
                                      ? label(String(v))
                                      : String(v)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </section>
                ))}
                <div className="raw-exports">
                  <h3>Evidence and proposals stay separate</h3>
                  <a href="/api/exports/raw_observations.csv" download>
                    Raw source observations CSV ↓
                  </a>
                  <a href="/api/exports/proposed_annotations.csv" download>
                    Proposed annotations CSV ↓
                  </a>
                  <p className="muted">
                    Power BI can import these database-generated CSVs. No .pbix
                    report, success rate or investment outcome analysis is
                    included.
                  </p>
                </div>
              </>
            )}
          </section>
        )}
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
    <App />
  </React.StrictMode>,
);
