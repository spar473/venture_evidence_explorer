import { useState } from "react";
import type { OutcomeCounts, OutcomeLibrary, OutcomeRow, WorkbenchClaim } from "./api-schema";
import { useResource } from "./hooks";
import { Status } from "./shared";
import { dateLabel, downloadCsv, fieldLabel, OutcomeStatus, statuses } from "./workbench-shared";
import { Trajectory } from "./workbench-trajectory";

const statusesInOrder = Object.keys(statuses) as (keyof typeof statuses)[];

function StatusBar({ data }: { data: OutcomeCounts }) {
  return (
    <>
      <div className="wb-status-bar" aria-hidden="true">
        {statusesInOrder.map(
          (key) =>
            (data.statuses[key] ?? 0) > 0 && (
              <span
                key={key}
                className={`wb-bar-${statuses[key][1]}`}
                style={{ flexGrow: data.statuses[key] }}
              />
            ),
        )}
      </div>
      <ul className="wb-status-counts">
        {statusesInOrder.map((key) => (
          <li key={key}>
            <OutcomeStatus status={key} />
            <strong>{data.statuses[key] ?? 0}</strong>
          </li>
        ))}
      </ul>
    </>
  );
}

function Story({ row, onClaim }: { row: OutcomeRow; onClaim: (claim: WorkbenchClaim) => void }) {
  const main = row.points.filter(
    (point) => !point.is_anchor && point.claim.field !== "last_verified_activity",
  );
  const points = main.length ? main : row.points;
  return (
    <article className="wb-comp">
      <h3>{row.display_name}</h3>
      <OutcomeStatus status={row.status} />
      <ul className="wb-story-claims">
        {points.map(({ claim }) => (
          <li key={claim.claim_id}>
            <button className="wb-text-button" onClick={() => onClaim(claim)}>
              {fieldLabel(claim.field)}
            </button>
            <p>
              {dateLabel(claim)}
              {row.notes[claim.claim_id] && ` · ${row.notes[claim.claim_id]}`}
            </p>
            <a href={claim.url} target="_blank" rel="noreferrer">
              {claim.publisher}
            </a>
          </li>
        ))}
      </ul>
    </article>
  );
}

export function OutcomeLibraryPage({ onClaim }: { onClaim: (claim: WorkbenchClaim) => void }) {
  const [sector, setSector] = useState("");
  const [vintage, setVintage] = useState("");
  const [endpoint, setEndpoint] = useState<OutcomeLibrary["endpoint"]>("primary");
  const [offset, setOffset] = useState(0);
  const [retry, setRetry] = useState(0);
  const params = new URLSearchParams({
    sector,
    endpoint,
    cohort: "A",
    offset: String(offset),
    limit: "8",
  });
  if (vintage) params.set("vintage", vintage);
  const { data, error, loading } = useResource<OutcomeLibrary>(
    "/workbench/outcomes?" + params,
    retry,
  );
  // Facets are seed-audit dimensions and do not change with a filter result.
  const [facets, rememberFacets] = useState<Pick<OutcomeLibrary, "sectors" | "vintages"> | null>(
    null,
  );
  if (data && facets === null) rememberFacets(data);
  const endpointLabel = endpoint === "primary" ? "Series A or later" : "Next priced equity round";

  return (
    <>
      <header className="wb-header">
        <h1>Outcome library</h1>
        <p>Public follow-up on NZ companies from first institutional pre-seed or seed.</p>
        <p className="wb-muted">
          Present-day view: counts come from the latest cohort audit and do not change with the
          precedent As-of date.
        </p>
      </header>
      <div className="wb-card wb-filters">
        <label>
          Cohort
          <select value="A" onChange={() => setOffset(0)}>
            <option value="A">A · NZ seed-entry</option>
            <option value="B" disabled>
              B · UoA programme-entry (not yet available)
            </option>
          </select>
        </label>
        <label>
          Sector
          <select
            value={sector}
            onChange={(event) => {
              setSector(event.target.value);
              setOffset(0);
            }}
          >
            <option value="">All sectors</option>
            {facets?.sectors.map((option) => (
              <option key={option}>{option}</option>
            ))}
          </select>
        </label>
        <label>
          Entry vintage
          <select
            value={vintage}
            onChange={(event) => {
              setVintage(event.target.value);
              setOffset(0);
            }}
          >
            <option value="">All vintages</option>
            {facets?.vintages.map((option) => (
              <option key={option}>{option}</option>
            ))}
          </select>
        </label>
        <label>
          Outcome
          <select
            value={endpoint}
            onChange={(event) => {
              setEndpoint(event.target.value as typeof endpoint);
              setOffset(0);
            }}
          >
            <option value="primary">Series A or later</option>
            <option value="secondary">Next priced equity round</option>
          </select>
        </label>
      </div>
      {loading ? (
        <Status>Loading cohort audit…</Status>
      ) : error ? (
        <Status error>
          {error} <button onClick={() => setRetry((value) => value + 1)}>Retry outcomes</button>
        </Status>
      ) : (
        data && (
          <>
            <section className="wb-card">
              <div className="wb-toolbar">
                <h2>36-month status · {endpointLabel}</h2>
                <button
                  type="button"
                  onClick={() =>
                    downloadCsv("outcome-library.csv", [
                      ["cohort", "as_of", "endpoint", "group", "denominator", "status", "count"],
                      ...[data.counts, ...data.sectors_comparison].flatMap((group) =>
                        statusesInOrder.map((key) => [
                          data.cohort,
                          data.as_of,
                          data.endpoint,
                          group.label,
                          group.denominator,
                          key,
                          group.statuses[key] ?? 0,
                        ]),
                      ),
                    ])
                  }
                >
                  Export outcome counts CSV
                </button>
              </div>
              <dl className="wb-metrics">
                <div>
                  <dd>{data.candidate_records}</dd>
                  <dt>Candidates reviewed · full audit</dt>
                </div>
                <div>
                  <dd>
                    {data.total} of {data.cohort_entries}
                  </dd>
                  <dt>Confirmed entries in view</dt>
                </div>
                <div>
                  <dd>{data.verified_closures}</dd>
                  <dt>Verified closures · any date</dt>
                </div>
                <div>
                  <dd>
                    {data.known_at_36_months} of {data.total}
                  </dd>
                  <dt>Outcome known at 36 months</dt>
                </div>
              </dl>
              <p className="wb-muted">Source-covered cohort · audit as of {data.as_of}</p>
              <StatusBar data={data.counts} />
            </section>
            <section className="wb-card">
              <h2>Company stories on one clock</h2>
              <Trajectory title="Outcome library swimlane" rows={data.rows} onClaim={onClaim} />
              <div className="wb-toolbar wb-pagination">
                <button
                  disabled={offset === 0}
                  onClick={() => setOffset(Math.max(0, offset - data.limit))}
                >
                  Previous companies
                </button>
                <span aria-live="polite">
                  {data.rows.length ? offset + 1 : 0}–{offset + data.rows.length} of {data.total}
                </span>
                <button
                  disabled={offset + data.limit >= data.total}
                  onClick={() => setOffset(offset + data.limit)}
                >
                  Next companies
                </button>
              </div>
            </section>
            {data.stories.length > 0 && (
              <section className="wb-card">
                <h2>Stories worth knowing</h2>
                <div className="wb-comp-grid">
                  {data.stories.map((row) => (
                    <Story key={row.company_id} row={row} onClaim={onClaim} />
                  ))}
                </div>
              </section>
            )}
            <div className="wb-overview-grid">
              <section className="wb-card">
                <h2>Entries by vintage</h2>
                <p>{data.total} confirmed entries in this view.</p>
                <div className="wb-table-scroll">
                  <table className="wb-table">
                    <thead>
                      <tr>
                        <th scope="col">Entry year</th>
                        <th scope="col">Companies</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.vintage_counts.map((row) => (
                        <tr key={row.year}>
                          <th scope="row">{row.year}</th>
                          <td>{row.entries}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {data.benchmarks.length > 0 && (
                  <>
                    <h3>Young Company Finance benchmarks</h3>
                    <ul>
                      {data.benchmarks.map((row) => (
                        <li key={row.description}>
                          <strong>{row.deals} deals</strong> · {row.description} ·{" "}
                          <a href={row.url} target="_blank" rel="noreferrer">
                            Source
                          </a>
                        </li>
                      ))}
                    </ul>
                  </>
                )}
              </section>
              <section className="wb-card">
                <h2>Cohort comparison</h2>
                <p>{vintage || "All vintages"} · Rates locked</p>
                {data.sectors_comparison
                  .filter((group) => group.label.startsWith("Healthtech"))
                  .map((group) => (
                    <p key={group.label} className="wb-muted">
                      Small denominator: {group.statuses.reached_outcome ?? 0} of{" "}
                      {group.denominator} healthtech entries reached the outcome. With{" "}
                      {group.denominator} entries, one company moves the share by about{" "}
                      {Math.round(100 / Math.max(group.denominator, 1))} points, so read these as
                      counts, not rates.
                    </p>
                  ))}
                <div className="wb-table-scroll">
                  <table className="wb-table">
                    <thead>
                      <tr>
                        <th scope="col">Status</th>
                        {data.sectors_comparison.map((group) => (
                          <th key={group.label} scope="col">
                            {group.label} · {group.denominator} entries
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {statusesInOrder.map((status) => (
                        <tr key={status}>
                          <th scope="row">
                            <OutcomeStatus status={status} />
                          </th>
                          {data.sectors_comparison.map((group) => (
                            <td key={group.label}>{group.statuses[status] ?? 0}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            </div>
          </>
        )
      )}
    </>
  );
}
