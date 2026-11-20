import {useEffect, useState, type FormEvent} from "react";
import type {ClaimReview, PrecedentResponse, WorkbenchClaim, WorkbenchRow} from "./api-schema";
import {api} from "./api";
import {label} from "./labels";
import {downloadCsv, fieldLabel} from "./workbench-shared";

const defaultFields = [
  {title: "Clinical evidence", match: ["clinical_evidence", "clinical_study", "prototype", "provider_study"]},
  {title: "Regulatory", match: ["regulatory", "regulatory_clearance", "regulatory_decision", "regulatory_class", "submission", "jurisdiction"]},
  {title: "Commercial use", match: ["commercial_use", "provider_deployment", "first_paid_customer", "paid_pilot", "buyer", "business_model"]},
  {title: "Funding at stage", match: ["funding", "stage", "seed", "pre_seed", "pre_series_a", "series_a",
    "series_b", "series_c_plus", "round_size_band", "lead_investor_type", "other_financing"]},
];

function WitnessBadge({claim}: {claim: WorkbenchClaim}) {
  return <small className={claim.witness ? "wb-witness" : "wb-witness wb-unwitnessed"}>{claim.witness ?
    `${label(claim.witness.kind)} · ${claim.witness.available_on}` : "No dated witness"}</small>;
}

export function EvidenceMatrix({data, focusCompany, onClaim}: {
  data: PrecedentResponse; focusCompany: string | null; onClaim: (row: WorkbenchRow, claim: WorkbenchClaim) => void;
}) {
  const [sameStage, setSameStage] = useState(false);
  const [fields, setFields] = useState<string[]>([]);
  const byId = new Map<string, WorkbenchRow>();
  for (const row of [data.subject, ...data.comps.map(item => item.peer.row), ...data.curated, ...data.peers.map(item => item.row)]) {
    if (!byId.has(row.company_id)) byId.set(row.company_id, row);
  }
  const rows = [...byId.values()];
  const dateRows = rows.map(row => ({row, claims: sameStage ? row.snapshot : row.claims}));
  const shownFields = [...defaultFields, ...fields.map(field => ({title: fieldLabel(field), match: [field]}))];
  const knownFields = new Set(shownFields.flatMap(item => item.match));
  useEffect(() => {
    if (!focusCompany) return;
    const row = document.getElementById("wb-evidence-" + focusCompany);
    row?.focus({preventScroll: true});
    row?.scrollIntoView({block: "nearest"});
  }, [focusCompany]);
  const choices = [...new Set(rows.flatMap(row => [...row.claims, ...row.snapshot].map(claim => claim.field)))]
    .filter(field => !knownFields.has(field)).sort();

  return <section className="wb-card">
    <div className="wb-toolbar"><h2>Evidence matrix</h2><button onClick={() => downloadCsv("precedent-evidence.csv", [
      ["company", "mode", "field", "claim_id", "value", "publisher", "url", "witness_date", "as_of"],
      ...dateRows.flatMap(({row, claims}) => shownFields.flatMap<(string | number | null | undefined)[]>(field => {
        const inField = claims.filter(claim => field.match.includes(claim.field));
        if (!inField.length) return [[row.display_name, sameStage ? "same_stage" : "current", field.title,
          null, null, null, null, null, data.as_of]];
        return inField.map(claim => [row.display_name, sameStage ? "same_stage" : "current", field.title,
          claim.claim_id, claim.value, claim.publisher, claim.url, claim.witness?.available_on, data.as_of]);
      })),
    ])}>Export evidence CSV</button></div>
    <div className="wb-toolbar wb-chart-controls">
      <div className="wb-toggle" role="group" aria-label="Evidence time">
        <button aria-pressed={!sameStage} onClick={() => setSameStage(false)}>Everything known today</button>
        <button aria-pressed={sameStage} onClick={() => setSameStage(true)}>What was public at the same stage</button>
      </div>
      <label>Additional field<select value="" onChange={event => {
        const field = event.target.value;
        if (field) setFields(previous => [...previous, field]);
      }}><option value="">+ Add field</option>{choices.map(field => <option key={field} value={field}>{fieldLabel(field)}</option>)}</select></label>
    </div>
    <p className="wb-muted">{sameStage ? "Each row uses its earliest possible anchor date and a dated source availability witness." :
      `Source-attributed evidence available by ${data.as_of}.`}</p>
    <div className="wb-table-scroll wb-evidence-scroll"><table className="wb-table wb-matrix" aria-label="Evidence matrix">
      <thead><tr><th scope="col">Venture</th>{shownFields.map(field => <th scope="col" key={field.title}>{field.title}</th>)}</tr></thead>
      <tbody>{dateRows.map(({row, claims}, index) => <tr key={row.company_id} id={"wb-evidence-" + row.company_id} tabIndex={-1} className={index === 0 ? "wb-pinned" : undefined}>
        <th scope="row">{row.display_name}{index === 0 && <small>Selected subject</small>}
          {sameStage && <small>{row.anchor?.claim.date_value || "Anchor unresolved"}</small>}</th>
        {shownFields.map(field => {
          const items = claims.filter(claim => field.match.includes(claim.field));
          if (!items.length) return <td key={field.title} className="wb-missing">
            {sameStage ? "Not in public record" : "Not yet extracted"}</td>;
          return <td key={field.title}>{items.map(claim => <div key={claim.claim_id + claim.field} className="wb-cell-claim">
            <button className="wb-text-button" onClick={() => onClaim(row, claim)}>{claim.value}</button>
            <small>{claim.publisher}</small><WitnessBadge claim={claim}/>
            {claim.review_state === "disputed" && <small className="wb-disputed">Disputed</small>}
          </div>)}</td>;
        })}
      </tr>)}</tbody>
    </table></div>
  </section>;
}

export function DisputeControl({subjectId, claim, onReview}: {
  subjectId: string; claim: WorkbenchClaim; onReview: (review: ClaimReview) => void;
}) {
  const [open, setOpen] = useState(false);
  const [analyst, setAnalyst] = useState("");
  const [rationale, setRationale] = useState("");
  const [requestId, setRequestId] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [recorded, setRecorded] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (busy || !analyst.trim() || !rationale.trim()) return;
    const id = requestId || crypto.randomUUID();
    setRequestId(id); setBusy(true); setError("");
    try {
      const result = await api<ClaimReview>(`/precedents/${encodeURIComponent(subjectId)}/disputes`, {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({request_id: id, claim_id: claim.claim_id, analyst, rationale}),
      });
      setRecorded(true); setOpen(false); setRequestId(""); setRationale(""); onReview(result);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Dispute could not be recorded.");
    } finally {
      setBusy(false);
    }
  }

  return <section className="wb-claim-dispute">
    {recorded && <p role="status">Dispute recorded.</p>}
    {open ? <form onSubmit={submit}>
      <label>Analyst name<input required value={analyst} maxLength={120} disabled={busy}
        onChange={event => {setAnalyst(event.target.value); setRequestId("");}}/></label>
      <label>Reason for dispute<textarea required value={rationale} maxLength={2400} disabled={busy}
        onChange={event => {setRationale(event.target.value); setRequestId("");}}/></label>
      {error && <p role="alert">{error}</p>}
      <div className="wb-toolbar"><button type="submit" disabled={busy || !analyst.trim() || !rationale.trim()}>
        {busy ? "Recording…" : "Record dispute"}</button><button type="button" disabled={busy} onClick={() => setOpen(false)}>Cancel</button></div>
    </form> : <button onClick={() => setOpen(true)}>Dispute claim</button>}
  </section>;
}
