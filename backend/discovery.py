"""Strict lossless discovery staging. Portfolio leads are never accepted ventures."""

import hashlib
import json
import sqlite3
from pathlib import Path
from urllib.parse import urlsplit
from contextlib import closing
from typing import Literal
from pydantic import JsonValue, Field, model_validator
from jsonschema import Draft202012Validator, FormatChecker
from .database import ROOT, migrate
from .ingestion import StrictModel, Text, HistoricalDate, day
from .contracts import Contract
from .research_validation import decode_packet
from .research_adapter import research_time_interval, dry_run_research
from .retrieval import name_key

PACK = ROOT / 'research/expanded-discovery/Discovery_pack.json'
SCHEMA = json.loads((PACK.parent / 'Discovery_staging_v1.schema.json').read_text())
KEYS = {
    'organisations': 'organisation_id',
    'sources': 'source_id',
    'candidates': 'discovery_id',
    'listings': 'listing_id',
    'targeted_outcome_events': 'event_id',
    'name_links': None,
    'unresolved_cases': None,
}
REFERENCES = {'source_id', 'source_ids', 'organisation_id', 'organisation_ids', 'discovery_id', 'subjects'}


def canonical(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def record_id(collection, row):
    return (
        row[KEYS[collection]]
        if KEYS[collection]
        else collection + '_' + hashlib.sha256(canonical(row).encode()).hexdigest()[:24]
    )


def records(packet):
    return [(c, record_id(c, r), r) for c in KEYS for r in packet[c]]


def validate_packet(packet, as_of):
    Draft202012Validator(SCHEMA, format_checker=FormatChecker()).validate(packet)
    day(as_of)
    day(packet['metadata']['prepared_on'])
    if packet['metadata']['prepared_on'] > as_of:
        raise ValueError('Discovery preparation after validation date')
    indexed = {}
    all_ids = set()
    for c in KEYS:
        indexed[c] = {record_id(c, r): r for r in packet[c]}
        if any(not rid.strip() for rid in indexed[c]):
            raise ValueError('Empty discovery ID')
        if len(indexed[c]) != len(packet[c]):
            raise ValueError('Duplicate discovery record IDs in ' + c)
        if all_ids & set(indexed[c]):
            raise ValueError('Discovery IDs must be globally unique')
        all_ids.update(indexed[c])

    def refs(values, c):
        if any(v not in indexed[c] for v in values):
            raise ValueError('Unknown ' + c + ' reference')

    for s in packet['sources']:
        day(s['retrieved_on'])
        url = urlsplit(s['url'])
        if (
            url.scheme != 'https'
            or not url.hostname
            or url.username
            or any(c.isspace() for c in s['url'])
            or s['retrieved_on'] > packet['metadata']['prepared_on']
        ):
            raise ValueError('Invalid source URL/retrieval date')
        for key in ('published_at', 'updated_at'):
            if s[key] is not None:
                day(s[key])
                if s[key] > s['retrieved_on']:
                    raise ValueError('Source label after retrieval')
    for r in packet['organisations']:
        refs([r['source_id']], 'sources')
    for r in packet['candidates']:
        refs(r['source_ids'], 'sources')
        refs(r['organisation_ids'], 'organisations')
    for r in packet['listings']:
        refs([r['discovery_id']], 'candidates')
        refs([r['source_id']], 'sources')
        if r['organisation_id']:
            refs([r['organisation_id']], 'organisations')
    for r in packet['targeted_outcome_events']:
        refs([r['discovery_id']], 'candidates')
        refs([r['source_id']], 'sources')
        interval = research_time_interval(
            dict(value=r['date_value'], precision=r['date_precision'], basis=r['date_basis'], unknown_reason=None)
        )
        if interval['lower_bound'] and interval['lower_bound'] > as_of:
            raise ValueError('Future reported outcome')
    for r in packet['name_links']:
        refs([r['discovery_id']], 'candidates')
        refs([r['source_id']], 'sources')
    for r in packet['unresolved_cases']:
        refs(r.get('subjects', []), 'candidates')
        refs(r.get('source_ids', []), 'sources')
    return {c: len(packet[c]) for c in KEYS}


def _insert(c, table, row, keys):
    cols = sorted(row)
    existing = c.execute(
        'SELECT ' + ','.join(cols) + ' FROM ' + table + ' WHERE ' + ' AND '.join(k + '=?' for k in keys),
        [row[k] for k in keys],
    ).fetchone()
    values = tuple(row[k] for k in cols)
    if existing is not None:
        if tuple(existing) != values:
            raise ValueError('Conflicting immutable discovery ID in ' + table)
    else:
        c.execute(
            'INSERT INTO ' + table + ' (' + ','.join(cols) + ') VALUES (' + ','.join('?' for _ in cols) + ')', values
        )


def import_discovery(db, path=PACK, as_of='2026-11-18', failure_injector=None):
    raw = Path(path).read_bytes()
    packet = decode_packet(raw)
    counts = validate_packet(packet, as_of)
    digest = hashlib.sha256(raw).hexdigest()
    from .ingestion import load_seed

    if not Path(db).exists():
        load_seed(db)
    with closing(sqlite3.connect(db)) as c:
        c.execute('PRAGMA foreign_keys=ON')
        migrate(c)
        c.execute('BEGIN IMMEDIATE')
        try:
            old = c.execute('SELECT raw_bytes FROM discovery_imports WHERE packet_sha256=?', (digest,)).fetchone()
            if old:
                if old[0] != raw:
                    raise ValueError('Discovery digest/bytes mismatch')
                c.execute('ROLLBACK')
                return dict(status='already_staged', packet_sha256=digest, counts=counts, promoted=0)
            _insert(
                c,
                'discovery_imports',
                dict(
                    packet_sha256=digest,
                    raw_bytes=raw,
                    metadata_json=canonical(packet['metadata']),
                    validation_as_of=as_of,
                ),
                ['packet_sha256'],
            )
            rows = records(packet)
            ids = {rid for _, rid, _ in rows}
            for ordinal, (collection, rid, row) in enumerate(rows):
                _insert(
                    c,
                    'discovery_records',
                    dict(record_id=rid, collection=collection, record_json=canonical(row)),
                    ['record_id'],
                )
                _insert(
                    c,
                    'discovery_membership',
                    dict(packet_sha256=digest, record_id=rid, ordinal=ordinal),
                    ['packet_sha256', 'record_id'],
                )
                if failure_injector:
                    failure_injector(collection, c)
            for _, rid, row in rows:
                for field, value in row.items():
                    if field in REFERENCES:
                        for v in value if isinstance(value, list) else [value]:
                            if v in ids:
                                _insert(
                                    c,
                                    'discovery_links',
                                    dict(owner_id=rid, role=field, target_id=v),
                                    ['owner_id', 'role', 'target_id'],
                                )
            if c.execute('PRAGMA foreign_key_check').fetchall():
                raise ValueError('Discovery foreign-key failure')
            c.execute('COMMIT')
        except BaseException:
            if c.in_transaction:
                c.execute('ROLLBACK')
            raise
    return dict(status='staged', packet_sha256=digest, counts=counts, promoted=0)


class DiscoveryDecision(StrictModel):
    decision_id: Text
    discovery_id: Text
    kind: Literal['identity', 'nz_inclusion', 'period_scope']
    disposition: Literal['resolved', 'excluded']
    actor_role: Literal['owner', 'independent_reviewer']
    actor_id: Text
    decided_on: Text
    source_ids: list[Text] = Field(min_length=1)
    evidence_date: HistoricalDate
    rationale: Text
    target_research_subject_id: str | None = None

    @model_validator(mode='after')
    def dated(self):
        day(self.decided_on)
        if self.evidence_date.precision == 'unknown':
            raise ValueError('Review needs dated evidence, not an invented default')
        return self


class DiscoveryDecisionDocument(StrictModel):
    format_version: Literal['discovery-decisions:1']
    decisions: list[DiscoveryDecision]


def data(conn, collection):
    return [
        json.loads(r[0])
        for r in conn.execute(
            'SELECT record_json FROM discovery_records WHERE collection=? ORDER BY record_id', (collection,)
        )
    ]


def get_candidate(conn, did):
    row = conn.execute(
        "SELECT record_json FROM discovery_records WHERE record_id=? AND collection='candidates'", (did,)
    ).fetchone()
    return json.loads(row[0]) if row else None


def import_decisions(db, path, as_of='2026-11-18'):
    raw = Path(path).read_bytes()
    document = DiscoveryDecisionDocument.model_validate(decode_packet(raw))
    digest = hashlib.sha256(raw).hexdigest()
    with closing(sqlite3.connect(db)) as c:
        c.row_factory = sqlite3.Row
        c.execute('PRAGMA foreign_keys=ON')
        c.execute('BEGIN IMMEDIATE')
        try:
            _insert(c, 'discovery_decision_documents', dict(document_sha256=digest, raw_bytes=raw), ['document_sha256'])
            for d in document.decisions:
                candidate = get_candidate(c, d.discovery_id)
                if not candidate or not set(d.source_ids) <= set(candidate['source_ids']):
                    raise ValueError('Decision references outside discovery subject')
                if d.decided_on > as_of or d.evidence_date.lower_bound > d.decided_on:
                    raise ValueError('Future discovery decision/evidence')
                for source in data(c, 'sources'):
                    if source['source_id'] in d.source_ids and source['retrieved_on'] > d.decided_on:
                        raise ValueError('Decision predates source inspection')
                _insert(
                    c,
                    'discovery_reviews',
                    dict(
                        decision_id=d.decision_id,
                        discovery_id=d.discovery_id,
                        kind=d.kind,
                        document_sha256=digest,
                        decision_json=canonical(d.model_dump()),
                    ),
                    ['decision_id'],
                )
            c.execute('COMMIT')
        except BaseException:
            if c.in_transaction:
                c.execute('ROLLBACK')
            raise
    return {'status': 'decisions_recorded', 'count': len(document.decisions), 'writes_to_accepted_corpus': 0}


def reviews(conn, did):
    return [
        json.loads(r[0])
        for r in conn.execute('SELECT decision_json FROM discovery_reviews WHERE discovery_id=? ORDER BY rowid', (did,))
    ]


def gaps(candidate, outcomes):
    result = ['identity', 'nz_inclusion', 'source_observations', 'source_capture']
    if not outcomes:
        result.append('dated_activity')
    return result


def preview(conn, did):
    candidate = get_candidate(conn, did)
    if candidate is None:
        return None
    cases = [
        r
        for r in data(conn, 'unresolved_cases')
        if did in r.get('subjects', []) or set(candidate['source_ids']) & set(r.get('source_ids', []))
    ]
    aliases = [r for r in data(conn, 'name_links') if r['discovery_id'] == did]
    names = {name_key(candidate['display_name']), *(name_key(r['other_name']) for r in aliases)}
    duplicates = [
        {'kind': 'discovery', 'id': r['discovery_id'], 'name': r['display_name'], 'basis': 'Name/alias candidate only'}
        for r in data(conn, 'candidates')
        if r['discovery_id'] != did and name_key(r['display_name']) in names
    ]
    duplicates += [
        {'kind': 'application', 'id': r['venture_id'], 'name': r['display_name'], 'basis': 'Name/alias candidate only'}
        for r in conn.execute('SELECT venture_id,display_name FROM ventures')
        if name_key(r['display_name']) in names
    ]
    for case in cases:
        for other in case.get('subjects', []):
            if other != did and not any(d['id'] == other for d in duplicates):
                duplicates.append({'kind': 'unresolved_case', 'id': other, 'name': other, 'basis': case['action']})
    source_map = {r['source_id']: r for r in data(conn, 'sources')}
    orgs = {r['organisation_id']: r for r in data(conn, 'organisations')}
    outcomes = [r for r in data(conn, 'targeted_outcome_events') if r['discovery_id'] == did]
    decisions = reviews(conn, did)
    latest = {d['kind']: d for d in decisions}
    missing = [
        g
        for g in gaps(candidate, outcomes)
        if not (
            g == 'identity'
            and latest.get('identity', {}).get('disposition') == 'resolved'
            or g == 'nz_inclusion'
            and latest.get('nz_inclusion', {}).get('disposition') == 'resolved'
        )
    ]
    return dict(
        candidate=candidate,
        sources=[source_map[s] for s in candidate['source_ids']],
        organisations=[orgs[s] for s in candidate['organisation_ids']],
        listings=[r for r in data(conn, 'listings') if r['discovery_id'] == did],
        outcomes=outcomes,
        name_links=aliases,
        unresolved_cases=cases,
        duplicate_candidates=duplicates,
        review_decisions=decisions,
        evidence_gaps=missing,
        nz_inclusion_evidence=latest.get('nz_inclusion')
        if latest.get('nz_inclusion', {}).get('disposition') == 'resolved'
        else None,
        accepted=False,
    )


def promotion_preview(conn, did, research_packet=None, as_of="2026-11-18"):
    view = preview(conn, did)
    if view is None:
        raise LookupError('Discovery candidate not found')
    latest = {r['kind']: r for r in view['review_decisions']}
    missing = [
        kind
        for kind in ('identity', 'nz_inclusion', 'period_scope')
        if latest.get(kind, {}).get('disposition') != 'resolved'
    ]
    blockers = ['Genuine resolved ' + kind + ' decision and dated evidence required' for kind in missing]
    adapter = None
    if research_packet:
        # This is deliberately a dry run only: no implicit invention of 0.2.1 claims.
        database = conn.execute('PRAGMA database_list').fetchone()[2]
        adapter = dry_run_research(research_packet, db_path=database, as_of=as_of)
        if adapter['status'] != 'valid_dry_run':
            blockers.append('Research adapter rejected supplied packet')
        p = decode_packet(Path(research_packet).read_bytes())
        target = latest.get('identity', {}).get('target_research_subject_id')
        subject = next((s for s in p.get('subjects', []) if s['subject_id'] == target), None)
        if not subject or subject['review']['state'] != 'accepted':
            blockers.append('Matching research subject needs actual typed acceptance provenance')
    else:
        blockers.append(
            'No reviewed research 0.2.1 packet supplied; portfolio listing cannot be fabricated into source observations'
        )
    return dict(
        discovery_id=did,
        ready_for_research_import=not blockers,
        blockers=blockers,
        adapter_report=adapter,
        writes=0,
        scope='Staging only; no promotion/app import endpoint is enabled',
    )


class DiscoveryItem(Contract):
    discovery_id: str
    display_name: str
    source_families: list[str]
    status: str
    research_depth: str
    reported_outcome_years: list[int]
    evidence_gaps: list[str]


class DiscoveryPage(Contract):
    items: list[DiscoveryItem]
    total: int
    staged_total: int
    source_families_total: int
    promoted_total: Literal[0] = 0
    accepted_nz_population: None = None
    limit: int
    offset: int


class DiscoveryDetail(Contract):
    candidate: dict[str, JsonValue]
    sources: list[dict[str, JsonValue]]
    organisations: list[dict[str, JsonValue]]
    listings: list[dict[str, JsonValue]]
    outcomes: list[dict[str, JsonValue]]
    name_links: list[dict[str, JsonValue]]
    unresolved_cases: list[dict[str, JsonValue]]
    duplicate_candidates: list[dict[str, str]]
    review_decisions: list[dict[str, JsonValue]]
    evidence_gaps: list[str]
    nz_inclusion_evidence: dict[str, JsonValue] | None
    accepted: Literal[False] = False


class PromotionPreview(Contract):
    discovery_id: str
    ready_for_research_import: bool
    blockers: list[str]
    adapter_report: dict[str, JsonValue] | None
    writes: Literal[0] = 0
    scope: str


def queue(conn, q='', family='', status='', year=None, gap='', unknown_period=False, limit=25, offset=0):
    candidates = data(conn, 'candidates')
    orgs = {r['organisation_id']: r['name'] for r in data(conn, 'organisations')}
    outcomes = data(conn, 'targeted_outcome_events')
    items = []
    all_reviews = {}
    for row in conn.execute('SELECT discovery_id,decision_json FROM discovery_reviews ORDER BY rowid'):
        all_reviews.setdefault(row[0], []).append(json.loads(row[1]))
    for c in candidates:
        events = [o for o in outcomes if o['discovery_id'] == c['discovery_id']]
        years = sorted({int(o['date_value'][:4]) for o in events if o['date_value']})
        decisions = all_reviews.get(c['discovery_id'], [])
        latest = {d['kind']: d for d in decisions}
        state = (
            'excluded_by_review'
            if any(d['disposition'] == 'excluded' for d in latest.values())
            else 'reviewed_staging'
            if len(latest) == 3
            else 'pending_review'
        )
        missing = [
            g
            for g in gaps(c, events)
            if not (
                g == 'identity'
                and latest.get('identity', {}).get('disposition') == 'resolved'
                or g == 'nz_inclusion'
                and latest.get('nz_inclusion', {}).get('disposition') == 'resolved'
            )
        ]
        if (
            q.casefold() not in c['display_name'].casefold()
            or family
            and family not in c['organisation_ids']
            or status
            and status != state
            or year
            and year not in years
            or gap
            and gap not in missing
            or unknown_period
            and years
        ):
            continue
        items.append(
            dict(
                discovery_id=c['discovery_id'],
                display_name=c['display_name'],
                source_families=[orgs[o] for o in c['organisation_ids']],
                status=state,
                research_depth=c['research_depth'],
                reported_outcome_years=years,
                evidence_gaps=missing,
            )
        )
    items.sort(key=lambda x: (x['display_name'].casefold(), x['discovery_id']))
    return dict(
        items=items[offset : offset + limit],
        total=len(items),
        staged_total=len(candidates),
        source_families_total=len(orgs),
        promoted_total=0,
        accepted_nz_population=None,
        limit=limit,
        offset=offset,
    )


class SourceFamily(Contract):
    organisation_id: str
    name: str
    coverage_status: str


class DiscoveryFacets(Contract):
    families: list[SourceFamily]
    outcome_years: list[int]
