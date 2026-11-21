import type {
  ResearchObservation,
  ResearchEvent,
  ResearchReport,
  ResearchReadiness,
  ResearchUnknown,
  ResearchCase,
} from "./api-schema";
import { label } from "./labels";
import {
  ResearchLimitations,
  ResearchRaw,
  ResearchRefs,
  ResearchReviewValue,
  ResearchTimeValue,
} from "./research-shared";

type SubjectName = (id: string) => string;
export function ResearchObservationCard({
  record,
  subjectName,
}: {
  record: ResearchObservation;
  subjectName: SubjectName;
}) {
  const money = record.money;
  return (
    <article
      className="research-record research-observation"
      id={`research-${record.observation_id}`}
      tabIndex={-1}
    >
      <div className="section-head">
        <h4>{label(record.field)}</h4>
        <span className="tag">{label(record.assertion_nature)}</span>
      </div>
      <p className="muted">
        {subjectName(record.subject_id)} · <code>{record.observation_id}</code>
      </p>
      <p className="research-claim">{record.paraphrase}</p>
      <p>
        Claim responsibility: <strong>{label(record.source_relationship)}</strong> ·{" "}
        {record.speaker_context}
      </p>
      <p className="muted">Passage: {record.locator}</p>
      <ResearchRefs ids={[record.source_id]} title="Source version" />
      <ResearchReviewValue review={record.review} />
      {money && (
        <dl className="research-values research-money">
          <div>
            <dt>Reported amount</dt>
            <dd>
              {money.amount} · {label(money.qualifier)}
            </dd>
          </div>
          <div>
            <dt>Currency</dt>
            <dd>
              {money.currency.value ||
                `Unknown · ${label(money.currency.unknown_reason || "not recorded")}`}
            </dd>
          </div>
          <div>
            <dt>Monetary scope</dt>
            <dd>{label(money.scope)}</dd>
          </div>
          <div>
            <dt>Unit / interval</dt>
            <dd>
              {label(money.unit)} · {label(money.billing_interval)}
            </dd>
          </div>
        </dl>
      )}
      <details className="research-context">
        <summary>Dates, scope and limitations</summary>
        <dl className="research-values">
          <div>
            <dt>Effective / occurrence</dt>
            <dd>
              <ResearchTimeValue time={record.effective_time} />
            </dd>
          </div>
          <div>
            <dt>Source context</dt>
            <dd>
              <ResearchTimeValue time={record.context_time} />
            </dd>
          </div>
          <div>
            <dt>Target</dt>
            <dd>
              <ResearchTimeValue time={record.target_time} />
            </dd>
          </div>
          <div>
            <dt>Product scope</dt>
            <dd>{record.scope.product}</dd>
          </div>
          <div>
            <dt>Geography</dt>
            <dd>
              {record.scope.geographies.join(", ") ||
                `Unspecified · ${label(record.scope.geography_unknown_reason || "not recorded")}`}
              <small className="research-time-basis">{record.scope.geography_basis}</small>
            </dd>
          </div>
        </dl>
        <ResearchRefs
          ids={record.related_party_id ? [record.related_party_id] : []}
          title="Named party"
        />
        <ResearchRefs ids={record.conflict_ids} title="Reconciliation cases" />
        <ResearchLimitations items={record.limitations} />
      </details>
      <ResearchRaw record={record} />
    </article>
  );
}
export function ResearchEventCard({
  event,
  reports,
}: {
  event: ResearchEvent;
  reports: ResearchReport[];
}) {
  return (
    <article
      className="research-record research-event"
      id={`research-${event.event_id}`}
      tabIndex={-1}
    >
      <div className="section-head">
        <h4>{label(event.event_kind)}</h4>
        <span className="tag">
          {event.scenario === "target" ? "Target / intention" : "Reported occurrence"}
        </span>
      </div>
      <code>{event.event_id}</code>
      <p>
        Source-reported state: <strong>{label(event.event_state)}</strong> · Identity:{" "}
        {label(event.identity_resolution)}
      </p>
      <dl className="research-values">
        <div>
          <dt>Occurrence</dt>
          <dd>
            <ResearchTimeValue time={event.occurrence_time} />
          </dd>
        </div>
        <div>
          <dt>Target</dt>
          <dd>
            <ResearchTimeValue time={event.target_time} />
          </dd>
        </div>
      </dl>
      <ResearchReviewValue review={event.review} />
      {event.scenario === "target" && (
        <p className="notice">
          A target year passing does not establish occurrence, failure or cancellation.
        </p>
      )}
      <ResearchRefs ids={event.state_basis_report_ids} title="State-basis reports" />
      {reports.map((report) => (
        <details
          className="research-report"
          key={report.report_id}
          id={`research-${report.report_id}`}
          tabIndex={-1}
        >
          <summary>
            {report.report_id} · {label(report.reported_event_state)}
          </summary>
          <p>
            Claim responsibility: {label(report.source_relationship)} ·{" "}
            {label(report.assertion_nature)}
          </p>
          <p>Passage: {report.locator}</p>
          <ResearchRefs ids={[report.source_id]} title="Source version" />
          <ResearchRefs ids={report.observation_ids} />
          <dl className="research-values">
            <div>
              <dt>Reported occurrence</dt>
              <dd>
                <ResearchTimeValue time={report.reported_occurrence_time} />
              </dd>
            </div>
            <div>
              <dt>Reported target</dt>
              <dd>
                <ResearchTimeValue time={report.reported_target_time} />
              </dd>
            </div>
          </dl>
          <ResearchReviewValue review={report.review} />
          <ResearchLimitations items={report.limitations} />
          <ResearchRaw record={report} />
        </details>
      ))}
      <ResearchLimitations items={event.limitations} />
      <ResearchRaw record={event} />
    </article>
  );
}
export function ResearchReadinessCard({
  record,
  subjectName,
}: {
  record: ResearchReadiness;
  subjectName: SubjectName;
}) {
  return (
    <article
      className="research-record research-readiness"
      id={`research-${record.readiness_id}`}
      tabIndex={-1}
    >
      <h4>{record.question}</h4>
      <code>{record.readiness_id}</code>
      <p>
        <strong>{label(record.assessment)}</strong> · {label(record.mode)}
      </p>
      <p>
        Subjects: {record.subject_ids.map(subjectName).join(", ")} · Research as of{" "}
        {record.evidence_cutoff}
      </p>
      <p className="muted">
        Research cutoff; historical web availability is not established. This is a question-specific
        assessment, not a venture score or relevance judgment.
      </p>
      <details>
        <summary>Evidence requirements · {record.requirements.length}</summary>
        {record.requirements.map((requirement) => (
          <div
            className="research-requirement"
            key={requirement.requirement_id}
            id={`research-${requirement.requirement_id}`}
            tabIndex={-1}
          >
            <h5>{requirement.description}</h5>
            <p>
              {label(requirement.status)} · Required subjects:{" "}
              {requirement.required_subject_ids.map(subjectName).join(", ")}
            </p>
            <ResearchRefs ids={requirement.supporting_observation_ids} />
            <ResearchRefs ids={requirement.missing_unknown_ids} title="Unknowns" />
            <ResearchRefs ids={requirement.unresolved_case_ids} title="Unresolved cases" />
          </div>
        ))}
      </details>
      <h5>Supported conclusions</h5>
      {!record.supported_conclusions.length && (
        <p>No supported business conclusion supplied for this question.</p>
      )}
      {record.supported_conclusions.map((conclusion) => (
        <div
          key={conclusion.conclusion_id}
          className="research-conclusion"
          id={`research-${conclusion.conclusion_id}`}
          tabIndex={-1}
        >
          <p>{conclusion.text}</p>
          <p className="muted">
            Applies to: {conclusion.subject_ids.map(subjectName).join(", ")} ·{" "}
            {label(conclusion.inference_type)}
          </p>
          <ResearchRefs ids={conclusion.basis_observation_ids} />
          <ResearchRefs ids={conclusion.source_ids} title="Sources" />
          <ResearchReviewValue review={conclusion.review} />
        </div>
      ))}
      <h5>Conclusions withheld</h5>
      <ul className="research-withheld">
        {record.withheld_conclusions.map((text, i) => (
          <li key={i}>{text}</li>
        ))}
      </ul>
      <p>{record.rationale}</p>
      <ResearchReviewValue review={record.review} />
      <ResearchRefs ids={record.missing_unknown_ids} title="Unknowns" />
      <ResearchRefs ids={record.unresolved_case_ids} title="Unresolved cases" />
      <ResearchRaw record={record} />
    </article>
  );
}
export function ResearchUnknownCard({ record }: { record: ResearchUnknown }) {
  return (
    <article
      className="research-record research-unknown"
      id={`research-${record.unknown_id}`}
      tabIndex={-1}
    >
      <h4>{label(record.field)}</h4>
      <code>{record.unknown_id}</code>
      <p>
        <strong>Unknown</strong> · {label(record.reason)}
      </p>
      <p>{record.explanation}</p>
      <p className="muted">
        Scope: {record.scope.product} · Assessed {record.as_of}
      </p>
      <ResearchRefs ids={record.inspected_source_ids} title="Inspected sources" />
      <ResearchRefs ids={record.access_gap_ids} title="Access gaps" />
      <ResearchReviewValue review={record.review} />
      <ResearchRaw record={record} />
    </article>
  );
}
export function ResearchCaseCard({ record }: { record: ResearchCase }) {
  return (
    <article
      className="research-record research-case"
      id={`research-${record.case_id}`}
      tabIndex={-1}
    >
      <h4>
        {label(record.case_kind)} · {record.status}
      </h4>
      <code>{record.case_id}</code>
      <p>{record.rationale}</p>
      <p>Required resolution: {record.required_resolution}</p>
      <p className="notice">
        Aggregation{" "}
        {record.aggregation_allowed
          ? "recorded as allowed; inspect decision"
          : "prohibited while unresolved"}
        .
      </p>
      <ResearchRefs ids={record.event_ids} title="Event candidates" />
      <ResearchRefs ids={record.observation_ids} />
      <ResearchRaw record={record} />
    </article>
  );
}
