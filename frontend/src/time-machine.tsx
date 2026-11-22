/// <reference types="vite/client" />

import { useState } from "react";
import type {
  BacktestComp,
  BacktestEvent,
  BacktestField,
  BacktestNearest,
  BacktestPeerScore,
  BacktestResponse,
  BacktestReviewMetadata,
  WorkbenchPoint,
} from "./api-schema";
import { useResource } from "./hooks";
import { fieldLabel } from "./workbench-shared";
import { Trajectory } from "./workbench-trajectory";

const subjects = [
  { id: "public_supie", name: "Supie" },
  { id: "public_partly", name: "Partly" },
  { id: "discovery_halter", name: "Halter" },
] as const;
type SubjectId = (typeof subjects)[number]["id"];
const track = import.meta.env.VITE_TIME_MACHINE_TRACK === "strict" ? "strict" : "preview";
const defaultSubject =
  subjects.find((subject) => subject.id === import.meta.env.VITE_TIME_MACHINE_SUBJECT)?.id ??
  "public_supie";
const formatDay = new Intl.DateTimeFormat("en-NZ", {
  day: "numeric",
  month: "long",
  year: "numeric",
  timeZone: "UTC",
});
const formatMonth = new Intl.DateTimeFormat("en-NZ", {
  month: "long",
  year: "numeric",
  timeZone: "UTC",
});
const formatScore = new Intl.NumberFormat("en-NZ", {
  minimumFractionDigits: 3,
  maximumFractionDigits: 3,
});

function scoreText(value: number) {
  return formatScore.format(Number(value.toFixed(12)));
}

const fieldLabels: Record<string, string> = {
  description: "What it offered",
  product_type: "Product type",
  buyer: "Customer",
  business_model: "Business model",
  sector_normalised: "Sector",
  market_focus: "Market served",
  prototype: "Working product",
  paid_pilot_or_revenue: "Paying customers",
  full_time_team: "Full-time team",
  lead_investor_type: "Lead investor",
  round_size_band: "Round size",
  months_since_founding: "Months since founding",
};
const valueLabels: Record<string, string> = {
  new_zealand: "New Zealand",
  australia_new_zealand: "Australia and New Zealand",
  retail_ecommerce: "Online retail",
  food_beverage: "Food and beverage",
  saas: "Software subscription",
  small_business: "Small business",
  household: "Households",
  "lt0.5m": "Under NZ$500,000",
  "0.5m_to_lt2m": "NZ$500,000 to under NZ$2m",
  "2m_to_lt5m": "NZ$2m to under NZ$5m",
  "5m_to_lt10m": "NZ$5m to under NZ$10m",
  gte10m: "NZ$10m or more",
};
const barLabels: Record<string, string> = {
  similarity: "Overall similarity below 0.35",
  coverage: "Shared evidence below 0.35",
  product_customer: "Product and customer match below 0.25",
  subject_fields: "Fewer than five facts about the subject",
  peer_fields: "Fewer than five facts about the peer",
};
const statusLabels: Record<string, string> = {
  unknown: "Outcome unclear",
  reached_outcome: "Reached Series A or later",
  closed_before_outcome: "Closed before Series A",
  acquired_or_ipo_before_outcome: "Acquired or listed before Series A",
  observed_no_outcome: "Operating with no qualifying outcome recorded",
  lost_to_follow_up: "Follow-up was incomplete",
};
const roleLabels = {
  ceiling: "Ceiling",
  typical: "Typical",
  floor: "Floor",
  representative: "Representative",
};

function dateText(value: string) {
  if (value.length === 7) return formatMonth.format(new Date(`${value}-01T00:00:00Z`));
  if (value.length === 4) return value;
  return formatDay.format(new Date(`${value}T00:00:00Z`));
}

function valueText(field: BacktestField) {
  if (typeof field.value === "number" || field.name === "description") return field.value;
  return (
    valueLabels[field.value] ??
    field.value.replaceAll("_", " ").replace(/^./, (c) => c.toUpperCase())
  );
}

function useCase(id: SubjectId | null, today = false) {
  return useResource<BacktestResponse>(
    id
      ? `/backtest/${id}?track=${track}&witness_mode=strict&peer_history=${today ? "today" : "as_of_anchor"}`
      : null,
  );
}

function SourceLink({ source, label }: { source: BacktestField["source"]; label?: string }) {
  return (
    <a
      href={source.url}
      title={source.locator}
      target="_blank"
      rel="noreferrer"
      aria-label={label ? `${source.publisher} source for ${label}` : undefined}
    >
      {source.publisher}
    </a>
  );
}

function ReviewBadge({
  field,
  metadata,
}: {
  field: BacktestField;
  metadata?: BacktestReviewMetadata;
}) {
  const label =
    field.review_state === "ai_adjudicated"
      ? "AI-adjudicated" + (field.second_reading_matched ? " · second reading matched" : "")
      : field.review_state === "confirmed"
        ? "Human-confirmed"
        : "Proposed";
  return (
    <span
      className="tm-review"
      title={
        metadata
          ? `Checked by ${metadata.reviewed_by} on ${dateText(metadata.reviewed_on)}`
          : undefined
      }
    >
      {label}
    </span>
  );
}

function EvidenceDetails({
  companyId,
  fields,
  reviews,
}: {
  companyId: string;
  fields: BacktestField[];
  reviews: Map<string, BacktestReviewMetadata>;
}) {
  if (!fields.length) return null;
  return (
    <details className="tm-evidence-details">
      <summary>Review and source details</summary>
      <dl>
        {fields.map((field) => {
          const review = reviews.get(`${companyId}:${field.name}`);
          const second = review?.second_reading_result;
          return (
            <div key={field.name}>
              <dt>{fieldLabels[field.name]}</dt>
              <dd>{field.source.locator}</dd>
              {review && (
                <dd>
                  Checked by {review.reviewed_by} on {dateText(review.reviewed_on)}.
                  {second && (
                    <>
                      {" "}
                      {second.startsWith("Not compared")
                        ? "No second comparison was recorded."
                        : second === "Yes"
                          ? "The second reading matched."
                          : "The second reading differed."}
                    </>
                  )}
                </dd>
              )}
            </div>
          );
        })}
      </dl>
    </details>
  );
}

function story(data: BacktestResponse) {
  const name = data.subject.display_name;
  const date = dateText(data.subject.cutoff);
  if (data.abstention === "strict_gate")
    return "The strict evidence gate is still open for review.";
  if (data.abstention === "no_subject_evidence")
    return `We found no qualifying evidence about ${name} that was public by ${date}, so there is no comparison.`;
  const context = data.subject.entry_round_source
    ? `On ${date}, ${name} has just reported a seed round`
    : `It's ${date}`;
  if (data.comps?.length) {
    const count = data.comps.length;
    return `${context}. ${count} sourced ${count === 1 ? "comparison is" : "comparisons are"} available.`;
  }
  if (data.abstention === "no_outcomes")
    return `${context}. The closest companies match on entry evidence, but their later paths cannot be ranked from the records available here.`;
  if (
    data.qualifying_count === 0 &&
    data.nearest_available?.length &&
    data.nearest_available.every((row) => row.failed_bars.includes("product_customer"))
  )
    return `${context}, but none of the past companies has a close enough product and customer match.`;
  return `${context}, and there are fewer than three comparisons with enough shared evidence and a close enough match.`;
}

function nextEvidence(data: BacktestResponse) {
  if (data.abstention === "strict_gate")
    return "The strict view needs five human-confirmed facts for at least 15 eligible Partly peers.";
  if (data.abstention === "no_subject_evidence" || data.abstention === "too_few_subject_fields")
    return "A dated article or preserved company page with five facts about the product, customers, market, team or funding would make a comparison possible.";
  if (data.abstention === "no_outcomes")
    return "Dated funding, operating or closure records for the matching companies would help distinguish their paths.";
  return data.subject.company_id === "public_supie"
    ? "Dated records about other early online retailers, who bought from them and how they sold would give this comparison a firmer basis."
    : "Dated records about similar earlier businesses, their customers and their sales would give this comparison a firmer basis.";
}

function matchBand(peer: BacktestPeerScore) {
  return peer.similarity >= 0.6 ? "Close" : peer.similarity >= 0.35 ? "Loose" : "Not a comp";
}

function failedChecks(peer: BacktestPeerScore) {
  return peer.failed_bars.map((bar) => barLabels[bar] ?? bar).join(" · ");
}

function EventList({ items }: { items: BacktestEvent[] }) {
  if (!items.length)
    return <p className="wb-muted">No dated follow-up in the records available for this view.</p>;
  return (
    <ol className="tm-events">
      {items.map((event) => (
        <li key={event.event_id}>
          <time dateTime={event.date.value ?? undefined}>{dateText(event.date.value!)}</time>
          <span>
            <strong>{fieldLabel(event.kind)}</strong>
            {event.hindsight && <span className="tm-review">Hindsight</span>}
            <br />
            <SourceLink source={event.source} label={fieldLabel(event.kind)} />
            {event.hindsight && (
              <small className="tm-event-date">
                {event.source.witness_id ? "Public by" : "Source checked"}{" "}
                {dateText(event.source.available_on)}
              </small>
            )}
          </span>
        </li>
      ))}
    </ol>
  );
}

function Timeline({ name, events }: { name: string; events: BacktestEvent[] }) {
  if (!events.length) return null;
  const points: WorkbenchPoint[] = events.map((event) => ({
    lower_days: event.lower_days,
    upper_days: event.upper_days,
    is_anchor: false,
    claim: {
      claim_id: event.event_id,
      field: event.kind,
      value: event.kind,
      passage: event.source.locator,
      publisher: event.source.publisher,
      published_on: event.source.published_on ?? null,
      retrieved_on: event.source.available_on,
      date_value: event.date.value,
      date_precision: event.date.precision,
      url: event.source.url,
    },
  }));
  return (
    <details className="tm-chart">
      <summary>Show time chart</summary>
      <Trajectory
        rows={[{ company_id: name, display_name: name, points }]}
        title={`${name} since its recorded institutional round`}
        axisNote="Time begins at the recorded institutional round. Bands show dates known only within a range."
        onClaim={(claim) => window.open(claim.url, "_blank", "noopener,noreferrer")}
      />
    </details>
  );
}

function PeerCard({
  peer,
  reviews,
  abstainedFor,
}: {
  peer: BacktestNearest | BacktestComp;
  reviews: Map<string, BacktestReviewMetadata>;
  abstainedFor: BacktestResponse["abstention"];
}) {
  const isNearest = !("role" in peer);
  const fields = Object.entries(peer.field_scores);
  const matched = fields
    .filter(([, value]) => value > 0)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3);
  const different = fields
    .filter(([, value]) => value < 1)
    .sort((a, b) => a[1] - b[1])
    .slice(0, 3);
  function comparisons(dimensions: [string, number][]) {
    return (
      <ul className="tm-differences">
        {dimensions.map(([key, value]) => {
          const field = peer.fields.find((item) => item.name === key)!;
          return (
            <li key={key}>
              <a
                href={field.source.url}
                title={field.source.locator}
                target="_blank"
                rel="noreferrer"
                aria-label={`${fieldLabels[key]} source for ${peer.display_name}`}
              >
                {fieldLabels[key]}
              </a>
              <span>
                {key === "description" ? "Wording" : valueText(field)}
                {value > 0 && value < 1 ? " · partial match" : ""}
              </span>
              <span className="tm-field-meta">
                <time dateTime={field.source.available_on}>
                  {dateText(field.source.available_on)}
                </time>
                <ReviewBadge field={field} metadata={reviews.get(`${peer.company_id}:${key}`)} />
              </span>
            </li>
          );
        })}
      </ul>
    );
  }
  return (
    <article className="wb-card tm-peer">
      <header>
        <h3>{peer.display_name}</h3>
        <span className="tm-role">{isNearest ? "Not a comp" : roleLabels[peer.role]}</span>
      </header>
      <p className="wb-muted">Recorded institutional round · {dateText(peer.entry.value!)}</p>
      <p className="tm-score">
        <strong>
          {scoreText(peer.similarity)} · {matchBand(peer)}
        </strong>
        <span title="A score of 1 means all fields could be compared.">
          Shared evidence {scoreText(peer.coverage)}
        </span>
      </p>
      {isNearest && (
        <p className="tm-missed">
          {failedChecks(peer) ||
            (abstainedFor === "no_outcomes"
              ? "Outcome records were too sparse to assign comparison roles."
              : "Fewer than three peers cleared all checks.")}
        </p>
      )}
      {matched.length > 0 && (
        <>
          <h4>Matched</h4>
          {comparisons(matched)}
        </>
      )}
      {different.length > 0 && (
        <>
          <h4>Differed</h4>
          {comparisons(different)}
        </>
      )}
      <EvidenceDetails companyId={peer.company_id} fields={peer.fields} reviews={reviews} />
      <h4>What happened next</h4>
      <EventList items={peer.history.events} />
      <p className="wb-muted">
        This view ends {Math.floor(peer.history.follow_up_days / (365.25 / 12))} months after the
        recorded round.
      </p>
    </article>
  );
}

export function TimeMachine() {
  const [subjectId, setSubjectId] = useState<SubjectId>(defaultSubject);
  const [today, setToday] = useState(false);
  const [revealed, setRevealed] = useState(false);
  const historical = useCase(subjectId);
  const partly = useCase("public_partly");
  const halter = useCase("discovery_halter");
  const hindsight = useCase(today ? subjectId : null, true);
  const data = historical.data?.subject.company_id === subjectId ? historical.data : null;
  const peerData = today
    ? hindsight.data?.subject.company_id === subjectId
      ? hindsight.data
      : null
    : data;
  const visiblePeers = [...(peerData?.comps ?? []), ...(peerData?.nearest_available ?? [])];
  const comparison = peerData ?? data;
  const name = subjects.find((subject) => subject.id === subjectId)!.name;
  const reviews = new Map(
    data?.reveal?.evidence_reviews.map((review) => [
      `${review.company_id}:${review.field}`,
      review,
    ]),
  );
  for (const review of peerData?.reveal?.evidence_reviews ?? [])
    reviews.set(`${review.company_id}:${review.field}`, review);
  return (
    <div className="tm-page">
      {(data?.provisional ?? track === "preview") && (
        <p className="tm-banner">
          <strong>Provisional preview:</strong> AI-adjudicated evidence, not human-confirmed. Strict
          evidence gate not passed
          {data ? ` (${data.preview_peers} of ${data.required_peers} peers)` : ""}.
        </p>
      )}
      <header className="wb-header tm-header">
        <div>
          <h1>Time Machine</h1>
          <p className="tm-story" aria-live="polite">
            {comparison
              ? story(comparison)
              : historical.error
                ? "The case could not load. Reload to try again."
                : `Loading ${name}'s public record…`}
          </p>
        </div>
        <div className="tm-picker wb-toolbar">
          <label>
            Company to explore
            <select
              value={subjectId}
              onChange={(event) => {
                setSubjectId(event.target.value as SubjectId);
                setToday(false);
                setRevealed(false);
              }}
            >
              {subjects.map((subject) => (
                <option key={subject.id} value={subject.id}>
                  {subject.name}
                </option>
              ))}
            </select>
          </label>
          {[partly.data, halter.data].map(
            (caseData) =>
              caseData?.abstention === "no_subject_evidence" && (
                <p key={caseData.subject.company_id}>
                  <strong>{caseData.subject.display_name}</strong> · No qualifying evidence public
                  by {dateText(caseData.subject.cutoff)}.
                </p>
              ),
          )}
        </div>
      </header>

      {data && (
        <>
          <div className="tm-overview">
            {data.reveal && (
              <section className="wb-card tm-reveal" aria-labelledby="tm-reveal-heading">
                <h2 id="tm-reveal-heading">What happened next?</h2>
                <p className="wb-muted">See the first 36 months after the round.</p>
                <button
                  className="tm-reveal-button"
                  type="button"
                  aria-expanded={revealed}
                  aria-controls="tm-reveal-content"
                  onClick={() => setRevealed(!revealed)}
                >
                  {revealed ? "Hide the outcome" : `Reveal what happened to ${name}`}
                </button>
                <div id="tm-reveal-content">
                  {revealed && (
                    <div className="tm-reveal-content">
                      <strong className="tm-status">{statusLabels[data.reveal.status]}</strong>
                      <EventList items={data.reveal.events} />
                      {data.reveal.later_events.length > 0 && (
                        <details>
                          <summary>Events after 36 months</summary>
                          <EventList items={data.reveal.later_events} />
                        </details>
                      )}
                    </div>
                  )}
                </div>
              </section>
            )}
            <section className="wb-card tm-snapshot" aria-labelledby="tm-snapshot">
              <h2 id="tm-snapshot">{name}’s snapshot</h2>
              <p className="wb-muted">What was public by {dateText(data.subject.cutoff)}</p>
              {data.subject.fields.length ? (
                <dl className="tm-facts">
                  {data.subject.fields.map((field) => (
                    <div
                      key={field.name}
                      className={field.name === "description" ? "tm-description" : undefined}
                    >
                      <dt>{fieldLabels[field.name] ?? field.name}</dt>
                      <dd>
                        <strong>{valueText(field)}</strong>
                      </dd>
                      <dd className="tm-field-meta">
                        <time dateTime={field.source.available_on}>
                          {dateText(field.source.available_on)}
                        </time>
                        <SourceLink source={field.source} label={fieldLabels[field.name]} />
                      </dd>
                      <dd>
                        <ReviewBadge
                          field={field}
                          metadata={reviews.get(`${subjectId}:${field.name}`)}
                        />
                      </dd>
                    </div>
                  ))}
                </dl>
              ) : data.abstention === "no_subject_evidence" ? (
                <>
                  <p>
                    No entry facts met the evidence requirements. {data.covered_peer_ids?.length} of{" "}
                    {data.eligible_peer_ids?.length} earlier companies have at least five usable
                    facts.
                  </p>
                  {data.subject.entry.precision === "month" && (
                    <p>The entry record gives only a month. The search stops on its first day.</p>
                  )}
                </>
              ) : (
                <p>{nextEvidence(data)}</p>
              )}
              <EvidenceDetails
                companyId={subjectId}
                fields={data.subject.fields}
                reviews={reviews}
              />
            </section>
          </div>
          {revealed && data.reveal && <Timeline name={name} events={data.reveal.events} />}

          {comparison?.abstention && (
            <section className="wb-card tm-why" aria-labelledby="tm-why">
              <h2 id="tm-why">Why no comps yet</h2>
              <p>{nextEvidence(comparison)}</p>
              {!!comparison.nearest_candidates?.length && (
                <table>
                  <caption>
                    This table gives more weight to cases with more shared evidence.
                  </caption>
                  <thead>
                    <tr>
                      <th scope="col">Company</th>
                      <th scope="col">Check missed</th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparison.nearest_candidates.map((peer) => (
                      <tr key={peer.company_id}>
                        <th scope="row">
                          {peer.display_name}
                          <span className="wb-muted">
                            {scoreText(peer.similarity)} · {matchBand(peer)} · Shared evidence{" "}
                            {scoreText(peer.coverage)}
                          </span>
                        </th>
                        <td>{failedChecks(peer)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </section>
          )}

          {data.reveal && (
            <section className="tm-peers" aria-labelledby="tm-peers">
              <div className="tm-peer-heading">
                <h2 id="tm-peers">
                  {comparison?.abstention ? "Nearest available, not comps" : "Comparisons"}
                </h2>
                <label className="tm-toggle">
                  <input
                    type="checkbox"
                    checked={today}
                    onChange={(event) => setToday(event.target.checked)}
                  />
                  Include what we know today
                </label>
              </div>
              <p className="wb-muted" aria-live="polite">
                {today
                  ? "Hindsight is on. Later additions are marked."
                  : `Only what was known by ${dateText(data.subject.cutoff)}.`}
              </p>
              {comparison?.abstention && !!visiblePeers.length && (
                <p className="wb-muted">These cases are ordered by similarity score.</p>
              )}
              {peerData ? (
                <div className="tm-peer-grid">
                  {visiblePeers.map((peer) => (
                    <PeerCard
                      key={peer.company_id}
                      peer={peer}
                      reviews={reviews}
                      abstainedFor={peerData.abstention}
                    />
                  ))}
                  {!visiblePeers.length && (
                    <p>There are no shared facts to score for this selection.</p>
                  )}
                </div>
              ) : (
                <p role="status">
                  {hindsight.error
                    ? "Peer history could not load. Switch views to try again."
                    : "Loading peer history…"}
                </p>
              )}
            </section>
          )}
        </>
      )}

      <footer className="tm-footer">
        <span>
          Three historical cases, selected with their outcomes already known. The method was
          registered on 22 November 2026.
        </span>
        <a href="/time-machine/method">Read the method</a>
        <a href="/time-machine/results">See the case results</a>
      </footer>
    </div>
  );
}
