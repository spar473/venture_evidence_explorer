import {useState} from 'react';
import type {ComparisonEvidence, HealthtechComparison, ResearchDossier} from './api-schema';
import {useResource} from './hooks';
import {label} from './labels';
import {Status} from './shared';
import {ResearchTimeValue, ResearchRefs} from './research-shared';

function Evidence({item}: {item: ComparisonEvidence}) {
  const {observation: o, source: s} = item;
  return <article className="healthtech-evidence">
    <p>{o.paraphrase}</p>
    <p className="muted">Claim responsibility: {label(o.source_relationship)} · {label(o.assertion_nature)}<br/>
      <a href={s.url} target="_blank" rel="noreferrer">{s.title}</a> · Publisher: {s.publisher}<br/>Passage: {o.locator}</p>
    <details><summary>Dates and source record</summary>
      <dl className="research-values">
        <div><dt>Source publication</dt><dd><ResearchTimeValue time={s.published_time}/></dd></div>
        <div><dt>Retrieved</dt><dd>{s.retrieved_on}</dd></div>
        <div><dt>Document / announcement context</dt><dd><ResearchTimeValue time={o.context_time}/></dd></div>
        <div><dt>Event / occurrence</dt><dd><ResearchTimeValue time={o.effective_time}/></dd></div>
        <div><dt>Prospective target</dt><dd><ResearchTimeValue time={o.target_time}/></dd></div>
      </dl><p>Historical web availability: not verified. Checked {o.review.checked_on}; {label(o.review.state)}.</p>
      <ResearchRefs ids={[o.observation_id, s.source_id]} title="Inspect full evidence"/>
    </details>
  </article>;
}

function ComparisonResult({path}: {path: string}) {
  const [retry, setRetry] = useState(0);
  const {data, loading, error} = useResource<HealthtechComparison>(path, retry);
  if (loading) return <Status>Loading provider evaluation comparison…</Status>;
  if (error) return <Status error>{error} <button onClick={() => setRetry(n => n + 1)}>Retry comparison</button></Status>;
  if (!data) return null;
  return <div aria-live="polite">
    <p className="notice"><strong>{data.status === 'abstain' ? 'Abstaining.' : 'Pathway precedents only.'}</strong> {data.explanation}</p>
    <p className="muted">{data.view === 'historical' ? 'Historical' : 'Research'} cutoff: {data.as_of} · Same-stage comparison: abstain · {data.peers.length} of at most 3 peers</p>
    {data.gaps.length > 0 && <ul>{data.gaps.map(gap => <li key={gap}>{gap}</li>)}</ul>}
    {data.peers.map(peer => <article key={peer.subject_id} className="healthtech-peer">
      <header><span className="eyebrow">Pathway precedent</span><h4>{peer.display_name}</h4></header>
      <p>{peer.readiness.rationale}</p>
      <p>Reference document: {peer.reference_document_date}. Verified early-stage anchor: unset.</p>
      <h5>Why this comparison is useful, and where it breaks</h5>
      {peer.readiness.supported_conclusions.map(conclusion => <div key={conclusion.conclusion_id} className="healthtech-conclusion"><p>{conclusion.text}</p><ResearchRefs ids={conclusion.basis_observation_ids} title="Rationale evidence"/></div>)}
      <details><summary>Reference-document evidence · {peer.reference_evidence.length} claims</summary>
        <p className="notice">Read in current research. This document date does not establish a historical snapshot or when a provider first evaluated the product.</p>
        {peer.reference_evidence.map(item => <Evidence key={item.observation.observation_id} item={item}/>)}</details>
      <details><summary>Later reports and milestones · {peer.later_evidence.length} claims</summary>
        <p>Subsequent reports remain separate from the reference-document evidence. Later outcomes do not establish what was known earlier.</p>
        {peer.later_evidence.map(item => <Evidence key={item.observation.observation_id} item={item}/>)}</details>
      <details><summary>Unknowns and unresolved mappings</summary><ul>{peer.unknowns.map(u => <li key={u.unknown_id}>{u.explanation}</li>)}</ul>
        {peer.unresolved_cases.map(c => <p key={c.case_id}>{c.rationale}<br/><strong>To resolve:</strong> {c.required_resolution}</p>)}
        <ResearchRefs ids={peer.unresolved_cases.map(c => c.case_id)} title="Open cases"/></details>
      <h5>Conclusions withheld</h5><ul>{peer.readiness.withheld_conclusions.map(text => <li key={text}>{text}</li>)}</ul>
    </article>)}
    <details><summary>Comparison method and provenance</summary><ul>{data.limitations.map(text => <li key={text}>{text}</li>)}</ul>
      <p>Policy: <code>{data.policy_version}</code><br/>Selection SHA-256: <code>{data.selection_sha256}</code><br/>Graph SHA-256: <code>{data.graph_sha256}</code></p>
      <p><a download href={'/api' + path}>Comparison JSON ↓</a></p></details>
  </div>;
}

export function HealthtechPanel({dossier}: {dossier: ResearchDossier}) {
  const [view, setView] = useState('research');
  const [cutoff, setCutoff] = useState(dossier.packet.metadata.prepared_on);
  const params = new URLSearchParams({view, as_of: cutoff, packet_sha256: dossier.packet_digest});
  const path = '/research/subjects/' + encodeURIComponent(dossier.subject.subject_id) + '/comparisons?' + params;
  return <section className="healthtech-comparison" aria-label="Provider evaluation comparison">
    <h3>Provider evaluation comparison</h3>
    <p>What did comparable Kiwi healthtech ventures have to demonstrate before a healthcare provider would evaluate or adopt their product?</p>
    <div className="research-toolbar">
      <label>Comparison evidence view<select value={view} onChange={e => setView(e.target.value)}><option value="research">Current research · pathway precedents</option><option value="historical">Historical snapshot · requires availability proof</option></select></label>
      <label>Comparison cutoff<input type="date" value={cutoff} onChange={e => setCutoff(e.target.value)}/></label>
    </div>
    <p className="muted">The cutoff applies to this comparison. The full dossier below retains all imported evidence.</p>
    {cutoff ? <ComparisonResult key={path} path={path}/> : <Status>Choose a cutoff to inspect eligible comparison evidence.</Status>}
  </section>;
}
