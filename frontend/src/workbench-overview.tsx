import type {PrecedentResponse, WorkbenchClaim, WorkbenchGates, WorkbenchRow} from "./api-schema";
import {type AnchorKind, anchors, dateLabel, downloadCsv, fieldLabel, GateProgress, OutcomeStatus} from "./workbench-shared";
import {Trajectory} from "./workbench-trajectory";

const roleNames = {ceiling: "Ceiling", typical: "Typical", floor: "Floor"} as const;
const roles = Object.keys(roleNames) as (keyof typeof roleNames)[];

function checkLabel(value: string) { return value === "unknown" ? "?" : value === "yes" ? "Yes" : "No"; }

export function Checklist({data, onClaim}: {data: PrecedentResponse; onClaim: (claim: WorkbenchClaim) => void}) {
  const columns = [
    {title: data.subject.display_name, row: data.subject, role: "subject"},
    ...data.comps.map(comp => ({title: roleNames[comp.role], row: comp.peer.row, role: comp.role})),
  ];
  return <section className="wb-card">
    <h2>Milestone checklist</h2>
    <p className="wb-muted">? means the dated evidence is open.</p>
    <div className="wb-table-scroll"><table className="wb-table">
      <thead><tr><th scope="col">Milestone</th>{columns.map(col => <th scope="col" key={col.role}>{col.title}</th>)}</tr></thead>
      <tbody>{data.subject.milestones.map(item => <tr key={item.milestone}>
        <th scope="row">{fieldLabel(item.milestone)}</th>
        {columns.map(col => {
          const cell = col.row.milestones.find(value => value.milestone === item.milestone);
          const claims = cell?.claim_ids.flatMap(id => col.row.claims.filter(claim => claim.claim_id === id)) ?? [];
          return <td key={col.role}><strong>{checkLabel(cell?.value || "unknown")}</strong>
            {claims.map((claim, i) => <button className="wb-text-button" key={claim.claim_id}
              onClick={() => onClaim(claim)} aria-label={`Evidence ${i + 1} for ${col.title}: ${fieldLabel(item.milestone)}`}>Source {i + 1}</button>)}</td>;
        })}
      </tr>)}</tbody>
    </table></div>
    {data.questions.length > 0 && <><h3>Diligence questions</h3><ul>{data.questions.map(question => <li key={question}>{question}</li>)}</ul></>}
  </section>;
}

function Comps({data, onClaim, onEvidence}: {
  data: PrecedentResponse; onClaim: (claim: WorkbenchClaim) => void; onEvidence: (companyId: string) => void;
}) {
  return <section className="wb-card">
    <header className="wb-toolbar"><h2>Ceiling, typical and floor comps</h2></header>
    {data.abstention && <p className="wb-notice">{data.abstention}</p>}
    {data.comps.length > 0 && <div className="wb-comp-grid">{roles.map(role => {
      const comp = data.comps.find(item => item.role === role);
      if (!comp) return <article key={role} className="wb-comp">
        <h3>{roleNames[role]}</h3><p>No observed floor comp is supported in the peer set.</p></article>;
      const {row, similarity, coverage, dimensions} = comp.peer;
      const matches = [...new Set(dimensions.flatMap(item => item.matched_fields))].map(fieldLabel);
      const differences = [...new Set(dimensions.flatMap(item => item.different_fields))].map(fieldLabel);
      return <article key={comp.role} className="wb-comp">
        <span className="wb-role">{roleNames[comp.role]}</span>
        <h3>{row.display_name}</h3>
        <OutcomeStatus status={row.status}/>
        <p>{row.outcome_label} · {comp.reason}</p>
        <p><strong>{similarity.toFixed(2)}</strong> similarity · {coverage.toFixed(2)} comparable coverage</p>
        <dl className="wb-dimensions">{dimensions.map(item => <div key={item.dimension}>
          <dt>{item.dimension}</dt><dd>{item.similarity?.toFixed(2) ?? "?"} · coverage {item.coverage.toFixed(2)}</dd></div>)}</dl>
        <p><strong>Matches</strong> {matches.length ? matches.join(", ") : "No shared match recorded."}</p>
        <p><strong>Differences</strong> {differences.length ? differences.join(", ") : "No supported difference in available fields."}</p>
        <h4>Same-stage snapshot</h4>
        {row.snapshot.length ? <ul>{row.snapshot.map(claim => <li key={claim.claim_id + claim.field}><button
          className="wb-text-button" onClick={() => onClaim(claim)}>{fieldLabel(claim.field)} · {claim.value}</button></li>)}</ul>
          : <p>{row.gaps.find(gap => gap.startsWith("Same-stage")) || "Same-stage evidence is withheld."}</p>}
        <button onClick={() => onEvidence(row.company_id)}>Evidence matrix</button>
      </article>;
    })}</div>}
    {data.no_verified_closure && data.peers.length >= 3 && <p>No verified closure among the closest peers.</p>}
    <details className="wb-peers">
      <summary>All {data.peers.length} similar peers</summary>
      {!data.peers.length && <p>{data.peer_count_evaluated} alignable companies reviewed for witnessed similarity.</p>}
      <ol>{data.peers.map(peer => <li key={peer.row.company_id}><strong>{peer.row.display_name}</strong>
        {" · "}{peer.similarity.toFixed(2)} similarity · {peer.coverage.toFixed(2)} coverage · <OutcomeStatus status={peer.row.status}/></li>)}</ol>
    </details>
  </section>;
}

export function Overview({data, gates, gateError, cohort, onCohort, onAnchor, onClaim, onOutlook, onEvidence}: {
  data: PrecedentResponse; gates: WorkbenchGates | null; gateError: string;
  cohort: "curated" | "similar"; onCohort: (cohort: "curated" | "similar") => void;
  onAnchor: (kind: AnchorKind) => void; onClaim: (claim: WorkbenchClaim) => void;
  onOutlook: () => void; onEvidence: (companyId: string) => void;
}) {
  const peers = cohort === "curated" ? data.curated : data.peers.map(peer => peer.row);
  const rows: WorkbenchRow[] = [data.subject, ...peers].filter(row => row.points.length > 0);
  const missing = cohort === "curated" ? data.curated.filter(row => row.not_alignable)
    .map(row => ({company_id: row.company_id, display_name: row.display_name, reason: row.not_alignable})) : data.not_alignable;

  return <>
    <section className="wb-card">
      <div className="wb-toolbar">
        <h2>Where comparable NZ ventures went</h2>
        <button type="button" disabled={!rows.length} onClick={() => downloadCsv("precedent-trajectories.csv", [
          ["company", "event", "reported_date", "precision", "lower_days", "upper_days", "source", "claim_id", "as_of"],
          ...rows.flatMap(row => row.points.map(({claim, lower_days, upper_days}) => [
            row.display_name, claim.field, claim.date_value, claim.date_precision, lower_days, upper_days,
            claim.url, claim.claim_id, data.as_of,
          ])),
        ])}>Export trajectory CSV</button>
      </div>
      <div className="wb-toolbar wb-chart-controls">
        <label>Align at <select value={data.anchor_kind} onChange={event => onAnchor(event.target.value as AnchorKind)}>
          {Object.entries(anchors).map(([value, name]) => <option value={value} key={value}>{name}</option>)}
        </select></label>
        <div className="wb-toggle" role="group" aria-label="Peer set">
          <button type="button" aria-pressed={cohort === "curated"} onClick={() => onCohort("curated")}>Curated precedents</button>
          <button type="button" aria-pressed={cohort === "similar"} onClick={() => onCohort("similar")}>Similar cohort</button>
        </div>
      </div>
      {data.subject.anchor && <p className="wb-muted">Subject anchor · {dateLabel(data.subject.anchor.claim)}</p>}
      <Trajectory rows={rows} onClaim={onClaim} title="Aligned venture trajectories"/>
      {missing.length > 0 && <details><summary>Not alignable · {missing.length}</summary>
        <ul>{missing.map(row => <li key={row.company_id}><strong>{row.display_name}</strong> · {row.reason}</li>)}</ul>
      </details>}
    </section>
    <div className="wb-overview-grid">
      <Comps data={data} onClaim={onClaim} onEvidence={onEvidence}/>
      <Checklist data={data} onClaim={onClaim}/>
    </div>
    <section className="wb-card">
      <h2>Outcome rates locked</h2>
      {gates ? <GateProgress gates={gates}/> : <p>{gateError || "Loading the cohort audit…"}</p>}
      <button onClick={onOutlook}>View Outlook</button>
    </section>
  </>;
}
