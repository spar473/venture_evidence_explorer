import { useContext } from "react";
import type { ResearchDossier, ResearchObservation } from "./api-schema";
import { label } from "./labels";
import { ResearchTimeValue, ResearchNavigation } from "./research-shared";

/** A view of supplied assertions/dates, never new venture research or inference. */
export function ResearchOverview({ dossier }: { dossier: ResearchDossier }) {
  const { packet, subject } = dossier;
  const navigate = useContext(ResearchNavigation);
  const observations = packet.observations.filter((o) => o.subject_id === subject.subject_id);
  const source = (id: string) => packet.sources.find((s) => s.source_id === id);
  function claim(o: ResearchObservation) {
    const s = source(o.source_id);
    return (
      <p key={o.observation_id}>
        {o.paraphrase}
        <small className="research-time-basis">
          {label(o.assertion_nature)} · {label(o.source_relationship)} ·{" "}
          {s ? (
            <a href={s.url} target="_blank" rel="noreferrer">
              {s.title}
            </a>
          ) : (
            "Source unavailable"
          )}{" "}
          ·{" "}
          <a
            href={"#research-" + o.observation_id}
            onClick={(e) => {
              e.preventDefault();
              navigate(o.observation_id);
            }}
          >
            Inspect claim
          </a>
        </small>
      </p>
    );
  }
  const solution = observations.filter((o) => o.field === "solution");
  const users = observations.filter(
    (o) => o.field === "intended_user" || o.field === "documented_user",
  );
  const customers = observations.filter((o) =>
    [
      "target_customer_segment",
      "named_customer_organisation",
      "reported_paying_organisation",
      "procurement_budget_authority",
    ].includes(o.field),
  );
  const events = packet.events
    .filter((e) => e.subject_id === subject.subject_id)
    .map((event) => {
      const report = packet.event_reports.find((r) =>
        event.state_basis_report_ids.includes(r.report_id),
      );
      return { event, report, source: report ? source(report.source_id) : undefined };
    })
    .sort(
      (a, b) =>
        (a.source?.published_time.value || "9999").localeCompare(
          b.source?.published_time.value || "9999",
        ) || a.event.event_id.localeCompare(b.event.event_id),
    );
  return (
    <section className="research-overview" aria-label="Attributed venture overview">
      <h3>Venture at a glance</h3>
      <p className="muted">
        Supplied source descriptions · {label(subject.review.state)} · not independently accepted
      </p>
      <div className="research-overview-grid">
        <div>
          <h4>Reported solution</h4>
          {solution.length ? solution.map(claim) : <p>No sourced solution supplied.</p>}
        </div>
        <div>
          <h4>Intended and documented users</h4>
          {users.length ? users.map(claim) : <p>Users not established in supplied evidence.</p>}
        </div>
        <div>
          <h4>Customer and payer distinction</h4>
          {customers.map(claim)}
          {!observations.some((o) => o.field === "reported_paying_organisation") && (
            <p>Payer not established.</p>
          )}
          <p className="muted">
            A named user, adopter or target customer does not establish payment or procurement
            authority.
          </p>
        </div>
      </div>
      <h3>Evidence timeline</h3>
      <p className="muted">
        Ordered by source publication where known, not verified occurrence order. Dates keep their
        precision; publication does not establish event timing.
      </p>
      <ol className="research-timeline">
        {events.map(({ event, source: s }) => (
          <li key={event.event_id}>
            <div>
              <strong>{label(event.event_kind)}</strong> ·{" "}
              {event.scenario === "target" ? "Target / intention" : "Source-reported event"}
              <p>
                Occurrence: <ResearchTimeValue time={event.occurrence_time} />
                {event.scenario === "target" && (
                  <>
                    Target: <ResearchTimeValue time={event.target_time} />
                  </>
                )}
              </p>
              {event.identity_resolution === "unresolved_possible_duplicate" && (
                <p className="muted">
                  Possible duplicate financing report; distinct rounds and totals withheld.
                </p>
              )}
            </div>
            <div>
              <span>Source published: </span>
              {s ? (
                <>
                  <ResearchTimeValue time={s.published_time} />
                  <a href={s.url} target="_blank" rel="noreferrer">
                    {s.title}
                  </a>
                </>
              ) : (
                <>Unknown / not supplied</>
              )}
              <p>
                <a
                  href={"#research-" + event.event_id}
                  onClick={(e) => {
                    e.preventDefault();
                    navigate(event.event_id);
                  }}
                >
                  Inspect event and reports
                </a>
              </p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
