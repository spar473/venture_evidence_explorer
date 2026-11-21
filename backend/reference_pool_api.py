"""Read-only views of sourced fixture trajectories and comparison coverage."""

from contextlib import closing
from datetime import date
from typing import Literal

from fastapi import HTTPException

from .database import connect
from .healthtech import compare_healthtech
from .ingestion import StrictModel
from .reference_pool import Feature, PoolEvent, PoolPacket, PoolSource, Status, Witness, coverage, outcome_status
from .research_repository import read_consistently
from .research_validation import decode_packet
from .retrieval import compare


class PoolCounts(StrictModel):
    kind: Literal['fixture']
    as_of: str
    companies: int
    statuses: dict[str, int]
    sources: dict[str, int]
    companies_without_entry: int
    companies_without_entry_snapshot: int


class PoolDirectoryItem(StrictModel):
    company_id: str
    display_name: str
    sector: str


class PoolDirectory(StrictModel):
    packet_sha256: str | None
    coverage: PoolCounts | None
    companies: list[PoolDirectoryItem]


class PoolPoint(StrictModel):
    event: PoolEvent
    source: PoolSource
    witnesses: list[Witness]
    lower_days: int | None
    upper_days: int | None


class WitnessedFeature(StrictModel):
    feature: Feature
    source: PoolSource
    witness: Witness


class PoolStageSnapshot(StrictModel):
    as_of: str
    stage_event_id: str
    features: list[WitnessedFeature]


class PoolTrajectory(StrictModel):
    company: PoolDirectoryItem
    status: Status
    entry_basis: str
    entry_event_id: str | None
    origin_source: PoolSource
    origin_passage: str
    censor_on: str | None
    censor_lower_days: int | None
    censor_upper_days: int | None
    stop_event_id: str | None
    points: list[PoolPoint]
    snapshots: list[PoolStageSnapshot]


class PoolAnalogy(StrictModel):
    coverage: PoolCounts | None
    trajectories: list[PoolTrajectory]
    b0_candidate_count: int
    method: Literal['lexical_b0', 'curated_pathway', 'abstain']


def latest_fixture(conn):
    if not conn.execute("SELECT 1 FROM sqlite_schema WHERE type='table' AND name='pool_imports'").fetchone():
        return None, None
    row = conn.execute('SELECT packet_sha256,raw_bytes FROM pool_imports ORDER BY rowid DESC LIMIT 1').fetchone()
    if row is None:
        return None, None
    return row['packet_sha256'], PoolPacket.model_validate(decode_packet(row['raw_bytes']))


def directory_item(company):
    return PoolDirectoryItem(company_id=company.company_id, display_name=company.display_name, sector=company.sector)


def trajectory(packet, company):
    sources = {source.source_id: source for source in packet.sources}
    witnesses = {w.witness_id: w for w in packet.witnesses}
    events = [e for e in packet.events if e.company_id == company.company_id]
    entry = next((e for e in events if e.event_id == company.entry_event_id), None)
    status, censor, stop = outcome_status(company, events)
    entry_lower, entry_upper = entry.date.bounds() if entry else (None, None)

    def offsets(lower, upper):
        if lower is None or entry_lower is None:
            return None, None
        return (
            (date.fromisoformat(lower) - date.fromisoformat(entry_upper)).days,
            (date.fromisoformat(upper) - date.fromisoformat(entry_lower)).days,
        )

    points = []
    for event in sorted(events, key=lambda e: (e.date.bounds()[0] or '9999-12-31', e.event_id)):
        lower, upper = (0, 0) if event == entry else offsets(*event.date.bounds())
        if event.entity_link == 'proposed':
            lower, upper = None, None
        points.append(
            PoolPoint(
                event=event,
                source=sources[event.source_id],
                witnesses=[w for w in packet.witnesses if w.source_id == event.source_id],
                lower_days=lower,
                upper_days=upper,
            )
        )
    censor_lower, censor_upper = offsets(censor, censor)
    snapshots = [
        PoolStageSnapshot(
            as_of=snapshot.as_of,
            stage_event_id=snapshot.stage_event_id,
            features=[
                WitnessedFeature(feature=f, source=sources[f.source_id], witness=witnesses[f.witness_id])
                for f in snapshot.features
            ],
        )
        for snapshot in sorted(packet.snapshots, key=lambda s: s.as_of)
        if snapshot.company_id == company.company_id
    ]
    return PoolTrajectory(
        company=directory_item(company),
        status=status,
        entry_basis=company.entry_basis,
        entry_event_id=company.entry_event_id,
        origin_source=sources[company.origin_source_id],
        origin_passage=company.origin_passage,
        censor_on=censor,
        censor_lower_days=censor_lower,
        censor_upper_days=censor_upper,
        stop_event_id=stop,
        points=points,
        snapshots=snapshots,
    )


@read_consistently
def analogy(conn, packet, subject_id):
    if packet is None:
        return PoolAnalogy(coverage=None, trajectories=[], b0_candidate_count=0, method='abstain')
    comparison = compare_healthtech(conn, subject_id, as_of=packet.as_of)
    query = ' '.join(
        item['observation']['paraphrase']
        for item in comparison['subject_evidence']
        if item['observation']['field'] in ('solution', 'intended_user')
    )
    result = compare(conn, query=query) if query and comparison['peers'] else {'results': []}
    by_venture = {c.venture_id: c for c in packet.companies if c.venture_id}
    companies = [
        by_venture[c['venture']['venture_id']]
        for c in result['results']
        if c['venture']['venture_id'] in by_venture
        and by_venture[c['venture']['venture_id']].research_subject_id != subject_id
    ]
    method = 'lexical_b0' if companies else 'abstain'
    if not companies:
        by_subject = {c.research_subject_id: c for c in packet.companies if c.research_subject_id}
        companies = [by_subject[p['subject_id']] for p in comparison['peers'] if p['subject_id'] in by_subject]
        if companies:
            method = 'curated_pathway'
    return PoolAnalogy(
        coverage=coverage(packet),
        b0_candidate_count=len(result['results']),
        method=method,
        trajectories=[trajectory(packet, c) for c in companies],
    )


def install(app, db):
    @app.get('/api/reference-pool', response_model=PoolDirectory)
    def reference_directory():
        with closing(connect(db)) as conn:
            digest, packet = latest_fixture(conn)
        return PoolDirectory(
            packet_sha256=digest,
            coverage=coverage(packet) if packet else None,
            companies=[directory_item(c) for c in sorted(packet.companies, key=lambda c: c.display_name.casefold())]
            if packet
            else [],
        )

    @app.get('/api/reference-pool/companies/{company_id}', response_model=PoolTrajectory)
    def reference_company(company_id: str):
        with closing(connect(db)) as conn:
            _, packet = latest_fixture(conn)
        company = next((c for c in packet.companies if c.company_id == company_id), None) if packet else None
        if company is None:
            raise HTTPException(404, 'Reference company not found')
        return trajectory(packet, company)

    @app.get('/api/reference-pool/analogy/{subject_id}', response_model=PoolAnalogy)
    def reference_analogy(subject_id: str):
        with closing(connect(db)) as conn:
            _, packet = latest_fixture(conn)
            try:
                return analogy(conn, packet, subject_id)
            except LookupError as error:
                raise HTTPException(404, 'Research subject not found') from error
