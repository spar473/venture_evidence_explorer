import { createContext, useContext, useState } from "react";
import type { ResearchTime, ResearchReview, ResearchSource } from "./api-schema";
import { label } from "./labels";

export const ResearchNavigation = createContext<(id: string) => void>(() => {});
export function ResearchRefs({ids, title = "Evidence"}: {ids: string[]; title?: string}) {
  const navigate = useContext(ResearchNavigation);
  return ids.length ? <div className="research-refs"><span>{title}: </span>{ids.map(id => <a key={id} href={"#research-" + id} onClick={event => {event.preventDefault(); navigate(id);}}>{id}</a>)}</div> : null;
}
export function ResearchTimeValue({time}: {time: ResearchTime}) {
  return <span>{time.value === null ? "Unknown / not established" : `${time.value} (${time.precision} precision)`}<small className="research-time-basis">{time.basis}{time.unknown_reason ? ` · ${label(time.unknown_reason)}` : ""}</small></span>;
}
export function ResearchReviewValue({review}: {review: ResearchReview}) {
  return <div className="research-review"><strong>Review: {label(review.state)}</strong> · Actor: {label(review.actor_role)} · Checked {review.checked_on}<br />{review.rationale}{review.acceptance_review_id && <ResearchRefs ids={[review.acceptance_review_id]} title="Acceptance event" />}</div>;
}
/** Progressive disclosure preserves every imported field without presenting raw JSON as a conclusion. */
export function ResearchRaw({record}: {record: unknown}) {
  const [open, setOpen] = useState(false);
  return <details className="research-raw" onToggle={event => setOpen(event.currentTarget.open)}><summary>Inspect complete record</summary>{open && <pre tabIndex={0}>{JSON.stringify(record, null, 2)}</pre>}</details>;
}
export function ResearchLimitations({items}: {items: string[]}) {
  return items.length ? <ul className="research-limitations">{items.map((item, i) => <li key={i}>{item}</li>)}</ul> : null;
}
export function ResearchSourceCard({source}: {source: ResearchSource}) {
  return <article className="research-record" id={`research-${source.source_id}`} tabIndex={-1}>
    <h4><a href={source.url} target="_blank" rel="noreferrer">{source.title}<span className="sr-only"> (opens in a new tab)</span></a></h4>
    <code>{source.source_id}</code>
    <p>{source.publisher} · Publisher role: {label(source.publisher_role)}</p>
    <dl className="research-values">
      <div><dt>Published</dt><dd><ResearchTimeValue time={source.published_time} /></dd></div>
      <div><dt>Updated</dt><dd><ResearchTimeValue time={source.updated_time} /></dd></div>
      <div><dt>Retrieved</dt><dd>{source.retrieved_on}</dd></div>
      <div><dt>Access</dt><dd>{label(source.access_status)}</dd></div>
      <div><dt>Archive</dt><dd>{label(source.archive_status)}</dd></div>
      <div><dt>Historical availability</dt><dd>{source.historical_availability_verified ? "Recorded as verified; inspect basis" : "Not verified"}</dd></div>
    </dl>
    <ResearchLimitations items={source.limitations} />
    <ResearchRaw record={source} />
  </article>;
}
