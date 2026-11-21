"""Paginated status counts and sourced timelines for the frozen seed-entry cohort."""

from collections import Counter
from typing import Literal

from fastapi import Query

from .cohort_audit import run_audit
from .ingestion import StrictModel
from .precedent_contracts import WorkbenchAnchor, WorkbenchPoint
from .precedent_evidence import points_for, pool_claim
from .precedents import cohort_source, event_claim, witnesses_by_source
from .reference_pool import CLOSURES, STATUSES, EventDate, PoolEvent, PoolSource, Status, Witness, plus_months

Endpoint = Literal['primary', 'secondary']
KNOWN_OUTCOMES = {'reached_outcome', 'closed_before_outcome', 'acquired_or_ipo_before_outcome'}
HEALTHTECH_SECTORS = {'healthtech', 'healthtech software', 'wearable healthtech', 'diagnostic imaging'}
STORY_IDS = ('public_partly', 'public_supie', 'discovery_halter', 'public_tirolifesciencesltd')


class OutcomeCompany(StrictModel):
    company_id: str
    display_name: str
    sector: str


class CohortCompanies(StrictModel):
    items: list[OutcomeCompany]


class OutcomeRow(OutcomeCompany):
    vintage: int
    status: Status
    primary_status: Status
    observed_at_36_months: bool | None
    verified_closure: bool
    points: list[WorkbenchPoint]
    notes: dict[str, str]


class OutcomeCounts(StrictModel):
    label: str
    denominator: int
    statuses: dict[str, int]


class VintageCount(StrictModel):
    year: int
    entries: int


class BenchmarkDeal(StrictModel):
    year: int
    deals: int
    description: str
    url: str


class OutcomeLibrary(StrictModel):
    as_of: str
    cohort: Literal['A'] = 'A'
    endpoint: Endpoint
    candidate_records: int
    cohort_entries: int
    total: int
    limit: int
    offset: int
    sectors: list[str]
    vintages: list[int]
    counts: OutcomeCounts
    verified_closures: int
    known_at_36_months: int
    rows: list[OutcomeRow]
    stories: list[OutcomeRow]
    vintage_counts: list[VintageCount]
    benchmarks: list[BenchmarkDeal]
    sectors_comparison: list[OutcomeCounts]


def entries_in(audit):
    return [decision['entry'] for decision in audit['decisions'] if decision['status'] == 'included']


def summary(label, decisions):
    counts = Counter(decision['status'] for decision in decisions)
    return OutcomeCounts(
        label=label, denominator=len(decisions), statuses={status: counts[status] for status in STATUSES}
    )


def row_notes(points, anchor, primary_status):
    earliest_horizon = plus_months(anchor.claim.lower_on, 36)
    latest_horizon = plus_months(anchor.claim.upper_on, 36)
    notes = {}
    for point in points:
        claim = point.claim
        if claim.field in CLOSURES and claim.lower_on > latest_horizon:
            notes[claim.claim_id] = (
                'Post-window closure · Series A status unknown'
                if primary_status == 'unknown'
                else 'Post-window closure'
            )
        elif (
            not point.is_anchor
            and claim.field != 'last_verified_activity'
            and claim.lower_on <= latest_horizon
            and claim.upper_on > earliest_horizon
        ):
            notes[claim.claim_id] = 'Unresolved at the 36-month boundary'
    return notes


class OutcomeLedger:
    def __init__(self, audit):
        self.audit = audit
        self.follow = audit['follow_up']
        self.as_of = self.follow['as_of']
        self.witnesses = witnesses_by_source(Witness.model_validate(raw) for raw in self.follow['witnesses'].values())
        self.sources = {key: PoolSource.model_validate(raw) for key, raw in self.follow['sources'].items()}

    def source(self, key):
        return self.sources.get(key) or cohort_source(key, self.audit['sources'][key])

    def row(self, entry, endpoint):
        company_id = entry['company_id']
        primary = self.follow['decisions'][company_id]
        result = primary if endpoint == 'primary' else primary['secondary']
        stage = 'pre_seed' if entry['label'].lower().startswith('pre') else 'seed'
        entry_claim = pool_claim(
            'cohort_entry:' + company_id,
            stage,
            entry['passage'],
            entry['locator'],
            self.source(entry['source_id']),
            self.witnesses[entry['source_id']],
            when=EventDate.model_validate(entry['date']),
            basis=entry['date_basis'],
            as_of=self.as_of,
        )
        anchor = WorkbenchAnchor(kind='first_institutional_round', claim=entry_claim)
        events = [entry_claim]
        for raw in primary['events']:
            event = PoolEvent.model_validate(raw)
            if event.entity_link != 'supported':
                continue
            claim = event_claim(event, self.source(event.source_id), self.witnesses[event.source_id], self.as_of)
            if claim:
                events.append(claim)
        if result.get('event_time_basis') == 'bounded_by_primary':
            bounds = result['event_time_bounds']
            linked = next(claim for claim in events if claim.claim_id == result['outcome_event_id'])
            lower, upper = bounds['earliest_on'], bounds['latest_on']
            events.append(
                linked.model_copy(
                    update={
                        'claim_id': 'secondary_bound:' + company_id,
                        'field': 'secondary_timing_bound',
                        'date_value': f'{lower} to {upper}',
                        'date_precision': 'interval',
                        'lower_on': lower,
                        'upper_on': upper,
                        'date_basis': 'Bounded by the sourced entry and primary outcome',
                        'value': 'A qualifying priced round occurred by the reported Series A. The earliest priced round remains unresolved.',
                    }
                )
            )
        points = points_for(anchor, events, self.as_of)
        return OutcomeRow(
            company_id=company_id,
            display_name=entry['name'],
            sector=entry['sector'],
            vintage=int(entry['date']['value'][:4]),
            status=result['status'],
            primary_status=primary['status'],
            observed_at_36_months=result['observed_at_36_months'],
            verified_closure=any(
                event['kind'] in CLOSURES and event['entity_link'] == 'supported' for event in primary['events']
            ),
            points=points,
            notes=row_notes(points, anchor, primary['status']),
        )


def outcome_library(*, sector='', vintage=None, endpoint='primary', limit=8, offset=0):
    audit = run_audit()
    ledger = OutcomeLedger(audit)
    entries = sorted(entries_in(audit), key=lambda entry: (entry['date']['value'], entry['company_id']))
    decisions = ledger.follow['decisions']
    vintages = sorted({int(entry['date']['value'][:4]) for entry in entries})
    sectors = sorted({entry['sector'] for entry in entries})
    eligible = [
        entry
        for entry in entries
        if (not sector or entry['sector'] == sector) and (vintage is None or str(vintage) == entry['date']['value'][:4])
    ]

    def decision(entry):
        row = decisions[entry['company_id']]
        return row if endpoint == 'primary' else row['secondary']

    def is_healthtech(entry):
        return entry['sector'].casefold() in HEALTHTECH_SECTORS or 'medtech' in entry['sector'].casefold()

    selected = [decision(entry) for entry in eligible]
    known = sum(
        row['status'] in KNOWN_OUTCOMES
        or (row['status'] == 'observed_no_outcome' and row['observed_at_36_months'] is True)
        for row in selected
    )
    closed = sum(
        any(
            event['kind'] in CLOSURES and event['entity_link'] == 'supported'
            for event in decisions[entry['company_id']]['events']
        )
        for entry in eligible
    )
    per_vintage = Counter(int(entry['date']['value'][:4]) for entry in eligible)
    companies = {entry['company_id']: entry for entry in eligible}
    stories = [companies[key] for key in STORY_IDS if key in companies]
    if not stories:
        stories = [entry for entry in eligible if decision(entry)['status'] in KNOWN_OUTCOMES][:4]
    return OutcomeLibrary(
        as_of=ledger.as_of,
        endpoint=endpoint,
        candidate_records=audit['candidate_records'],
        cohort_entries=len(entries),
        total=len(eligible),
        limit=limit,
        offset=offset,
        sectors=sectors,
        vintages=vintages,
        counts=summary('Filtered entries', selected),
        verified_closures=closed,
        known_at_36_months=known,
        rows=[ledger.row(entry, endpoint) for entry in eligible[offset : offset + limit]],
        stories=[ledger.row(entry, endpoint) for entry in stories],
        vintage_counts=[VintageCount(year=year, entries=per_vintage[year]) for year in sorted(per_vintage)],
        benchmarks=[
            BenchmarkDeal(
                year=row['year'],
                deals=row['count'],
                description=row['definition'],
                url=audit['sources'][row['source_id']]['url'],
            )
            for row in audit['benchmark_deal_counts']
            if vintage is None or row['year'] == vintage
        ],
        sectors_comparison=[
            summary(
                label,
                [
                    decision(entry)
                    for entry in entries
                    if (vintage is None or str(vintage) == entry['date']['value'][:4])
                    and is_healthtech(entry) == health
                ],
            )
            for label, health in (('Healthtech and medtech', True), ('All other sectors', False))
        ],
    )


def install(app):
    @app.get('/api/workbench/outcomes', response_model=OutcomeLibrary)
    def outcomes(
        sector: str = Query('', max_length=100),
        vintage: int | None = Query(None, ge=2012, le=2022),
        endpoint: Endpoint = 'primary',
        cohort: Literal['A'] = 'A',
        limit: int = Query(8, ge=1, le=40),
        offset: int = Query(0, ge=0),
    ):
        return outcome_library(sector=sector, vintage=vintage, endpoint=endpoint, limit=limit, offset=offset)

    @app.get('/api/workbench/cohort-companies', response_model=CohortCompanies)
    def cohort_companies():
        return CohortCompanies(
            items=[
                OutcomeCompany(company_id=row['company_id'], display_name=row['name'], sector=row['sector'])
                for row in entries_in(run_audit())
            ]
        )
