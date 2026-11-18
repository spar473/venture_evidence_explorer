import type React from "react";
import type { PartialDate } from "./api-schema";
import type { Evidence } from "./types";
import { dateLabel, label } from "./labels";
export function Source({ e }: { e: Evidence }) {
  return (
    <div className="source">
      <a href={e.url} target="_blank" rel="noreferrer">
        {e.source_title}
        <span className="sr-only"> (opens in a new tab)</span>
      </a>
      <div>
        {e.publisher} · Published <strong>{dateLabel(e.published_at, e.publication_date)}</strong> · Retrieved{" "}
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
      {e.effective_review_status && e.effective_review_status !== e.review_status && <div className="muted">Current review: {label(e.effective_review_status)}</div>}
      {e.superseded && <div className="notice">Superseded / corrected. Retained for historical inspection; excluded from current matching.</div>}
      {e.relations?.map(relation => <div key={relation.relation_id}>Relation: {relation.relation_type} → <code>{relation.replacement_id}</code> · {relation.rationale}</div>)}
      {e.announcement_date && <div className="muted">Announcement date: {dateLabel(null, e.announcement_date)}</div>}
      {e.date_basis && (
        <div className="muted">
          Date basis: {label(e.date_basis)} · Effective date:{" "}
          {dateLabel(e.effective_at, e.effective_date)}
        </div>
      )}
    </div>
  );
}
export function Observation({ e }: { e: Evidence }) {
  return (
    <article className="evidence" id={e.observation_id}>
      <span className="eyebrow">{label(e.field || "")} · Publisher report</span>
      <p>{e.value_text}</p>
      {e.financial_value && <dl className="muted">{Object.entries(e.financial_value).map(([key, value]) => <div key={key}><dt>{label(key)}</dt><dd>{value === null ? "Unknown / not recorded" : typeof value === "object" ? dateLabel(null, value as PartialDate) : String(value)}</dd></div>)}</dl>}
      {e.event_value && <dl className="muted">{Object.entries(e.event_value).map(([key, value]) => <div key={key}><dt>{label(key)}</dt><dd>{value === null ? "Unknown / not recorded" : typeof value === "object" ? dateLabel(null, value as PartialDate) : String(value)}</dd></div>)}</dl>}
      <Source e={e} />
    </article>
  );
}
export function Status({
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
