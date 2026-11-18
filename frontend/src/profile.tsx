import type { Venture } from "./types";
import { dateLabel, label, unknown } from "./labels";
import { Observation, Source } from "./shared";
export function Profile({
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
            Event date: {dateLabel(a.event_date, a.event_interval)} · Award year is not an
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

