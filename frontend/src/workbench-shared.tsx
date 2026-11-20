import {useEffect, useRef, type ReactNode} from "react";
import type {PrecedentResponse, WorkbenchClaim, WorkbenchGates} from "./api-schema";
import {label} from "./labels";

export type AnchorKind = PrecedentResponse["anchor_kind"];

export const anchors: Record<AnchorKind, string> = {
  first_institutional_round: "First institutional round",
  first_provider_or_clinical_study: "First provider or clinical study",
  first_regulatory_decision: "First regulatory decision",
  first_paid_customer: "First paid customer",
};

export const statuses = {
  reached_outcome: ["Reached outcome", "reached"],
  observed_no_outcome: ["Observed without outcome", "observed"],
  closed_before_outcome: ["Verified closure first", "closed"],
  acquired_or_ipo_before_outcome: ["Acquisition or IPO first", "exit"],
  lost_to_follow_up: ["Lost to follow-up", "lost"],
  unknown: ["Unknown", "unknown"],
} as const;

export function OutcomeStatus({status}: {status: keyof typeof statuses}) {
  const [name, style] = statuses[status];
  return <span className="wb-status"><i aria-hidden="true" className={`wb-status-mark wb-${style}`}/>{name}</span>;
}

const eventLabels: Record<string, string> = {
  secondary_timing_bound: "First priced round interval",
  clinical_study: "Clinical study evidence",
  provider_deployment: "Provider deployment",
  closed_founder_announcement: "Closure announcement",
  closed_register_removal: "Register removal",
  closed_liquidation: "Liquidation",
  other_financing: "Financing disclosure",
  last_verified_activity: "Last verified activity",
  series_c_plus: "Series C or later",
};

export function fieldLabel(field: string) { return eventLabels[field] || label(field); }
export function dateLabel(claim: WorkbenchClaim) {
  return claim.date_value ? `${claim.date_value} (${claim.date_precision} precision)` : "Date unresolved";
}

export function claimLink(claim: WorkbenchClaim) {
  return <a href={claim.url} target="_blank" rel="noreferrer">Open source</a>;
}

export function ClaimDrawer({claim, onClose, children}: {
  claim: WorkbenchClaim; onClose: () => void; children?: ReactNode;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const closeButton = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    const active = document.activeElement;
    const element = dialog.current;
    element?.showModal();
    closeButton.current?.focus();
    return () => {
      element?.close();
      if (active instanceof HTMLElement || active instanceof SVGElement) active.focus();
    };
  }, []);
  return <dialog ref={dialog} className="wb-drawer" aria-label="Claim evidence" onCancel={event => {
    event.preventDefault(); onClose();
  }}>
    <header><h2>{fieldLabel(claim.field)}</h2><button ref={closeButton} onClick={onClose}>Close evidence</button></header>
    <p>{claim.value}</p>
    <dl>
      <dt>Publisher</dt><dd>{claim.publisher}</dd>
      <dt>Passage or locator</dt><dd>{claim.passage}</dd>
      <dt>Event date</dt><dd>{dateLabel(claim)}</dd>
      {claim.date_basis && <><dt>Date basis</dt><dd>{label(claim.date_basis)}</dd></>}
      <dt>Published</dt><dd>{claim.published_on || "Date unresolved"}</dd>
      <dt>Retrieved</dt><dd>{claim.retrieved_on}</dd>
      <dt>Availability witness</dt><dd>{claim.witness ?
        <a href={claim.witness.url} target="_blank" rel="noreferrer">{label(claim.witness.kind)} · {claim.witness.available_on}</a> :
        "No dated availability witness"}</dd>
      <dt>Review</dt><dd>{label(claim.review_state ?? "source_attributed")}</dd>
      <dt>Claim ID</dt><dd><code>{claim.claim_id}</code></dd>
    </dl>
    {claimLink(claim)}
    {children}
  </dialog>;
}

export function GateProgress({gates}: {gates: WorkbenchGates}) {
  return <>
    <p><strong>{gates.entries} of {gates.minimum_entries}</strong> eligible seed-entry companies</p>
    <div className="wb-table-scroll"><table className="wb-table">
      <thead><tr><th scope="col">Requirement</th><th scope="col">Series A or later</th><th scope="col">Next priced equity round</th></tr></thead>
      <tbody>
        <tr><th scope="row">Qualifying events</th><td>{gates.primary.events} of {gates.minimum_events}</td><td>{gates.secondary.events} of {gates.minimum_events}</td></tr>
        <tr><th scope="row">Unknown or lost · fewer than 1 in 4 required</th><td>{gates.primary.unknown_or_lost} of {gates.entries}</td><td>{gates.secondary.unknown_or_lost} of {gates.entries}</td></tr>
        <tr><th scope="row">Verified still observed at 36 months</th><td>{gates.primary.verified_observed_at_36_months}</td><td>{gates.secondary.verified_observed_at_36_months}</td></tr>
        <tr><th scope="row">36-month observation unresolved</th><td>{gates.primary.unresolved_at_36_months}</td><td>{gates.secondary.unresolved_at_36_months}</td></tr>
      </tbody>
    </table></div>
    <p className="wb-muted">Cohort audit as of {gates.as_of}. Held-out model validation is pending.</p>
  </>;
}

export function downloadCsv(name: string, rows: (string | number | null | undefined)[][]) {
  const csv = rows.map(row => row.map(value => {
    const cell = value == null ? "" : String(value);
    const safe = typeof value === "string" && /^[=+\-@\t\r]/.test(cell) ? "'" + cell : cell;
    return `"${safe.replaceAll('"', '""')}"`;
  }).join(",")).join("\r\n");
  const url = URL.createObjectURL(new Blob([csv], {type: "text/csv;charset=utf-8"}));
  const anchor = Object.assign(document.createElement("a"), {href: url, download: name});
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
