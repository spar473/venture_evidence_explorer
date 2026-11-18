import { useState, type Dispatch, type SetStateAction } from "react";
import type { Facets, VentureSummary } from "./types";
import type { Filters } from "./filters";
import { FilterControls } from "./filters";
import { label } from "./labels";
import { Status } from "./shared";
import { Pagination } from "./pagination";
import { useVenturePage } from "./hooks";

export type DirectorySession = {q: string; offset: number; limit: number};

export function Directory({ session, setSession, facets, filters, setFilters: updateFilters, onOpen, selectedId }: {
  session: DirectorySession;
  setSession: Dispatch<SetStateAction<DirectorySession>>;
  facets: Facets | null;
  filters: Filters;
  setFilters: (filters: Filters) => void;
  onOpen: (v: VentureSummary) => void;
  selectedId?: string;
}) {
  const {q, offset, limit} = session;
  const setOffset = (offset: number) => setSession(s => ({...s, offset}));
  const setLimit = (limit: number) => setSession(s => ({...s, limit, offset: 0}));
  const [retry, setRetry] = useState(0);
  const { data, loading, error } = useVenturePage({q, ...filters}, offset, limit, retry);
  const items = data?.items || [];
  const total = data?.total || 0;
  const setQ = (q: string) => setSession(s => ({...s, q, offset: 0}));
  const setFilters = (value: Filters) => { updateFilters(value); setOffset(0); };
  const reset = () => { setQ(""); setFilters({programme: "", year: "", connection: ""}); };
  const filterControls = <FilterControls facets={facets} filters={filters} setFilters={setFilters} />;
  return (<>
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
                      {total ? `${offset + 1}–${Math.min(offset + limit, total)}` : "0"} of {total} matching ventures
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
                              (selectedId === v.venture_id
                                ? "selected"
                                : "")
                            }
                          >
                            <td className="venture-identity">
                              <button
                                className="venture-open"
                                data-venture-id={v.venture_id}
                                onClick={() => onOpen(v)}
                                aria-haspopup="dialog"
                              >
                                {v.display_name}
                              </button>
                              <p>
                                {v.product_excerpt ||
                                  "No sourced product description recorded."}
                              </p>
                            </td>
                            <td data-label="Recognition">
                              {v.award_count ? (
                                v.recognitions.map((a) => (
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
                              {v.connection_types.length ? (
                                v.connection_types.map((connectionType) => (
                                  <div
                                    className="relationship"
                                    key={connectionType}
                                  >
                                    {label(connectionType)}
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
                              <span>{v.source_count} {v.source_count === 1 ? "source" : "sources"}</span>
                              {v.publication_dates.length ? v.publication_dates.map(d => d ? <time key={d} dateTime={d}>{d}</time> : <span key="unknown">Unknown / partial publication date</span>) : <span>Unknown / partial publication date</span>}
                              <span className="record-note">Published</span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
                <label className="page-size">Records per page
                  <select aria-label="Records per page" value={limit} onChange={e => { setLimit(Number(e.target.value)); setOffset(0); }}>
                    {[5, 25, 50, 100].map(size => <option key={size} value={size}>{size}</option>)}
                  </select>
                </label>
                <Pagination total={total} offset={offset} limit={limit} onChange={setOffset} label="Directory pages" />
                <p className="directory-footnote">
                  Programme and year refer to the same recorded award.
                  University relationships can overlap. “Not recorded” means
                  absent from this sample, not evidence of non-participation.
                </p>
              </section>
            </div>
  </>);
}
