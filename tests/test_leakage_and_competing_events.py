"""Direct tests for competing terminal events, as-of leakage guards and snapshot validator rejections."""

import json
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from backend.precedent_contracts import WorkbenchAnchor, WorkbenchClaim
from backend.precedent_evidence import pool_claim, research_claims
from backend.precedent_similarity import select_comps
from backend.precedents import PrecedentCatalog, comp_outcome
from backend.reference_pool import EventDate, PoolEvent, PoolSource, Witness
from backend.witnessed_snapshots import FEATURES, PACKET, WitnessedSnapshotPacket


def wclaim(claim_id, lower, upper=None, *, review_state='source_attributed'):
    upper = upper or lower
    return WorkbenchClaim(
        claim_id=claim_id,
        field=claim_id,
        value='Synthetic',
        passage='Synthetic test claim.',
        publisher='Example',
        url='https://example.org/',
        published_on=upper,
        retrieved_on='2026-11-21',
        date_value=lower,
        date_precision='day',
        lower_on=lower,
        upper_on=upper,
        review_state=review_state,
    )


def event(event_id, kind, value, precision='day', *, instrument='unknown'):
    return PoolEvent(
        event_id=event_id,
        company_id='example',
        source_id='publisher',
        kind=kind,
        date=EventDate(value=value, precision=precision),
        date_basis='reported_occurrence',
        claim='Dated event.',
        passage='Test.',
        instrument=instrument,
        entity_link='supported',
    )


def dated(kind, lower, upper=None):
    return event(kind, kind, lower), wclaim(kind, lower, upper)


SEED_ANCHOR = WorkbenchAnchor(kind='first_institutional_round', claim=wclaim('seed', '2019-01-01'))


# Latest-status ladder: competing terminal events (precedents.comp_outcome)


def test_closure_after_exit_takes_the_floor():
    result = comp_outcome(
        SEED_ANCHOR, [dated('acquired', '2022-01-01'), dated('closed_liquidation', '2023-06-01')], None, '2026-11-21'
    )
    assert (result.rank, result.date_value) == (0, '2023-06-01')


def test_exit_after_closure_takes_the_ceiling():
    result = comp_outcome(
        SEED_ANCHOR, [dated('closed_register_removal', '2021-03-01'), dated('ipo', '2024-02-01')], None, '2026-11-21'
    )
    assert (result.rank, result.date_value) == (5, '2024-02-01')


def test_overlapping_exit_and_closure_stay_unresolved():
    records = [dated('acquired', '2022-01-01', '2022-12-31'), dated('closed_liquidation', '2022-06-01', '2022-06-30')]
    assert comp_outcome(SEED_ANCHOR, records, None, '2026-11-21') is None


def test_terminal_events_after_the_cutoff_do_not_leak_into_the_status():
    records = [dated('acquired', '2022-01-01'), dated('closed_liquidation', '2025-06-01')]
    assert comp_outcome(SEED_ANCHOR, records, None, '2024-12-31').rank == 5


# Alternate-clock outcomes (PrecedentCatalog.comparison_outcome)


def catalog(status, outcome_event_id=None, *, follow_up_as_of='2026-11-21', as_of='2026-11-21'):
    decisions = {'example': {'status': status, 'outcome_event_id': outcome_event_id}}
    return SimpleNamespace(follow_up={'as_of': follow_up_as_of, 'decisions': decisions}, as_of=as_of)


ENTRY = {'company_id': 'example', 'date': {'value': '2018-03', 'precision': 'month'}}
STUDY = WorkbenchAnchor(kind='first_provider_or_clinical_study', claim=wclaim('study', '2019-06-01'))


def outcome(cat, events, anchor=STUDY, entry=ENTRY):
    return PrecedentCatalog.comparison_outcome(cat, entry, anchor, {e.event_id: e for e in events})


def test_alternate_clock_counts_only_priced_lettered_rounds_inside_its_window():
    priced = event('a', 'series_a', '2020-05-01', instrument='priced_equity')
    unpriced = event('b', 'series_b', '2021-05-01', instrument='equity_unspecified')
    late = event('c', 'series_c_plus', '2023-01-01', instrument='priced_equity')
    assert outcome(catalog('unknown'), [priced, unpriced, late]) == ('reached_outcome', 3)
    assert outcome(catalog('unknown'), [unpriced, late]) == ('unknown', None)


def test_alternate_clock_exit_and_closure_before_outcome():
    exit_event = event('x', 'acquired', '2020-02-01')
    assert outcome(catalog('acquired_or_ipo_before_outcome', 'x'), [exit_event]) == (
        'acquired_or_ipo_before_outcome',
        5,
    )
    closure = event('z', 'closed_liquidation', '2021-02-01')
    assert outcome(catalog('closed_before_outcome', 'z'), [closure]) == ('closed_before_outcome', 0)
    # A seed that may postdate the alternate anchor cannot establish closure before outcome on that clock.
    late_seed = {**ENTRY, 'date': {'value': '2019', 'precision': 'year'}}
    assert outcome(catalog('closed_before_outcome', 'z'), [closure], entry=late_seed) == ('unknown', None)
    # A closure on or before the anchor day is outside the alternate window.
    early = event('z', 'closed_liquidation', '2019-06-01')
    assert outcome(catalog('closed_before_outcome', 'z'), [early]) == ('unknown', None)


def test_frozen_outcomes_are_withheld_before_the_follow_up_cutoff_and_need_their_event():
    seed_anchor = WorkbenchAnchor(kind='first_institutional_round', claim=wclaim('seed', '2018-03-31'))
    assert outcome(catalog('reached_outcome', 'a', as_of='2025-01-01'), [], anchor=seed_anchor) == ('unknown', None)
    assert outcome(catalog('reached_outcome', 'a'), [], anchor=seed_anchor) == ('unknown', None)
    priced = event('a', 'series_a', '2020-05-01', instrument='priced_equity')
    assert outcome(catalog('reached_outcome', 'a'), [priced], anchor=seed_anchor) == ('reached_outcome', 3)


# As-of leakage guards (precedent_evidence)


def source(published_on='2020-01-01', retrieved_on='2026-11-21'):
    return PoolSource(
        source_id='src',
        title='Synthetic',
        publisher='Example',
        url='https://example.org/a',
        kind='news_article',
        published_on=published_on,
        retrieved_on=retrieved_on,
    )


def test_pool_claim_refuses_events_starting_after_the_cutoff():
    witness = Witness(
        witness_id='w',
        source_id='src',
        kind='publisher_dated',
        available_on='2020-01-01',
        url='https://example.org/a',
        locator='Dateline',
    )
    args = dict(claim_id='c', field='funding', value='x', passage='p', source=source(), witnesses=[witness])
    assert pool_claim(**args, when=EventDate(value='2020-03', precision='month'), as_of='2020-02-15') is None
    assert pool_claim(**args, when=EventDate(value='2020-02', precision='month'), as_of='2020-02-15')
    assert pool_claim(**args, as_of='2019-12-31') is None


def research_graph(*, retrieved_on='2020-01-01', published='2020-01-01', effective='2020-02-01', reviews=()):
    return {
        'packet': {
            'sources': [
                {
                    'source_id': 's',
                    'publisher': 'Example',
                    'url': 'https://example.org/r',
                    'published_time': {'value': published, 'precision': 'day'},
                    'retrieved_on': retrieved_on,
                }
            ],
            'review_events': list(reviews),
            'observations': [
                {
                    'observation_id': 'obs',
                    'subject_id': 'subj',
                    'field': 'solution',
                    'source_id': 's',
                    'effective_time': {'value': effective, 'precision': 'day', 'basis': 'reported'},
                    'paraphrase': 'Synthetic',
                    'locator': 'Para 1',
                    'review': {'state': 'unreviewed'},
                }
            ],
        }
    }


def test_research_claims_drop_sources_and_effective_dates_after_the_cutoff():
    assert len(research_claims(research_graph(), 'subj', '2020-03-01')) == 1
    assert research_claims(research_graph(retrieved_on='2020-04-01'), 'subj', '2020-03-01') == []
    assert research_claims(research_graph(published='2020-03-02'), 'subj', '2020-03-01') == []
    assert research_claims(research_graph(effective='2020-03-02'), 'subj', '2020-03-01') == []
    assert research_claims(None, 'subj', '2020-03-01') == []


def test_research_reviews_dispute_only_on_their_latest_day_and_not_from_the_future():
    def state(reviews, as_of='2020-06-01'):
        return research_claims(research_graph(reviews=reviews), 'subj', as_of)[0].review_state

    rejected = {'target_id': 'obs', 'reviewed_on': '2020-04-01', 'decision': 'rejected'}
    accepted = {'target_id': 'obs', 'reviewed_on': '2020-05-01', 'decision': 'accepted'}
    assert state([rejected]) == 'disputed'
    assert state([rejected, accepted]) == 'unreviewed'
    assert state([rejected], as_of='2020-03-31') == 'unreviewed'


# Comps selection when every peer's outcome is unresolved (precedent_similarity.select_comps)


def test_select_comps_abstains_when_all_qualifying_peers_are_unresolved():
    peers = [
        SimpleNamespace(similarity=0.9 - i / 10, row=SimpleNamespace(company_id=f'p{i}', comp_outcome=None))
        for i in range(3)
    ]
    comps, no_closure, reason = select_comps(peers)
    assert comps == [] and no_closure and reason == 'Outcome evidence is unresolved for all qualifying peers.'


# Witnessed snapshot validator rejections (witnessed_snapshots.WitnessedSnapshotPacket)


def packet():
    return json.loads(PACKET.read_bytes())


def profile(data, subject_id='toku', scope=None):
    return next(p for p in data['profiles'] if p['subject_id'] == subject_id and (scope is None or p['scope'] == scope))


def add_archived_source(data, *, published_on, captured):
    data['sources'].append(
        {
            'source_id': 'synthetic_late',
            'title': 'Synthetic',
            'publisher': 'Example',
            'url': 'https://example.org/late',
            'kind': 'news_article',
            'published_on': published_on,
            'retrieved_on': '2026-11-21',
        }
    )
    data['witnesses'].append(
        {
            'witness_id': 'w_synthetic_late',
            'source_id': 'synthetic_late',
            'kind': 'archived_capture',
            'available_on': captured,
            'captured_at': captured + 'T00:00:00Z',
            'url': 'https://web.archive.org/web/1/https://example.org/late',
            'locator': 'Capture',
        }
    )
    return {'source_id': 'synthetic_late', 'witness_id': 'w_synthetic_late'}


def mutate_duplicate(data):
    data['profiles'].append(json.loads(json.dumps(profile(data))))


def mutate_orphan_witness(data):
    data['witnesses'][0]['source_id'] = 'missing_source'


def mutate_future_cutoff(data):
    profile(data, 'subj_ht_mri')['cutoff'] = '2026-11-22'


def mutate_missing_anchor(data):
    profile(data)['anchor_claim_id'] = None


def mutate_anchor_on_project(data):
    profile(data, 'subj_ht_mri')['anchor_claim_id'] = 'unexpected'


def mutate_publication_after_cutoff(data):
    ids = add_archived_source(data, published_on='2021-07-10', captured='2021-06-20')
    profile(data)['features'][0].update(ids)


def mutate_round_context_field(data):
    case = profile(data, 'discovery_respiraq', 'institutional_entry_contemporaneous')
    case['features'][0]['name'] = 'prototype'
    case['features'][0]['value'] = 'yes'


def mutate_contemporaneous_not_later(data):
    case = profile(data, 'discovery_respiraq', 'institutional_entry_contemporaneous')
    ids = add_archived_source(data, published_on=None, captured=case['cutoff'])
    case['features'][0].update(ids)


def mutate_non_dimension_feature(data):
    outside = sorted({'team_size', 'founder_count', 'prior_founder_exits', 'university_origin', 'sector'} - FEATURES)[0]
    profile(data)['features'][0]['name'] = outside


def mutate_milestone_value(data):
    next(f for f in profile(data)['features'] if f['name'] == 'prototype')['value'] = 'probably'


@pytest.mark.parametrize(
    ('mutate', 'message'),
    [
        (mutate_duplicate, 'Duplicate subject and snapshot scope'),
        (mutate_orphan_witness, 'Witness requires a source retrieved by the compilation date'),
        (mutate_future_cutoff, 'Profile cutoff exceeds the compilation date'),
        (mutate_missing_anchor, 'Entry profiles require a specific existing anchor claim'),
        (mutate_anchor_on_project, 'Entry profiles require a specific existing anchor claim'),
        (mutate_publication_after_cutoff, 'Feature source publication exceeds its profile cutoff'),
        (mutate_round_context_field, 'limited to clinical workflow and buyer fields'),
        (mutate_contemporaneous_not_later, 'require a later workflow or buyer witness'),
        (mutate_non_dimension_feature, 'Feature must belong to a comparison dimension'),
        (mutate_milestone_value, 'explicit Yes or No value'),
    ],
)
def test_snapshot_validator_rejections(mutate, message):
    data = packet()
    WitnessedSnapshotPacket.model_validate(data)
    mutate(data)
    with pytest.raises(ValidationError, match=message):
        WitnessedSnapshotPacket.model_validate(data)
