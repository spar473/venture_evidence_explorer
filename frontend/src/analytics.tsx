import { useState } from "react";
import { label } from "./labels";
import { Status } from "./shared";
import { useResource } from "./hooks";

import type { AnalyticsResponse } from "./api-schema";
export function AnalyticsWorkspace() {
  const [retry, setRetry] = useState(0);
  const { data: analytics, error: analysisError } = useResource<AnalyticsResponse>(
    "/analytics",
    retry,
  );
  return (
    <section className="analytics">
      {analysisError ? (
        <Status error>
          {analysisError} <button onClick={() => setRetry((x) => x + 1)}>Retry</button>
        </Status>
      ) : !analytics ? (
        <Status>Loading analytical views…</Status>
      ) : (
        <>
          <p className="notice">
            {analytics.scope} Empty CSV cells represent unknown or not recorded, never zero. Source
            age uses the exported as_of_date in UTC.
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
                <a className="download" href={`/api/exports/${name}.csv`} download>
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
                              : column === "programme" || column === "connection_type"
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
              Power BI can import these database-generated CSVs. No .pbix report, success rate or
              investment outcome analysis is included.
            </p>
          </div>
        </>
      )}
    </section>
  );
}
