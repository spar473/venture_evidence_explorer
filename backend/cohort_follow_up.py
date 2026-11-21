"""Independent outcome coverage audit for an already selected entry cohort."""

from collections import Counter, defaultdict
import hashlib
from pathlib import Path
import re
from typing import Literal

from pydantic import Field, model_validator

from .database import ROOT
from .ingestion import StrictModel, Text, day
from .reference_pool import (
    CLOSURES,
    OUTCOMES,
    STATUSES,
    EventDate,
    FollowUp,
    Id,
    PoolCompany,
    PoolEvent,
    PoolSource,
    Witness,
    https,
    lettered_round_status,
    outcome_status,
    plus_months,
    unique_index,
    validate_event,
)
from .research_validation import decode_packet


FOLLOW_UP = ROOT / 'research/healthtech-pilot/cohort-follow-up.json'
ENTRY_ANCHOR = 'entry_anchor'
FOLLOW_ON_ROUNDS = OUTCOMES | {
    'pre_series_a',
    'seed_extension',
    'bridge',
    'other_financing',
    'series_a_equivalent',
}


class RegistrySearch(StrictModel):
    company_number: str = Field(pattern=r'^[0-9]+$')
    profile_url: Text
    filings_url: Text
    identity_and_history: Text
    status: Literal['registered', 'removed', 'liquidation']
    indexed_filings: int = Field(ge=0)
    filings_in_screened_years: int = Field(ge=0)
    first_filing_in_screen: str | None
    last_filing_in_screen: str | None
    last_annual_return: str | None


class BoundedSearch(StrictModel):
    company_id: Id
    searched_on: str
    screened_from_year: int
    screened_through_year: int
    registry: RegistrySearch
    news_query: Text
    fund_query: Text
    additional_queries: list[Text] = Field(default_factory=list)
    public_leads: list[Text]
    unresolved: Text


class NextRoundProof(StrictModel):
    event_id: Id
    priced_at: Text
    new_company_equity: Text
    distinct_from_entry: Text


class CoverageReview(StrictModel):
    company_id: Id
    reviewed_on: str
    searched_through: str
    scope: Text
    source_ids: list[Id] = Field(min_length=1)
    activity_event_id: Id | None = None


class OutcomeEvidence(StrictModel):
    format_version: Literal['nz-cohort-follow-up:1']
    as_of: str
    sources: list[PoolSource]
    events: list[PoolEvent]
    reviews: list[CoverageReview]
    searches: list[BoundedSearch] = Field(default_factory=list)
    next_round_proofs: list[NextRoundProof] = Field(default_factory=list)
    witnesses: list[Witness] = Field(default_factory=list)

    @model_validator(mode='after')
    def chronology(self):
        day(self.as_of)
        sources = unique_index(self.sources, 'source_id')
        events = unique_index(self.events, 'event_id')
        unique_index(self.reviews, 'company_id')
        unique_index(self.searches, 'company_id')
        unique_index(self.next_round_proofs, 'event_id')
        unique_index(self.witnesses, 'witness_id')
        for witness in self.witnesses:
            if witness.source_id not in sources:
                raise ValueError('Follow-up witness needs a source in the same ledger')
            witness.check_source(sources[witness.source_id])
        if any(source.retrieved_on > self.as_of for source in self.sources):
            raise ValueError('Follow-up source retrieval exceeds cutoff')
        for event in self.events:
            source = sources.get(event.source_id)
            if not source or event.event_id == ENTRY_ANCHOR:
                raise ValueError('Follow-up event needs a source and an independent event ID')
            if event.kind in ('pre_seed', 'seed'):
                raise ValueError('Follow-up evidence cannot alter the entry round')
            _, end = event.date.bounds()
            if (end is None) != (event.date_basis == 'unknown') or (
                end and end > (source.published_on or source.retrieved_on)
            ):
                raise ValueError('Follow-up event date exceeds or conflicts with its dated source')
            if event.date_basis == 'completed_at_announcement' and (not end or end != source.published_on):
                raise ValueError('Announcement timing must use the publication day')
            validate_event(event, source)
        for proof in self.next_round_proofs:
            event = events.get(proof.event_id)
            if (
                not event
                or event.kind not in FOLLOW_ON_ROUNDS
                or event.instrument != 'priced_equity'
                or event.entity_link != 'supported'
                or not event.date.bounds()[0]
            ):
                raise ValueError('Next-round proof needs a dated, linked, priced financing event')
        for search in self.searches:
            if day(search.searched_on) > self.as_of:
                raise ValueError('Bounded search exceeds audit cutoff')
            registry = search.registry
            profile = f'https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/{registry.company_number}'
            if registry.profile_url != profile or registry.filings_url != f'{profile}/documents':
                raise ValueError('Registry search requires the official profile and filing index')
            first, last = registry.first_filing_in_screen, registry.last_filing_in_screen
            starts, ends = search.screened_from_year, search.screened_through_year
            if (
                ends != starts + 3
                or registry.filings_in_screened_years > registry.indexed_filings
                or (registry.filings_in_screened_years > 0) != bool(first and last)
                or bool(first) != bool(last)
                or (first and not f'{starts}-01-01' <= day(first) <= day(last) <= f'{ends}-12-31')
                or (last and last > search.searched_on)
                or (registry.last_annual_return and day(registry.last_annual_return) > search.searched_on)
            ):
                raise ValueError('Registry filing summary exceeds its bounded search')
            for url in search.public_leads:
                https(url)
        for review in self.reviews:
            if not day(review.searched_through) <= day(review.reviewed_on) <= self.as_of:
                raise ValueError('Follow-up search window exceeds its review or audit date')
            if len(set(review.source_ids)) != len(review.source_ids) or any(
                source_id not in sources or sources[source_id].retrieved_on > review.reviewed_on
                for source_id in review.source_ids
            ):
                raise ValueError('Follow-up review needs sources retrieved by its review date')
            if review.activity_event_id:
                activity = events.get(review.activity_event_id)
                if (
                    not activity
                    or activity.company_id != review.company_id
                    or activity.kind in CLOSURES
                    or activity.entity_link != 'supported'
                    or activity.source_id not in review.source_ids
                    or activity.date.bounds()[1] is None
                    or activity.date.bounds()[1] > review.searched_through
                ):
                    raise ValueError('Follow-up needs a supported, dated activity within its own search')
        return self


def registry_events(records):
    kinds = {
        'voluntary_administration': 'voluntary_administration',
        'liquidation': 'closed_liquidation',
        'removed': 'closed_register_removal',
    }
    for record in records:
        kind = kinds[record.status]
        yield PoolEvent(
            event_id=f'register_{record.company_number}_{record.status}_{record.effective_on.replace("-", "")}',
            company_id=record.company_id,
            source_id=record.source_id,
            date_basis='reported_occurrence',
            date=EventDate(value=record.effective_on, precision='day'),
            kind=kind,
            closure_evidence={'liquidation': 'liquidation_notice', 'removed': 'register_removal'}.get(record.status),
            claim=f"Companies Register records {record.status.replace('_', ' ')}.",
            passage=record.locator,
        )


def assess(entry, events, review, *, classify_round=lettered_round_status, strictly_after_entry=False):
    company_id = entry['company_id']
    anchor = PoolEvent(
        event_id=ENTRY_ANCHOR,
        company_id=company_id,
        source_id=entry['source_id'],
        date=EventDate.model_validate(entry['date']),
        date_basis='reported_occurrence',
        kind='pre_seed' if entry['label'].lower().startswith('pre') else 'seed',
        round_label=entry['label'],
        institutional_investor=entry['institutional_investor'],
        passage=entry['locator'],
        claim=entry['passage'],
    )
    earliest_entry, latest_entry = anchor.date.bounds()
    early_horizon = plus_months(earliest_entry, 36)
    horizon = plus_months(latest_entry, 36)
    company = PoolCompany(
        company_id=company_id,
        display_name=entry['name'],
        sector=entry['sector'],
        origin_source_id=entry['source_id'],
        origin_passage=entry['locator'],
        entry_event_id=ENTRY_ANCHOR,
        entry_basis=entry['first_basis'],
    )
    by_id = {event.event_id: event for event in events}
    activity = by_id.get(review.activity_event_id) if review else None
    if activity and activity.date.bounds()[0] < latest_entry:
        raise ValueError('Later activity cannot precede or overlap uncertain entry')
    if activity:
        company.follow_up = FollowUp(
            searched_on=review.reviewed_on, scope=review.scope, activity_event_id=activity.event_id
        )
    status, censored_on, event_id = outcome_status(company, [anchor, *events], classify_round=classify_round)
    if status == 'observed_no_outcome' and any(
        unresolved_in_window(event, earliest_entry, horizon) for event in events
    ):
        status, censored_on = 'unknown', None
    if strictly_after_entry and status == 'reached_outcome' and by_id[event_id].date.bounds()[0] <= latest_entry:
        status, event_id = 'unknown', None
    if status in ('closed_before_outcome', 'acquired_or_ipo_before_outcome') and (
        not review or review.searched_through < by_id[event_id].date.bounds()[1]
    ):
        # A registry event proves closure, while the competing outcome also
        # needs a financing search covering the period up to the event.
        status, event_id = 'unknown', None
    covered_at_36_months = None
    if status in ('reached_outcome', 'closed_before_outcome', 'acquired_or_ipo_before_outcome'):
        covered_at_36_months = False
    elif status in ('observed_no_outcome', 'lost_to_follow_up'):
        if activity.date.bounds()[0] >= horizon and review.searched_through >= horizon:
            covered_at_36_months = True
        elif activity.date.bounds()[1] < early_horizon:
            covered_at_36_months = False
    return dict(
        status=status,
        censor_on=censored_on,
        outcome_event_id=event_id,
        latest_horizon=horizon,
        observed_at_36_months=covered_at_36_months,
    )


def unresolved_in_window(event, earliest_entry, latest_horizon):
    if event.kind != 'other_financing' or event.instrument not in ('unknown', 'equity_unspecified'):
        return False
    # An explicitly excluded round can still leave the secondary unresolved.
    if re.match(r'^(?:(?:pre|post)[ -])?seed\b|^pre[ -]series\b|^bridge\b', (event.round_label or '').strip(), re.I):
        return False
    start, end = event.date.bounds()
    return start is not None and start <= latest_horizon and end > earliest_entry


def assess_secondary(entry, events, review, primary, classify_round):
    result = assess(entry, events, review, classify_round=classify_round, strictly_after_entry=True)
    by_id = {event.event_id: event for event in events}
    bounds = None
    basis = None
    if result['status'] == 'reached_outcome':
        bounds = by_id[result['outcome_event_id']].date.bounds()
        basis = 'direct'
    if primary['status'] == 'reached_outcome':
        primary_id = primary['outcome_event_id']
        _, primary_end = by_id[primary_id].date.bounds()
        if bounds is None or primary_end <= bounds[1]:
            # An earlier possible priced round makes the time uncertain, but a
            # qualifying primary round proves a secondary event by that date.
            entry_start, _ = EventDate.model_validate(entry['date']).bounds()
            bounds = (entry_start, primary_end)
            basis = 'bounded_by_primary'
            result.update(
                status='reached_outcome', outcome_event_id=primary_id, censor_on=None, observed_at_36_months=False
            )
    return dict(
        result,
        event_time_basis=basis,
        event_time_bounds={'earliest_on': bounds[0], 'latest_on': bounds[1]} if bounds else None,
    )


def outcome_audit(included, registry_statuses, path=FOLLOW_UP):
    raw = Path(path).read_bytes()
    evidence = OutcomeEvidence.model_validate(decode_packet(raw))
    reviews = {review.company_id: review for review in evidence.reviews}
    searches = {search.company_id: search for search in evidence.searches}
    proofs = {proof.event_id: proof for proof in evidence.next_round_proofs}

    def next_round_status(event):
        if event.kind not in FOLLOW_ON_ROUNDS or event.instrument == 'other':
            return None
        return 'reached_outcome' if event.event_id in proofs else 'unknown'

    groups = defaultdict(list)
    for event in [*evidence.events, *registry_events(registry_statuses)]:
        groups[event.company_id].append(event)
    results = {}
    for entry in included:
        owner = entry['company_id']
        review = reviews.get(owner)
        search = searches.get(owner)
        if search and search.screened_from_year != int(entry['date']['value'][:4]):
            raise ValueError('Bounded filing search must use the included entry vintage')
        events = groups[owner]
        result = assess(entry, events, review)
        results[owner] = dict(
            result,
            secondary=assess_secondary(entry, events, review, result, next_round_status),
            review=review.model_dump() if review else None,
            search=search.model_dump() if search else None,
            next_round_proofs=[proofs[event.event_id].model_dump() for event in events if event.event_id in proofs],
            events=[event.model_dump() for event in events],
        )
    return dict(
        **gate(results.values(), 'primary'),
        secondary=gate([item['secondary'] for item in results.values()], 'secondary'),
        as_of=evidence.as_of,
        evidence_sha256=hashlib.sha256(raw).hexdigest(),
        reviewed_companies=len(results.keys() & reviews.keys()),
        searched_companies=len(results.keys() & searches.keys()),
        evidence_outside_included_companies=sorted((reviews.keys() | groups.keys() | searches.keys()) - results.keys()),
        sources={s.source_id: s.model_dump() for s in evidence.sources},
        witnesses={w.witness_id: w.model_dump() for w in evidence.witnesses},
        decisions=results,
    )


def gate(results, endpoint):
    count = Counter(item['status'] for item in results)
    observed = sum(item['observed_at_36_months'] is True for item in results)
    open_at_36 = sum(item['observed_at_36_months'] is None for item in results)
    total = len(results)
    blockers = []
    if total < 150:
        blockers.append('fewer_than_150_eligible_companies')
    if count['reached_outcome'] < 30:
        blockers.append(f'fewer_than_30_{endpoint}_outcomes')
    if not total or open_at_36 == total:
        blockers.append('no_measured_36_month_coverage')
    if not total or 4 * (count['lost_to_follow_up'] + count['unknown']) >= total:
        blockers.append('follow_up_below_required_coverage')
    return dict(
        statuses={status: count[status] for status in STATUSES},
        observed_at_36_months=None if not total or open_at_36 else observed,
        verified_observed_at_36_months=observed,
        unresolved_at_36_months=open_at_36,
        gate_ready=not blockers,
        gate_blockers=blockers,
    )
