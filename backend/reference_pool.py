"""Reference-pool fixture contract, validation and atomic import."""

import calendar
import hashlib
import json
import re
import sqlite3
from collections import Counter, defaultdict
from contextlib import closing
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, StrictInt, model_validator

from .database import ROOT, connect, migrate
from .ingestion import StrictModel, Text, day
from .research_validation import decode_packet

FIXTURE = ROOT / 'research/healthtech-pilot/reference-fixture.json'
ENTRY_START = '2012-01-01'
ENTRY_END = '2022-12-31'
FORMAT = 'nz-reference-pool:1'
Status = Literal[
    'reached_outcome',
    'closed_before_outcome',
    'acquired_or_ipo_before_outcome',
    'observed_no_outcome',
    'lost_to_follow_up',
    'unknown',
]
STATUSES = Status.__args__
Stage = Literal[
    'pre_seed',
    'seed',
    'series_a',
    'series_b',
    'series_c_plus',
    'series_a_equivalent',
    'pre_series_a',
    'seed_extension',
    'bridge',
    'convertible_note',
    'grant',
    'crowdfunding',
    'other_financing',
    'acquired',
    'ipo',
    'first_paid_customer',
    'provider_deployment',
    'regulatory_clearance',
    'regulatory_decision',
    'clinical_study',
    'closed_register_removal',
    'closed_liquidation',
    'closed_founder_announcement',
    'last_verified_activity',
    'voluntary_administration',
]
CLOSURES = {
    'closed_register_removal': 'registry_record',
    'closed_liquidation': 'liquidation_notice',
    'closed_founder_announcement': 'founder_announcement',
}
OUTCOMES = {'series_a', 'series_b', 'series_c_plus'}
Id = Annotated[str, Field(pattern=r'^[a-z][a-z0-9_]{0,79}$')]
FeatureName = Literal[
    'stage',
    'months_since_founding',
    'team_size',
    'founder_count',
    'prior_founder_exits',
    'university_origin',
    'sector',
    'buyer',
    'business_model',
    'regulatory_class',
    'capital_raised_to_date',
    'lead_investor_type',
    'description',
    'modality',
    'clinical_user',
    'output_type',
    'procurement_path',
    'jurisdiction',
    'regulatory_decision',
    'prototype',
    'provider_study',
    'submission',
    'paid_pilot',
    'full_time_team',
    'round_size_band',
]


def https(value):
    from urllib.parse import urlsplit

    parts = urlsplit(value)
    if parts.scheme != 'https' or not parts.hostname or parts.username or parts.password:
        raise ValueError('Evidence requires a public HTTPS URL')
    return value


class EventDate(StrictModel):
    value: str | None
    precision: Literal['day', 'month', 'quarter', 'year', 'unknown']

    @model_validator(mode='after')
    def calendar(self):
        self.bounds()
        return self

    def bounds(self):
        if self.precision == 'unknown':
            if self.value is not None:
                raise ValueError('Unknown dates must have a null value')
            return None, None
        patterns = {'day': r'\d{4}-\d{2}-\d{2}', 'month': r'\d{4}-\d{2}', 'quarter': r'\d{4}-Q[1-4]', 'year': r'\d{4}'}
        if not self.value or not re.fullmatch(patterns[self.precision], self.value):
            raise ValueError('Date does not match its precision')
        if self.precision == 'day':
            return day(self.value), self.value
        year = int(self.value[:4])
        if self.precision == 'year':
            first, last = 1, 12
        elif self.precision == 'quarter':
            first = (int(self.value[-1]) - 1) * 3 + 1
            last = first + 2
        else:
            first = last = int(self.value[-2:])
        return date(year, first, 1).isoformat(), date(year, last, calendar.monthrange(year, last)[1]).isoformat()


class PoolSource(StrictModel):
    source_id: Id
    title: Text
    publisher: Text
    url: Text
    kind: Literal[
        'press_release',
        'news_article',
        'portfolio_page',
        'company_page',
        'registry_record',
        'liquidation_notice',
        'founder_announcement',
        'dated_report',
    ]
    published_on: str | None
    retrieved_on: str
    revised_on: str | None = None

    @model_validator(mode='after')
    def chronology(self):
        https(self.url)
        day(self.retrieved_on)
        for source_date in (self.published_on, self.revised_on):
            if source_date and day(source_date) > self.retrieved_on:
                raise ValueError('Source date follows retrieval')
        if self.revised_on and self.published_on and self.revised_on < self.published_on:
            raise ValueError('Revision predates publication')
        return self


class Witness(StrictModel):
    witness_id: Id
    source_id: Id
    kind: Literal['publisher_dated', 'archived_capture']
    available_on: str
    url: Text
    locator: Text
    captured_at: str | None = None

    def check_source(self, source):
        day(self.available_on)
        https(self.url)
        if self.available_on > source.retrieved_on:
            raise ValueError('Witness day follows retrieval')
        if self.kind == 'publisher_dated':
            if (
                source.kind not in ('press_release', 'news_article')
                or self.url != source.url
                or self.available_on != (source.revised_on or source.published_on)
                or self.captured_at is not None
            ):
                raise ValueError('Publisher witness requires the dated version of a published article or release')
            return
        if not self.captured_at or not re.fullmatch(
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})', self.captured_at
        ):
            raise ValueError('Archive witness requires a timestamp with timezone')
        timestamp = datetime.fromisoformat(self.captured_at.replace('Z', '+00:00'))
        if timestamp.astimezone(timezone.utc).date().isoformat() != self.available_on or self.url == source.url:
            raise ValueError('Archive witness requires a distinct capture URL and its UTC day')
        if source.revised_on and source.revised_on > self.available_on:
            raise ValueError('A capture cannot witness a later source revision')


class PoolEvent(StrictModel):
    event_id: Id
    company_id: Id
    kind: Stage
    date: EventDate
    date_basis: Literal['reported_occurrence', 'completed_at_announcement', 'unknown']
    source_id: Id
    passage: Text
    claim: Text
    round_label: str | None = None
    institutional_investor: str | None = None
    entity_link: Literal['supported', 'proposed'] = 'supported'
    instrument: Literal['priced_equity', 'equity_unspecified', 'other', 'unknown'] = 'unknown'
    closure_evidence: Literal['register_removal', 'liquidation_notice', 'founder_announcement'] | None = None
    amount_nzd: Annotated[StrictInt, Field(gt=0)] | None = None


class FollowUp(StrictModel):
    searched_on: str
    scope: Text
    activity_event_id: Id


class PoolCompany(StrictModel):
    company_id: Id
    display_name: Text
    sector: Text
    aliases: list[Text] = Field(default_factory=list)
    venture_id: Id | None = None
    research_subject_id: Id | None = None
    origin_source_id: Id
    origin_passage: Text
    entry_event_id: Id | None = None
    entry_basis: Text
    follow_up: FollowUp | None = None


class Feature(StrictModel):
    name: FeatureName
    value: Text | StrictInt
    source_id: Id
    witness_id: Id
    passage: Text


class EntrySnapshot(StrictModel):
    snapshot_id: Id
    company_id: Id
    stage_event_id: Id
    as_of: str
    features: list[Feature] = Field(min_length=1)


def unique_index(items, key):
    index = {getattr(item, key): item for item in items}
    if len(index) != len(items):
        raise ValueError('Duplicate ' + key)
    return index


class PoolPacket(StrictModel):
    format_version: Literal['nz-reference-pool:1']
    kind: Literal['fixture']
    as_of: str
    companies: list[PoolCompany] = Field(min_length=1)
    sources: list[PoolSource] = Field(min_length=1)
    witnesses: list[Witness]
    events: list[PoolEvent]
    snapshots: list[EntrySnapshot]

    @model_validator(mode='after')
    def validate_graph(self):
        day(self.as_of)
        companies = unique_index(self.companies, 'company_id')
        sources = unique_index(self.sources, 'source_id')
        witnesses = unique_index(self.witnesses, 'witness_id')
        events = unique_index(self.events, 'event_id')
        unique_index(self.snapshots, 'snapshot_id')
        if any(s.retrieved_on > self.as_of for s in self.sources):
            raise ValueError('Source retrieved after fixture cutoff')
        for witness in self.witnesses:
            if witness.source_id not in sources:
                raise ValueError('Witness references an unknown source')
            witness.check_source(sources[witness.source_id])
        company_events = defaultdict(list)
        for event in self.events:
            source = sources.get(event.source_id)
            if event.company_id not in companies or source is None:
                raise ValueError('Event references an unknown source or company')
            if source.published_on is None:
                raise ValueError('Event needs a dated public source')
            _, upper = event.date.bounds()
            if (upper is None) != (event.date_basis == 'unknown') or (upper and upper > source.published_on):
                raise ValueError('Event timing exceeds or conflicts with the dated report')
            if event.date_basis == 'completed_at_announcement' and upper != source.published_on:
                raise ValueError('Announcement timing must use the publication day')
            validate_event(event, source)
            company_events[event.company_id].append(event)
        for company in self.companies:
            if company.origin_source_id not in sources or len(set(company.aliases)) != len(company.aliases):
                raise ValueError('Company has an unknown origin source or duplicate aliases')
            entry = events.get(company.entry_event_id)
            if company.entry_event_id and not valid_entry(entry, company, company_events[company.company_id]):
                raise ValueError(
                    'Entry must identify the earliest supported institutional pre-seed or seed in the window'
                )
            if company.follow_up:
                activity = events.get(company.follow_up.activity_event_id)
                if (
                    not entry
                    or not activity
                    or activity.company_id != company.company_id
                    or activity.entity_link != 'supported'
                    or activity.kind in CLOSURES
                    or not activity.date.bounds()[0]
                    or activity.date.bounds()[0] < entry.date.bounds()[1]
                    or not sources[activity.source_id].retrieved_on <= day(company.follow_up.searched_on) <= self.as_of
                ):
                    raise ValueError('Follow-up needs dated activity on or after entry and a bounded search')
                if any(
                    other.date.bounds()[0] and other.date.bounds()[0] > activity.date.bounds()[1]
                    for other in company_events[company.company_id]
                    if other.kind not in CLOSURES
                ):
                    raise ValueError('Follow-up omits a later supplied activity record')
        for snapshot in self.snapshots:
            validate_snapshot(snapshot, events, witnesses, sources)
        for field in ('venture_id', 'research_subject_id'):
            links = [getattr(company, field) for company in self.companies if getattr(company, field)]
            if len(set(links)) != len(links):
                raise ValueError('Ambiguous company identity link')
        return self


def validate_event(event, source):
    if event.kind in CLOSURES:
        expected = {
            'closed_register_removal': 'register_removal',
            'closed_liquidation': 'liquidation_notice',
            'closed_founder_announcement': 'founder_announcement',
        }[event.kind]
        if event.closure_evidence != expected or source.kind != CLOSURES[event.kind]:
            raise ValueError('Closure requires a positive dated registry, liquidation or founder source')
    elif event.closure_evidence is not None:
        raise ValueError('Closure proof belongs to a closure event')
    if event.kind in OUTCOMES | {'pre_seed', 'seed'} and not event.round_label:
        raise ValueError('Classified rounds need the publisher’s exact label')
    letter = {'series_a': 'a', 'series_b': 'b', 'series_c_plus': '[c-z]'}.get(event.kind)
    if letter and not re.fullmatch(
        rf'series\s+{letter}(?:-?[0-9]+)?(?:\s+(?:preferred|stock|investment|equity|financing|funding|fundraising|capital raise|round))*',
        event.round_label.strip(),
        re.I,
    ):
        raise ValueError('Series classification requires an explicit letter-stage label')
    if event.kind == 'series_a_equivalent' and (
        event.round_label is not None
        or event.instrument != 'priced_equity'
        or (event.amount_nzd or 0) < 5_000_000
        or not event.institutional_investor
    ):
        raise ValueError('Series A equivalent requires an unlabelled NZ$5M+ priced round with an institutional lead')


def valid_entry(entry, company, events):
    if (
        not entry
        or entry.company_id != company.company_id
        or entry.kind not in ('pre_seed', 'seed')
        or not entry.institutional_investor
        or entry.instrument == 'other'
        or entry.entity_link != 'supported'
    ):
        return False
    pattern = r'pre[- ]?seed' if entry.kind == 'pre_seed' else 'seed'
    if not re.fullmatch(
        pattern + r'(?:\s+(?:equity|financing|funding|round|investment|capital))*', entry.round_label.strip(), re.I
    ):
        return False
    lower, upper = entry.date.bounds()
    if not lower or not ENTRY_START <= lower <= upper <= ENTRY_END:
        return False
    return not any(
        other.event_id != entry.event_id
        and other.kind in ('pre_seed', 'seed')
        and other.institutional_investor
        and other.instrument != 'other'
        and (other.date.bounds()[0] is None or other.date.bounds()[0] <= upper)
        for other in events
    )


def validate_snapshot(snapshot, events, witnesses, sources):
    stage = events.get(snapshot.stage_event_id)
    if (
        not stage
        or stage.company_id != snapshot.company_id
        or stage.entity_link != 'supported'
        or stage.date.bounds()[1] != day(snapshot.as_of)
    ):
        raise ValueError('Snapshot needs a same-company stage anchor at the latest possible event date')
    unique_index(snapshot.features, 'name')
    for feature in snapshot.features:
        witness = witnesses.get(feature.witness_id)
        if not witness or witness.source_id != feature.source_id or witness.available_on > snapshot.as_of:
            raise ValueError('Snapshot feature needs source-version evidence on or before its cutoff')
        published = sources[feature.source_id].published_on
        if published and published > snapshot.as_of:
            raise ValueError('Snapshot feature source was published after its cutoff')
    if not any(w.source_id == stage.source_id and w.available_on <= snapshot.as_of for w in witnesses.values()):
        raise ValueError('Snapshot needs a witnessed stage source on or before its cutoff')


def plus_months(value, months):
    original = date.fromisoformat(value)
    year, offset = divmod(original.year * 12 + original.month - 1 + months, 12)
    return date(year, offset + 1, min(original.day, calendar.monthrange(year, offset + 1)[1])).isoformat()


def lettered_round_status(event):
    if event.kind in OUTCOMES and event.instrument != 'other':
        return 'reached_outcome' if event.instrument == 'priced_equity' else 'unknown'
    return None


def outcome_status(company, events, *, classify_round=lettered_round_status):
    by_id = {event.event_id: event for event in events}
    entry = by_id.get(company.entry_event_id)
    if entry is None:
        return 'unknown', None, None
    lower, upper = entry.date.bounds()
    early_horizon, late_horizon = plus_months(lower, 36), plus_months(upper, 36)
    candidates = []
    for event in events:
        status = classify_round(event)
        if event.kind in CLOSURES:
            status = 'closed_before_outcome'
        elif event.kind in ('acquired', 'ipo'):
            status = 'acquired_or_ipo_before_outcome'
        if status is None:
            continue
        first, last = event.date.bounds()
        if first and (first > late_horizon or last < lower):
            continue
        if event.entity_link == 'proposed':
            return 'unknown', None, None
        if not first or first < upper or last > early_horizon:
            return 'unknown', None, None
        candidates.append((first, last, status, event.event_id))
    candidates.sort()
    if candidates:
        _, end, status, event_id = candidates[0]
        if any(first <= end and other_status != status for first, _, other_status, _ in candidates[1:]):
            return 'unknown', None, None
        return status, None, event_id if status != 'unknown' else None
    if not company.follow_up:
        return 'unknown', None, None
    _, last = by_id[company.follow_up.activity_event_id].date.bounds()
    status = 'lost_to_follow_up' if plus_months(last, 18) <= company.follow_up.searched_on else 'observed_no_outcome'
    return status, last, None


def coverage(packet):
    events = defaultdict(list)
    for event in packet.events:
        events[event.company_id].append(event)
    statuses = Counter(outcome_status(company, events[company.company_id])[0] for company in packet.companies)
    witnessed = {w.source_id: w.kind for w in packet.witnesses if w.kind == 'publisher_dated'}
    witnessed.update({w.source_id: w.kind for w in packet.witnesses if w.kind == 'archived_capture'})
    witness_counts = Counter(witnessed.get(s.source_id, 'unwitnessed') for s in packet.sources)
    entry_ids = {company.entry_event_id for company in packet.companies if company.entry_event_id}
    snapshots = {snapshot.stage_event_id for snapshot in packet.snapshots}
    return dict(
        kind=packet.kind,
        as_of=packet.as_of,
        companies=len(packet.companies),
        statuses={status: statuses[status] for status in STATUSES},
        sources={kind: witness_counts[kind] for kind in ('publisher_dated', 'archived_capture', 'unwitnessed')},
        companies_without_entry=len(packet.companies) - len(entry_ids),
        companies_without_entry_snapshot=len(packet.companies) - len(entry_ids & snapshots),
    )


def _record_rows(conn, digest, packet):
    def insert(table, rows):
        for row in rows:
            cols = ','.join(row)
            placeholders = ','.join('?' for _ in row)
            conn.execute(
                f'INSERT INTO {table}(packet_sha256,{cols}) VALUES (?,{placeholders})', (digest, *row.values())
            )

    events = defaultdict(list)
    for event in packet.events:
        events[event.company_id].append(event)
    for company in packet.companies:
        status, censor, _ = outcome_status(company, events[company.company_id])
        insert(
            'pool_companies',
            [
                dict(
                    company_id=company.company_id,
                    display_name=company.display_name,
                    venture_id=company.venture_id,
                    research_subject_id=company.research_subject_id,
                    status=status,
                    censor_on=censor,
                )
            ],
        )
        insert('pool_aliases', [dict(company_id=company.company_id, alias=alias) for alias in company.aliases])
    insert(
        'pool_sources',
        [source.model_dump(include={'source_id', 'url', 'published_on', 'retrieved_on'}) for source in packet.sources],
    )
    insert(
        'pool_witnesses',
        [
            dict(
                witness_id=w.witness_id,
                source_id=w.source_id,
                kind=w.kind,
                available_on=w.available_on,
                captured_at=w.captured_at,
                witness_url=w.url,
                locator=w.locator,
            )
            for w in packet.witnesses
        ],
    )
    for event in packet.events:
        lower, upper = event.date.bounds()
        insert(
            'pool_events',
            [
                dict(
                    **event.model_dump(
                        include={'event_id', 'company_id', 'kind', 'source_id', 'passage', 'round_label'}
                    ),
                    date_value=event.date.value,
                    date_precision=event.date.precision,
                    date_lower=lower,
                    date_upper=upper,
                )
            ],
        )
    for snapshot in packet.snapshots:
        insert('pool_snapshots', [snapshot.model_dump(exclude={'features'})])
        insert(
            'pool_snapshot_features',
            [
                dict(
                    snapshot_id=snapshot.snapshot_id,
                    feature=f.name,
                    value_json=json.dumps(f.value),
                    source_id=f.source_id,
                    witness_id=f.witness_id,
                    passage=f.passage,
                )
                for f in snapshot.features
            ],
        )


def _check_links(conn, packet):
    ids = {r[0] for r in conn.execute('SELECT venture_id FROM ventures')}
    if any(c.venture_id is not None and c.venture_id not in ids for c in packet.companies):
        raise ValueError('Existing venture link must refer to a stored venture ID')


def import_pool(packet_path, db=None, *, apply=False):
    raw = Path(packet_path).read_bytes()
    packet = PoolPacket.model_validate(decode_packet(raw))
    digest = hashlib.sha256(raw).hexdigest()
    if db is not None and Path(db).is_file() and not apply:
        with closing(connect(db)) as conn:
            _check_links(conn, packet)
    result = dict(packet_sha256=digest, coverage=coverage(packet), status='valid_dry_run', writes=0)
    if not apply:
        return result
    if db is None or not Path(db).is_file():
        raise ValueError('Apply requires a bootstrapped database')
    with closing(sqlite3.connect(db)) as conn:
        conn.execute('PRAGMA foreign_keys=ON')
        _check_links(conn, packet)
        migrate(conn)
        conn.execute('BEGIN IMMEDIATE')
        try:
            changes = conn.total_changes
            inserted = conn.execute(
                'INSERT OR IGNORE INTO pool_imports VALUES (?,?,?,?)', (digest, packet.kind, packet.as_of, raw)
            ).rowcount
            if inserted:
                _record_rows(conn, digest, packet)
            conn.execute('COMMIT')
            return dict(
                result, status='applied' if inserted else 'already_applied', writes=conn.total_changes - changes
            )
        except BaseException:
            conn.execute('ROLLBACK')
            raise
