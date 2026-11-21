import type {
  NearestCandidate,
  PrecedentResponse,
  WorkbenchClaim,
  WorkbenchGates,
  WorkbenchRow,
} from "./api-schema";
import {
  type AnchorKind,
  type WitnessMode,
  anchors,
  dateLabel,
  downloadCsv,
  fieldLabel,
  GateProgress,
  WitnessDelay,
} from "./workbench-shared";
import { Trajectory } from "./workbench-trajectory";

const roleNames = {
  ceiling: "Ceiling",
  typical: "Typical",
  floor: "Floor",
  representative: "Representative comp",
} as const;

function checkLabel(value: string) {
  return value === "unknown" ? "?" : value === "yes" ? "Yes" : "No";
}

export function Checklist({
  data,
  onClaim,
}: {
  data: PrecedentResponse;
  onClaim: (claim: WorkbenchClaim) => void;
}) {
  const columns = [
    { title: data.subject.display_name, row: data.subject, role: "subject" },
    ...data.comps.map((comp) => ({
      title: roleNames[comp.role],
      row: comp.peer.row,
      role: comp.role,
    })),
  ];
  return (
    <section className="wb-card">
      <h2>Milestone checklist</h2>
      <p className="wb-muted">? means the dated evidence is open.</p>
      <div className="wb-table-scroll">
        <table className="wb-table">
          <thead>
            <tr>
              <th scope="col">Milestone</th>
              {columns.map((col) => (
                <th scope="col" key={col.role}>
                  {col.title}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.subject.milestones.map((item) => (
              <tr key={item.milestone}>
                <th scope="row">{fieldLabel(item.milestone)}</th>
                {columns.map((col) => {
                  const cell = col.row.milestones.find(
                    (value) => value.milestone === item.milestone,
                  );
                  const claims =
                    cell?.claim_ids.flatMap((id) =>
                      col.row.claims.filter((claim) => claim.claim_id === id),
                    ) ?? [];
                  return (
                    <td key={col.role}>
                      <strong>{checkLabel(cell?.value || "unknown")}</strong>
                      {claims.map((claim, i) => (
                        <button
                          className="wb-text-button"
                          key={claim.claim_id}
                          onClick={() => onClaim(claim)}
                          aria-label={`Evidence ${i + 1} for ${col.title}: ${fieldLabel(item.milestone)}`}
                        >
                          Source {i + 1}
                        </button>
                      ))}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {data.questions.length > 0 && (
        <>
          <h3>Diligence questions</h3>
          <ul>
            {data.questions.map((question) => (
              <li key={question}>{question}</li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}

const score = (value: number | null | undefined) => (value == null ? "?" : value.toFixed(2));

function Bar({
  label,
  value,
  min,
  met,
}: {
  label: string;
  value: number | null;
  min: number;
  met: boolean;
}) {
  return (
    <div className={met ? "wb-bar wb-bar-met" : "wb-bar"}>
      <dt>{label}</dt>
      <dd>
        <strong>{score(value)}</strong> of {min.toFixed(2)} required · {met ? "clears" : "short"}
      </dd>
    </div>
  );
}

function nextEvidence(candidate: NearestCandidate) {
  const steps: string[] = [];
  const clinical = candidate.dimensions.find((item) => item.dimension === "Clinical workflow");
  if (!candidate.meets_clinical) {
    steps.push(
      clinical && clinical.coverage > 0
        ? "The clinical workflow fields recorded on both sides do not match closely enough. A peer with the same modality, clinical user or output would clear this bar."
        : "No clinical workflow field is witnessed on both sides. Witnessed modality, clinical user and output for both would let this bar be scored.",
    );
  }
  if (candidate.missing_on_peer.length) {
    steps.push(
      `Witnessed values for this peer's ${candidate.missing_on_peer.map(fieldLabel).join(", ")} at its anchor.`,
    );
  }
  if (!candidate.meets_coverage || !candidate.meets_similarity) {
    steps.push("More fields witnessed on both sides, so more dimensions can be compared.");
  }
  return steps;
}

function WhyNoComps({ data }: { data: PrecedentResponse }) {
  const t = data.thresholds;
  const candidates = data.nearest_candidates ?? [];
  const subjectGaps = candidates[0]?.missing_on_subject ?? [];
  return (
    <section className="wb-why" aria-labelledby="why-no-comps">
      <h3 id="why-no-comps">Why no comps yet</h3>
      <p>
        A comp needs {t.min_peers} peers that each clear all three bars: clinical workflow
        similarity of at least {t.min_clinical_similarity.toFixed(2)}, overall similarity of at
        least {t.min_similarity.toFixed(2)} and weighted evidence coverage of at least{" "}
        {t.min_coverage.toFixed(2)}. {data.peers.length} of {data.peer_count_evaluated} alignable
        companies clear them at this anchor.
      </p>
      {candidates.length ? (
        <>
          <p className="wb-muted">
            The nearest candidates are shown to explain the gap. They are not comps, and their
            outcomes are not shown.
          </p>
          <div className="wb-candidates">
            {candidates.map((candidate) => (
              <article key={candidate.company_id} className="wb-candidate">
                <h4>{candidate.display_name}</h4>
                <dl className="wb-bars">
                  <Bar
                    label="Clinical workflow"
                    value={candidate.clinical_similarity}
                    min={t.min_clinical_similarity}
                    met={candidate.meets_clinical}
                  />
                  <Bar
                    label="Overall similarity"
                    value={candidate.similarity}
                    min={t.min_similarity}
                    met={candidate.meets_similarity}
                  />
                  <Bar
                    label="Evidence coverage"
                    value={candidate.coverage}
                    min={t.min_coverage}
                    met={candidate.meets_coverage}
                  />
                </dl>
                <details>
                  <summary>Per-dimension breakdown</summary>
                  <dl className="wb-dimensions">
                    {candidate.dimensions.map((item) => (
                      <div key={item.dimension}>
                        <dt>{item.dimension}</dt>
                        <dd>
                          {score(item.similarity)} similarity · coverage {item.coverage.toFixed(2)}
                        </dd>
                      </div>
                    ))}
                  </dl>
                </details>
                <p>
                  <strong>Missing on this peer</strong>{" "}
                  {candidate.missing_on_peer.length
                    ? candidate.missing_on_peer.map(fieldLabel).join(", ")
                    : "Nothing the subject has."}
                </p>
                <p>
                  <strong>What would clear the bar</strong>
                </p>
                <ul>
                  {nextEvidence(candidate).map((step) => (
                    <li key={step}>{step}</li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </>
      ) : (
        <p>No alignable company shares a witnessed comparison field with this subject yet.</p>
      )}
      {subjectGaps.length > 0 && (
        <p>
          <strong>Subject evidence to add</strong> {subjectGaps.map(fieldLabel).join(", ")}. Each
          witnessed value adds a field that peers can be compared on. The thresholds do not change.
        </p>
      )}
    </section>
  );
}

function Comps({
  data,
  onClaim,
  onEvidence,
}: {
  data: PrecedentResponse;
  onClaim: (claim: WorkbenchClaim) => void;
  onEvidence: (companyId: string) => void;
}) {
  return (
    <section className="wb-card">
      <header className="wb-toolbar">
        <h2>Ceiling, typical and floor comps</h2>
      </header>
      {data.subject.kind === "research_project" && (
        <p className="wb-muted">
          Subject today vs peers at their {anchors[data.anchor_kind].toLowerCase()} · Subject as of{" "}
          {data.as_of}
        </p>
      )}
      {data.abstention && <p className="wb-notice">{data.abstention}</p>}
      {data.comps.length === 0 && <WhyNoComps data={data} />}
      {data.comps.length > 0 && (
        <div className="wb-comp-grid">
          {data.comps.map((comp) => {
            const { row, similarity, coverage, dimensions } = comp.peer;
            const outcome = row.comp_outcome;
            const matches = [...new Set(dimensions.flatMap((item) => item.matched_fields))].map(
              fieldLabel,
            );
            const differences = [
              ...new Set(dimensions.flatMap((item) => item.different_fields)),
            ].map(fieldLabel);
            return (
              <article key={comp.role} className="wb-comp">
                <span className="wb-role">{roleNames[comp.role]}</span>
                <h3>{row.display_name}</h3>
                {outcome && (
                  <p>
                    <strong>{outcome.label}</strong> ·{" "}
                    <button
                      className="wb-text-button"
                      onClick={() => onClaim(outcome.claim)}
                      aria-label={`Status evidence for ${row.display_name} (${outcome.date_value})`}
                    >
                      {outcome.date_value} ({outcome.date_precision} precision)
                    </button>
                  </p>
                )}
                <p>{comp.reason}</p>
                <p>
                  <strong>{similarity.toFixed(2)}</strong> similarity · {coverage.toFixed(2)}{" "}
                  comparable coverage
                </p>
                <dl className="wb-dimensions">
                  {dimensions.map((item) => (
                    <div key={item.dimension}>
                      <dt>{item.dimension}</dt>
                      <dd>
                        {item.similarity?.toFixed(2) ?? "?"} · coverage {item.coverage.toFixed(2)}
                      </dd>
                    </div>
                  ))}
                </dl>
                <p>
                  <strong>Matches</strong>{" "}
                  {matches.length ? matches.join(", ") : "No shared match recorded."}
                </p>
                <p>
                  <strong>Differences</strong>{" "}
                  {differences.length
                    ? differences.join(", ")
                    : "No supported difference in available fields."}
                </p>
                <h4>Peer snapshot at anchor</h4>
                {row.snapshot.length ? (
                  <ul>
                    {row.snapshot.map((claim) => (
                      <li key={claim.claim_id + claim.field}>
                        <button className="wb-text-button" onClick={() => onClaim(claim)}>
                          {fieldLabel(claim.field)} · {claim.value}
                        </button>
                        <WitnessDelay claim={claim} />
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p>
                    {row.gaps.find((gap) => gap.startsWith("Same-stage")) ||
                      "Same-stage evidence is withheld."}
                  </p>
                )}
                <button onClick={() => onEvidence(row.company_id)}>Evidence matrix</button>
              </article>
            );
          })}
        </div>
      )}
      {data.no_verified_closure && data.peers.length >= 3 && (
        <p>No verified closure among the closest peers.</p>
      )}
      <details className="wb-peers">
        <summary>All {data.peers.length} similar peers</summary>
        {!data.peers.length && (
          <p>{data.peer_count_evaluated} alignable companies reviewed for witnessed similarity.</p>
        )}
        <ol>
          {data.peers.map(({ row, similarity, coverage }) => (
            <li key={row.company_id}>
              <strong>{row.display_name}</strong>
              {" · "}
              {similarity.toFixed(2)} similarity · {coverage.toFixed(2)} coverage ·{" "}
              {row.comp_outcome
                ? `${row.comp_outcome.label} · ${row.comp_outcome.date_value}`
                : "Current status unresolved"}
            </li>
          ))}
        </ol>
      </details>
    </section>
  );
}

export function Overview({
  data,
  gates,
  gateError,
  cohort,
  onCohort,
  onAnchor,
  onWitnessMode,
  onClaim,
  onOutlook,
  onEvidence,
}: {
  data: PrecedentResponse;
  gates: WorkbenchGates | null;
  gateError: string;
  cohort: "curated" | "similar";
  onCohort: (cohort: "curated" | "similar") => void;
  onAnchor: (kind: AnchorKind) => void;
  onClaim: (claim: WorkbenchClaim) => void;
  onWitnessMode: (mode: WitnessMode) => void;
  onOutlook: () => void;
  onEvidence: (companyId: string) => void;
}) {
  const peers = cohort === "curated" ? data.curated : data.peers.map((peer) => peer.row);
  const rows: WorkbenchRow[] = [data.subject, ...peers].filter((row) => row.points.length > 0);
  const missing =
    cohort === "curated"
      ? data.curated
          .filter((row) => row.not_alignable)
          .map((row) => ({
            company_id: row.company_id,
            display_name: row.display_name,
            reason: row.not_alignable,
          }))
      : data.not_alignable;

  return (
    <>
      <section className="wb-card">
        <div className="wb-toolbar">
          <h2>Where comparable NZ ventures went</h2>
          <button
            type="button"
            disabled={!rows.length}
            onClick={() =>
              downloadCsv("precedent-trajectories.csv", [
                [
                  "company",
                  "event",
                  "reported_date",
                  "precision",
                  "lower_days",
                  "upper_days",
                  "source",
                  "claim_id",
                  "as_of",
                ],
                ...rows.flatMap((row) =>
                  row.points.map(({ claim, lower_days, upper_days }) => [
                    row.display_name,
                    claim.field,
                    claim.date_value,
                    claim.date_precision,
                    lower_days,
                    upper_days,
                    claim.url,
                    claim.claim_id,
                    data.as_of,
                  ]),
                ),
              ])
            }
          >
            Export trajectory CSV
          </button>
        </div>
        <div className="wb-toolbar wb-chart-controls">
          <label>
            Align at{" "}
            <select
              value={data.anchor_kind}
              onChange={(event) => onAnchor(event.target.value as AnchorKind)}
            >
              {Object.entries(anchors).map(([value, name]) => (
                <option value={value} key={value}>
                  {name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Peer witness mode{" "}
            <select
              value={data.witness_mode}
              onChange={(event) => onWitnessMode(event.target.value as WitnessMode)}
            >
              <option value="strict">Strict · at anchor</option>
              <option value="contemporaneous">Contemporaneous · up to 90 days later</option>
            </select>
          </label>
          <div className="wb-toggle" role="group" aria-label="Peer set">
            <button
              type="button"
              aria-pressed={cohort === "curated"}
              onClick={() => onCohort("curated")}
            >
              Curated precedents
            </button>
            <button
              type="button"
              aria-pressed={cohort === "similar"}
              onClick={() => onCohort("similar")}
            >
              Similar cohort
            </button>
          </div>
        </div>
        {data.subject.anchor && (
          <p className="wb-muted">Subject anchor · {dateLabel(data.subject.anchor.claim)}</p>
        )}
        {data.witness_mode === "contemporaneous" && (
          <p className="wb-muted">
            Late workflow and buyer evidence can fill gaps in peer snapshots. Badges show the
            witness delay.
          </p>
        )}
        <Trajectory rows={rows} onClaim={onClaim} title="Aligned venture trajectories" />
        {missing.length > 0 && (
          <details>
            <summary>Not alignable · {missing.length}</summary>
            <ul>
              {missing.map((row) => (
                <li key={row.company_id}>
                  <strong>{row.display_name}</strong> · {row.reason}
                </li>
              ))}
            </ul>
          </details>
        )}
      </section>
      <div className="wb-overview-grid">
        <Comps data={data} onClaim={onClaim} onEvidence={onEvidence} />
        <Checklist data={data} onClaim={onClaim} />
      </div>
      <section className="wb-card">
        <h2>Outcome rates locked</h2>
        <p className="wb-muted">
          Present-day gate{gates ? ` · audit ${gates.as_of}` : ""}. It does not change with the
          As-of date.
        </p>
        {gates ? <GateProgress gates={gates} /> : <p>{gateError || "Loading the cohort audit…"}</p>}
        <button onClick={onOutlook}>View Outlook</button>
      </section>
    </>
  );
}
