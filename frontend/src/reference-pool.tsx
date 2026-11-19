import {useState} from 'react';
import type {PoolAnalogy, PoolCounts, PoolDirectory, PoolTrajectory} from './api-schema';
import {useResource} from './hooks';
import {label} from './labels';
import {Status} from './shared';

const statusLabels: Record<string,string> = {
  reached_outcome: 'Reached Series A or later',
  closed_before_outcome: 'Verified closure first',
  acquired_or_ipo_before_outcome: 'Acquisition or IPO first',
  observed_no_outcome: 'Observed without a qualifying outcome',
  lost_to_follow_up: 'Lost to follow-up',
  unknown: 'Unknown',
};
const daysInMonth = 365.25/12;
const stages = ['pre_seed','seed','pre_series_a','series_a','series_b','series_c_plus','acquired','ipo'] as const;

function Coverage({data}: {data: PoolCounts}) {
  return <section className="pool-coverage" aria-label="Fixture coverage">
    <h3>Fixture coverage</h3>
    <p><strong>{data.companies} companies</strong> in the hand-picked fixture · Checked {data.as_of}</p>
    <dl className="pool-counts">{Object.entries(statusLabels).map(([status, name]) =>
      <div key={status}><dt>{name}</dt><dd>{data.statuses[status] ?? 0}</dd></div>)}</dl>
    <p>{data.companies_without_entry} without a supported entry · {data.companies_without_entry_snapshot} without a witnessed entry snapshot</p>
    <p>Sources · {data.sources.publisher_dated} publisher-dated · {data.sources.archived_capture} archived · {data.sources.unwitnessed} without a witness</p>
  </section>;
}

function plottedPoints(data: PoolTrajectory) {
  const stopIndex = data.points.findIndex(point => point.event.event_id === data.stop_event_id &&
    (point.event.kind.startsWith('closed_') || point.event.kind === 'acquired' || point.event.kind === 'ipo'));
  return data.points.filter((point,index) => (stopIndex < 0 || index <= stopIndex)
    && point.lower_days !== null && point.lower_days >= 0
    && (stages.some(stage => stage === point.event.kind) || point.event.kind.startsWith('closed_')));
}

function horizon(items: PoolTrajectory[]) {
  const months = Math.max(0, ...items.flatMap(item =>
    [item.censor_upper_days ?? 0, ...plottedPoints(item).map(point => point.upper_days ?? 0)]))/daysInMonth;
  return Math.max(6, Math.ceil(months/6)*6);
}

function TrajectoryStrip({data, maxMonth}: {data: PoolTrajectory, maxMonth: number}) {
  const points = plottedPoints(data);
  const rows: string[] = [...new Set(points.map(point => point.event.kind))].reverse();
  if (!rows.length) return <p>{statusLabels[data.status]}. The entry date needs more evidence before these records can be aligned.</p>;
  const position = (days: number) => `${days/daysInMonth/maxMonth*100}%`;
  const isExact = (point: typeof points[number]) => point.lower_days === point.upper_days;
  const last = points.at(-1);
  const showCensor = data.censor_lower_days != null && data.censor_lower_days >= (last?.upper_days ?? 0);
  return <figure className="pool-figure">
    <figcaption>Months since entry evidence · {statusLabels[data.status]}</figcaption>
    <div className="pool-plot" aria-hidden="true">
      {rows.map(stage => <div className="pool-plot-row" key={stage}>
        <span>{stage.startsWith('closed_') ? 'Closure' : label(stage)}</span>
        <div className="pool-plot-track">
          {points.map((point,index) => {
            if (point.event.kind !== stage) return null;
            const next = points[index+1];
            const left = point.lower_days!;
            const right = point.upper_days!;
            const end = next ? next.lower_days : showCensor ? data.censor_lower_days : null;
            const connectorRows = next ? rows.indexOf(stage)-rows.indexOf(next.event.kind) : 0;
            return <div key={point.event.event_id}>
              {isExact(point) && end != null && end >= left && <i className="pool-step" style={{left:position(left),width:position(end-left)}}/>}
              {isExact(point) && next && isExact(next) && connectorRows > 0 && <i className="pool-step-rise"
                style={{left:position(next.lower_days!),height:`${connectorRows*2.4}rem`}}/>}
              {right !== left && <i className="pool-range" style={{left:position(left),width:position(right-left)}}/>}
              <i className={'pool-mark'+(stage.startsWith('closed_')?' pool-close':'')}
                style={{left:position((left+right)/2)}}>{stage.startsWith('closed_') ? '×' : '●'}</i>
            </div>;
          })}
          {showCensor && stage === last?.event.kind &&
            <i className="pool-mark pool-censor" style={{left:position((data.censor_lower_days!+data.censor_upper_days!)/2)}}>○</i>}
        </div>
      </div>)}
      <div className="pool-plot-row pool-axis"><span/><div><span>0</span><span>{maxMonth/2}</span><span>{maxMonth} months</span></div></div>
    </div>
    <p className="muted">Bars preserve date ranges. × marks verified closure. ○ marks the last supported follow-up date.</p>
  </figure>;
}

function Trajectory({data, maxMonth = horizon([data])}: {data: PoolTrajectory, maxMonth?: number}) {
  return <section className="pool-trajectory">
    <h4>{data.company.display_name}</h4>
    <p>{data.entry_basis}</p>
    <TrajectoryStrip data={data} maxMonth={maxMonth}/>
    {data.censor_on && <p>Last verified follow-up · {data.censor_on}</p>}
    <details><summary>Inspect source evidence</summary>
      <p>Company and entry research · <a href={data.origin_source.url} target="_blank" rel="noreferrer">{data.origin_source.title}</a> · {data.origin_source.publisher} · {data.origin_passage}</p>
      <ul className="pool-evidence">{data.points.map(point => <li key={point.event.event_id}>
        <strong>{point.event.round_label ?? label(point.event.kind)}</strong>
        <p>{point.event.claim}</p>
        <p className="muted">Event date {point.event.date.value ?? 'unknown'} · {label(point.event.date.precision)} precision · {label(point.event.date_basis)} · Published {point.source.published_on ?? 'unknown'} · Retrieved {point.source.retrieved_on}</p>
        {point.event.entity_link === 'proposed' && <p className="muted">Entity link pending. This claim has no timeline position.</p>}
        <p><a href={point.source.url} target="_blank" rel="noreferrer">{point.source.title}</a> · {point.source.publisher} · {point.event.passage}</p>
        {point.witnesses.length
          ? <ul>{point.witnesses.map(w => <li key={w.witness_id}><a href={w.url} target="_blank" rel="noreferrer">{label(w.kind)}</a> · {w.available_on} · {w.locator}</li>)}</ul>
          : <p className="muted">Historical availability unverified.</p>}
      </li>)}</ul>
    </details>
    <details><summary>What was public at the time</summary>
      {data.snapshots.length === 0 && <p>No witnessed stage snapshot is available for this company.</p>}
      {data.snapshots.map(snapshot => <section key={snapshot.stage_event_id}>
        <h5>As of {snapshot.as_of}</h5>
        <ul>{snapshot.features.map(({feature,source,witness}) => <li key={feature.name}>
          <strong>{label(feature.name)}</strong> · {feature.value} · {source.publisher} · {feature.passage} · <a href={witness.url} target="_blank" rel="noreferrer">{label(witness.kind)}</a> · {witness.available_on}
        </li>)}</ul>
      </section>)}
    </details>
  </section>;
}

function Company({id}: {id: string}) {
  const [retry, setRetry] = useState(0);
  const {data, loading, error} = useResource<PoolTrajectory>('/reference-pool/companies/'+encodeURIComponent(id), retry);
  if (loading) return <Status>Loading trajectory…</Status>;
  if (error) return <Status error>{error} <button onClick={() => setRetry(n => n+1)}>Retry trajectory</button></Status>;
  return data && <Trajectory data={data}/>;
}

function FixtureDirectory() {
  const [id, setId] = useState('');
  const [retry, setRetry] = useState(0);
  const {data, loading, error} = useResource<PoolDirectory>('/reference-pool', retry);
  if (loading) return <Status>Loading reference fixture…</Status>;
  if (error) return <Status error>{error} <button onClick={() => setRetry(n => n+1)}>Retry reference fixture</button></Status>;
  if (!data?.coverage) return <p>Import the NZ reference fixture to explore its trajectories.</p>;
  return <>
    <Coverage data={data.coverage}/>
    <div className="research-toolbar"><label>Reference company <select value={id} onChange={event => setId(event.target.value)}>
      <option value="">Choose a company</option>
      {data.companies.map(company => <option key={company.company_id} value={company.company_id}>{company.display_name}</option>)}
    </select></label></div>
    {id && <Company key={id} id={id}/>}
  </>;
}

function Analogy({id}: {id: string}) {
  const [retry, setRetry] = useState(0);
  const {data, loading, error} = useResource<PoolAnalogy>('/reference-pool/analogy/'+encodeURIComponent(id), retry);
  if (loading) return <Status>Loading peer trajectories…</Status>;
  if (error) return <Status error>{error} <button onClick={() => setRetry(n => n+1)}>Retry peer trajectories</button></Status>;
  if (!data?.coverage) return <p>Import the NZ reference fixture to explore peer trajectories.</p>;
  const maxMonth = horizon(data.trajectories);
  return <>
    <p>This project is an analogy query. The timeline starts at each reference company’s own entry evidence.</p>
    {data.method === 'lexical_b0' && <p>Lexical B0 returned {data.b0_candidate_count} candidate{data.b0_candidate_count === 1 ? '' : 's'}. The fixture contains {data.trajectories.length} of them.</p>}
    {data.method === 'curated_pathway' && <p>Showing curated pathway precedents. No lexical B0 candidate has a linked fixture record.</p>}
    {data.method === 'abstain' && <p>There is insufficient comparison evidence to show a peer trajectory.</p>}
    {data.trajectories.map(item => <Trajectory key={item.company.company_id} data={item} maxMonth={maxMonth}/>)}
    <Coverage data={data.coverage}/>
  </>;
}

export function ReferencePool({subjectId}: {subjectId?: string}) {
  const [expanded, setExpanded] = useState(false);
  return <details className="pool-panel" onToggle={event => setExpanded(event.currentTarget.open)}>
    <summary>{subjectId ? 'Peer trajectories' : 'NZ reference fixture'}</summary>
    {expanded && (subjectId ? <Analogy id={subjectId}/> : <FixtureDirectory/>)}
  </details>;
}
