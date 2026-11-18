import type { Dispatch, SetStateAction } from "react";
import type { Venture } from "./types";
import { label } from "./labels";
import { Observation, Status } from "./shared";
import { useComparison, useVenturePage, type ComparisonSession } from "./hooks";
import { Pagination } from "./pagination";
import { FilterControls, type Filters } from "./filters";
import type { ComparisonRequest } from "./api-schema";
import type { Facets } from "./types";

export function ComparisonWorkspace({ session, setSession, filters, setFilters, facets, onOpen }: {
  session: ComparisonSession;
  setSession: Dispatch<SetStateAction<ComparisonSession>>;
  filters: Filters;
  setFilters: (filters: Filters) => void;
  facets: Facets | null;
  onOpen: (v: Venture) => void;
}) {
  const { programme, year, connection } = filters;
  const {subject, subjectName, subjectSearch, subjectOffset, mode, description} = session;
  const setSubject = (subject: string, subjectName: string) => setSession(s => ({...s, subject, subjectName, comparison: null, comparisonKey: null}));
  const setSubjectSearch = (subjectSearch: string) => setSession(s => ({...s, subjectSearch, subjectOffset: 0}));
  const setSubjectOffset = (subjectOffset: number) => setSession(s => ({...s, subjectOffset}));
  const setMode = (mode: ComparisonSession["mode"]) => setSession(s => ({...s, mode}));
  const setDescription = (description: string) => setSession(s => ({...s, description}));
  const subjects = useVenturePage({ q: subjectSearch }, subjectOffset, 25);
  const all = subjects.data?.items || [];
  const { comparison, setComparison, busy, compareError, runCompare } = useComparison(session, setSession, filters);
  const reset = () => setFilters({programme: "", year: "", connection: ""});
  const filterControls = <FilterControls filters={filters} setFilters={setFilters} facets={facets} />;
  return (
          <div className="comparison-workspace">
            <form className="compare-form" onSubmit={runCompare}>
              <div>
                <label>Find a subject
                  <input aria-label="Find a subject" value={subjectSearch} onChange={e => { setSubjectSearch(e.target.value); setSubjectOffset(0); }} placeholder="Search names or product descriptions" />
                </label>
                <label>
                  Subject venture
                  <select
                    aria-label="Subject venture"
                    value={subject}
                    onChange={(e) => {
                      setSubject(e.target.value, e.target.selectedOptions[0]?.textContent || e.target.value);
                      setComparison(null);
                    }}
                  >
                    <option value="">Use a description instead</option>
                    {subject && !all.some(v => v.venture_id === subject) && <option value={subject}>{subjectName || subject}</option>}
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
                    onChange={(e) => setMode(e.target.value as NonNullable<ComparisonRequest["mode"]>)}
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
              <Pagination total={subjects.data?.total || 0} offset={subjectOffset} limit={25} onChange={setSubjectOffset} label="Subject choices" />
              {subjects.error && <Status error>{subjects.error}</Status>}
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
                <button className="text" type="button" onClick={() => {
                  const url = URL.createObjectURL(new Blob([JSON.stringify(comparison.run, null, 2) + "\n"], {type: "application/json"}));
                  const link = document.createElement("a");
                  link.href = url; link.download = "comparison-run.json"; link.click();
                  URL.revokeObjectURL(url);
                }}>Download comparison run JSON ↓</button>
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
                  <p>Exploration policy: unreviewed source-checked publisher reports may contribute; reviewed acceptance is not implied.</p>
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
                          comparison.run.selected_observations.some(selected => selected.observation_id === o.observation_id),
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
                        onOpen(r.venture);
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
  );
}
