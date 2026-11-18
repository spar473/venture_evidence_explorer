import { useEffect, useRef, useState } from "react";
import type { ResearchDossier, ResearchSubjectsResponse, ResearchSubjectSummary } from "./api-schema";
import { useResource } from "./hooks";
import { label } from "./labels";
import { Status } from "./shared";
import { ResearchNavigation, ResearchRaw, ResearchRefs, ResearchReviewValue, ResearchSourceCard, ResearchLimitations } from "./research-shared";
import { ResearchCaseCard, ResearchEventCard, ResearchObservationCard, ResearchReadinessCard, ResearchUnknownCard } from "./research-records";

const exportNames = ["observations", "events", "event_reports", "unknowns", "readiness", "sources", "reconciliation_cases", "access_gaps", "identity_mappings", "date_intervals", "requirements", "conclusions"];

export function ResearchWorkspace() {
  const [q, setQ] = useState("");
  const [review, setReview] = useState("");
  const [retry, setRetry] = useState(0);
  const [selected, setSelected] = useState<ResearchSubjectSummary | null>(null);
  const params = new URLSearchParams({q, review_state: review});
  const {data, error, loading} = useResource<ResearchSubjectsResponse>("/research/subjects?" + params, retry, 120);
  return <section className="research-workspace">
    <p className="notice">Research dossiers preserve source-attributed claims, explicit unknowns and unresolved identity links. Source checks are not human acceptance or independent relevance judgments. Proposed mappings do not merge evidence into the venture directory or B0 comparison.</p>
    <div className="research-toolbar">
      <label>Search research dossiers<input aria-label="Search research dossiers" value={q} onChange={e => setQ(e.target.value)} placeholder="Search dossier names" /></label>
      <label>Research review state<select aria-label="Research review state" value={review} onChange={e => setReview(e.target.value)}><option value="">All review states</option>{["extracted", "source_checked", "accepted", "disputed"].map(state => <option key={state} value={state}>{label(state)}</option>)}</select></label>
      <button type="button" onClick={() => {setQ(""); setReview("");}}>Reset research filters</button>
    </div>
    {loading ? <Status>Loading research dossiers…</Status> : error ? <Status error>{error} <button onClick={() => setRetry(n => n + 1)}>Retry research dossiers</button></Status> : !data?.items.length ? <Status>No research dossiers match these filters. Import a validated research packet into a disposable pilot database to inspect it here.</Status> : <>
      <p className="muted" aria-live="polite">{data.total} research subjects · separate from accepted venture counts</p>
      <div className="research-directory">{data.items.map(subject => <article className="research-directory-row" key={subject.subject_id}>
        <div><button className="research-open" data-subject-id={subject.subject_id} aria-haspopup="dialog" onClick={() => setSelected(subject)}>{subject.display_name}</button><p><code>{subject.subject_id}</code> · {label(subject.subject_kind)}</p><p>Identity link: {label(subject.identity_link_status)} · Review: {label(subject.review_state)}</p></div>
        <dl className="research-summary-counts"><div><dt>Atomic claims</dt><dd>{subject.observation_count}</dd></div><div><dt>Event candidates</dt><dd>{subject.event_candidate_count}</dd></div><div><dt>Explicit unknowns</dt><dd>{subject.unknown_count}</dd></div><div><dt>Open cases</dt><dd>{subject.open_case_count}</dd></div></dl>
      </article>)}</div>
    </>}
    {selected && <ResearchDrawer selected={selected} onClose={() => setSelected(null)} />}
  </section>;
}

function ResearchDrawer({selected, onClose}: {selected: ResearchSubjectSummary; onClose: () => void}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [retry, setRetry] = useState(0);
  const {data, error, loading} = useResource<ResearchDossier>("/research/subjects/" + encodeURIComponent(selected.subject_id) + "?packet_sha256=" + encodeURIComponent(selected.packet_digest), retry);
  useEffect(() => {
    const node = dialog.current;
    const opener = document.querySelector<HTMLButtonElement>(`.research-open[data-subject-id="${CSS.escape(selected.subject_id)}"]`);
    node?.showModal();
    return () => {node?.close(); opener?.focus({preventScroll: true});};
  }, [selected.subject_id]);
  return <dialog ref={dialog} className="profile-wrap research-drawer" aria-label={selected.display_name + " research dossier"} onCancel={event => {event.preventDefault(); onClose();}}>
    <div className="research-drawer-head"><div><span className="eyebrow">Research dossier · {selected.subject_id}</span><h2>{selected.display_name}</h2></div><button autoFocus type="button" onClick={onClose}>Close dossier</button></div>
    {loading ? <Status>Loading source-attributed research…</Status> : error ? <Status error>{error} <button onClick={() => setRetry(n => n + 1)}>Retry dossier</button></Status> : data && <ResearchDossierContent dossier={data} />}
  </dialog>;
}

function ResearchDossierContent({dossier}: {dossier: ResearchDossier}) {
  const {subject, packet} = dossier;
  const [field, setField] = useState("");
  const [scope, setScope] = useState("subject");
  const subjectName = (id: string) => packet.subjects.find(item => item.subject_id === id)?.display_name || id;
  const currentObservations = packet.observations.filter(item => item.subject_id === subject.subject_id);
  const observations = packet.observations.filter(item => (scope === "all" || item.subject_id === subject.subject_id) && (!field || item.field === field));
  const events = packet.events.filter(item => scope === "all" || item.subject_id === subject.subject_id);
  const unknowns = packet.unknowns.filter(item => scope === "all" || item.subject_id === subject.subject_id);
  function reveal(id: string) {
    setScope("all"); setField("");
    // Expand ancestors only after the filtered observation list has rerendered.
    requestAnimationFrame(() => requestAnimationFrame(() => {
      const node = document.getElementById("research-" + id);
      if (!node) return;
      let parent = node.parentElement;
      while (parent) {if (parent instanceof HTMLDetailsElement) parent.open = true; parent = parent.parentElement;}
      if (node instanceof HTMLDetailsElement) node.open = true;
      node.scrollIntoView({block: "start"}); node.focus({preventScroll: true});
    }));
  }
  const sections = [["claims", "Atomic claims"], ["events", "Events & targets"], ["readiness", "Question readiness"], ["unknowns", "Unknowns"], ["cases", "Open cases"], ["sources", "Sources"], ["exports", "Exports"]];
  return <ResearchNavigation.Provider value={reveal}><div className="research-dossier">
    <p className="notice">{label(subject.identity_link_status)} at brand/project level. Legal identity remains separate and unverified; a brand/project mapping decision does not establish it. Research evidence remains quarantined from accepted structured matching and B0 retrieval.</p>
    <dl className="research-values research-identity">
      {[["Legal name", subject.legal_name], ["Registration", subject.registration_id], ["Current operating status", subject.current_operating_status], ["Current funding stage", subject.current_funding_stage]].map(([title, raw]) => {
        const value = raw as typeof subject.legal_name;
        return <div key={String(title)}><dt>{String(title)}</dt><dd>{value.value || "Unknown / unverified"}<small className="research-time-basis">{label(value.reason)}</small></dd></div>;
      })}
      <div><dt>Proposed existing record</dt><dd><code>{subject.proposed_application_id || "No proposed mapping"}</code></dd></div>
      <div><dt>Accepted records in supplied packet</dt><dd>{packet.metadata.accepted_records_count}</dd></div>
    </dl>
    <p>{subject.identity_basis}</p><ResearchReviewValue review={subject.review} />
    <section className="research-mapping" aria-label="Current brand and project mapping">
      <h3>Current brand/project mapping</h3>
      <dl className="research-values">
        <div><dt>Mapping decision state</dt><dd>{dossier.identity_mapping ? label(dossier.identity_mapping.state) : "Quarantined · external record not resolved"}</dd></div>
        <div><dt>Scope</dt><dd>Brand / project only · legal identity unresolved</dd></div>
        <div><dt>Decision actor</dt><dd>{dossier.identity_mapping?.actor_id || "No human decision supplied"}</dd></div>
        <div><dt>Decision date</dt><dd>{dossier.identity_mapping?.decided_on || "Not decided"}</dd></div>
      </dl>
      <p>{dossier.identity_mapping?.rationale || subject.identity_basis}</p>
      {dossier.identity_mapping?.supersedes_mapping_id && <p className="muted">Prior mapping: <code>{dossier.identity_mapping.supersedes_mapping_id}</code></p>}
      <details><summary>Identity mapping audit</summary><ResearchRaw record={dossier.identity_mapping} /></details>
    </section>
    <nav className="research-section-nav" aria-label="Dossier sections">{sections.map(([id, text]) => <a key={id} href={"#research-section-" + id}>{text}</a>)}</nav>
    <section id="research-section-claims"><h3>Atomic source-attributed claims <span className="count">{currentObservations.length}</span></h3>
      <div className="research-toolbar"><label>Evidence field<select aria-label="Evidence field" value={field} onChange={e => setField(e.target.value)}><option value="">All evidence fields</option>{[...new Set(packet.observations.map(item => item.field))].sort().map(name => <option key={name} value={name}>{label(name)}</option>)}</select></label><label>Evidence subjects<select aria-label="Evidence subjects" value={scope} onChange={e => setScope(e.target.value)}><option value="subject">Current dossier</option><option value="all">Include linked subjects supporting shared questions</option></select></label></div>
      {!observations.length && <Status>No claims match this field and subject filter. Missing claims do not establish absence.</Status>}
      {observations.map(record => <ResearchObservationCard key={record.observation_id} record={record} subjectName={subjectName} />)}
    </section>
    <section id="research-section-events"><h3>Reported events and prospective targets</h3><p className="notice">Event identities are candidates. Possibly duplicate financing reports are never added into a monetary total or counted as established distinct rounds. Advertised interfaces do not establish completed integrations.</p>{events.map(event => <ResearchEventCard key={event.event_id} event={event} reports={packet.event_reports.filter(report => report.event_id === event.event_id)} />)}</section>
    <section id="research-section-readiness"><h3>Question-specific readiness</h3><p>These shared questions may reference both dossiers. Supported and withheld conclusions retain their subject scope, sources and review disposition.</p>{packet.readiness.filter(record => scope === "all" || record.subject_ids.includes(subject.subject_id)).map(record => <ResearchReadinessCard key={record.readiness_id} record={record} subjectName={subjectName} />)}</section>
    <section id="research-section-unknowns"><h3>Explicit unknowns and missingness</h3><p>Unknown values retain bounded reasons and inspected-source references. Named users or adopters do not establish the payer or procurement authority.</p>{unknowns.map(record => <ResearchUnknownCard key={record.unknown_id} record={record} />)}</section>
    <section id="research-section-cases"><h3>Unresolved identity and event cases</h3>{packet.reconciliation_cases.filter(record => scope === "all" || record.subject_ids.includes(subject.subject_id)).map(record => <ResearchCaseCard key={record.case_id} record={record} />)}</section>
    <section id="research-section-sources"><h3>Source versions and access limits</h3>{packet.sources.map(source => <ResearchSourceCard key={source.source_id} source={source} />)}
      <h3>Access gaps</h3>{packet.access_gaps.map(gap => <article className="research-record" key={gap.gap_id} id={`research-${gap.gap_id}`} tabIndex={-1}><h4>{label(gap.status)}</h4><p><a href={gap.url} target="_blank" rel="noreferrer">Attempted source<span className="sr-only"> (opens in a new tab)</span></a> · Retrieved {gap.retrieved_on}</p><p>{gap.description}</p><h5>Cannot establish</h5><ul>{gap.not_evidence_of.map(text => <li key={text}>{text}</li>)}</ul><ResearchRaw record={gap} /></article>)}
      <h3>Named parties</h3>{packet.parties.map(party => <article className="research-record" id={`research-${party.party_id}`} key={party.party_id} tabIndex={-1}><h4>{party.display_name}</h4><p>{label(party.party_kind)} · Legal identity: {label(party.legal_identity_status)}</p><ResearchRaw record={party} /></article>)}
    </section>
    <section><h3>Proposed analyst annotations</h3><p className="notice">Analyst interpretations and questions. Excluded from accepted facts and independent relevance judgments.</p>{packet.proposed_annotations.filter(record => record.subject_ids.includes(subject.subject_id)).map(record => <article className="research-record research-proposal" key={record.annotation_id} id={`research-${record.annotation_id}`} tabIndex={-1}><h4>{label(record.annotation_kind)} · {record.status}</h4><p>{record.text}</p><ResearchRefs ids={record.basis_observation_ids} title="Proposed interpretation basis" /><ResearchRaw record={record} /></article>)}</section>
    <section><h3>Recorded review events</h3>{!packet.review_events.length && <p>No owner or independent-reviewer decisions are recorded in this packet.</p>}{packet.review_events.map(review => <article className="research-record" key={review.review_event_id} id={`research-${review.review_event_id}`} tabIndex={-1}><h4>{label(review.decision)} · {review.reviewer_id}</h4><p>{label(review.actor_role)} · {review.reviewed_on}</p><p>{review.rationale}</p><ResearchRaw record={review} /></article>)}</section>
    <section id="research-section-exports"><h3>Export this dossier</h3><p>Database-generated CSVs retain stable IDs, raw precision, attribution, review and unknown reasons. This dossier is a subject reference view, not a standalone interchange import packet. Shared question provenance can reference the other subject. Use the original packet download to preserve its complete import bytes. No monetary totals or investment scores are generated.</p><div className="research-export-links">{exportNames.map(name => <a key={name} href={`/api/research/exports/${name}.csv?subject_id=${encodeURIComponent(subject.subject_id)}&packet_sha256=${encodeURIComponent(dossier.packet_digest)}`} download>{label(name)} CSV ↓</a>)}</div>
      <p><a href={`/api/research/packets/${dossier.packet_digest}.json`} download>Original research packet JSON ↓</a></p>
      <p className="muted">Research format {packet.metadata.format_version} · Prepared {packet.metadata.prepared_on} · Packet SHA-256 <code>{dossier.packet_digest}</code></p><ResearchLimitations items={dossier.limitations} />
      <p className="muted">Reference graph SHA-256 <code>{dossier.graph_sha256}</code></p>
      <details><summary>Dossier reference view and preserved date projections (not a standalone import packet)</summary><ResearchRaw record={dossier} /></details>
    </section>
  </div></ResearchNavigation.Provider>;
}
