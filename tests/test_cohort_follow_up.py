from copy import deepcopy

import pytest
from pydantic import ValidationError

from backend.cohort_audit import run_audit
from backend.cohort_follow_up import CoverageReview, OutcomeEvidence, assess, assess_secondary, gate, outcome_audit
from backend.reference_pool import EventDate, PoolEvent


def entry(value='2020-06-15', precision='day'):
    return dict(
        company_id='public_case',
        source_id='seed_release',
        name='Example venture',
        sector='Software',
        first_basis='explicit_first',
        date={'value': value, 'precision': precision},
        label='Seed round',
        institutional_investor='Example Fund',
        locator='Opening',
        passage='Test entry.',
    )


def event(kind, value, **fields):
    return PoolEvent(
        event_id='test_event',
        company_id='public_case',
        kind=kind,
        date={'value': value, 'precision': 'day'},
        date_basis='reported_occurrence',
        source_id='later_release',
        passage='Date and activity',
        claim='Test observation.',
        **fields,
    )


def search(day, activity='test_event'):
    return CoverageReview(
        company_id='public_case',
        reviewed_on='2026-11-20',
        searched_through=day,
        scope='Bounded synthetic coverage',
        source_ids=['later_release'],
        activity_event_id=activity,
    )


def test_later_operating_evidence_and_partial_entry_bounds():
    early = event('last_verified_activity', '2023-05-15')
    result = assess(entry(), [early], search('2023-05-15'))
    assert result['status'] == 'lost_to_follow_up'
    assert result['observed_at_36_months'] is False
    result = assess(entry('2020', 'year'), [early], search('2023-05-15'))
    assert result['observed_at_36_months'] is None
    late = event('last_verified_activity', '2024-01-01')
    result = assess(entry('2020', 'year'), [late], search('2024-01-01'))
    assert result['observed_at_36_months'] is True


def test_competing_event_requires_bounded_financing_check():
    closure = event('closed_register_removal', '2022-06-15', closure_evidence='register_removal')
    assert assess(entry(), [closure], None)['status'] == 'unknown'
    assert assess(entry(), [closure], search('2022-06-14', None))['status'] == 'unknown'
    result = assess(entry(), [closure], search('2022-06-15', None))
    assert result['status'] == 'closed_before_outcome'
    assert result['observed_at_36_months'] is False


@pytest.mark.parametrize(
    ('financing_on', 'label', 'expected'),
    [
        ('2021-04-01', None, 'unknown'),
        ('2021-04-01', 'Seed round', 'observed_no_outcome'),
        ('2023-06-16', None, 'observed_no_outcome'),
    ],
)
def test_unresolved_primary_financing_candidate_cannot_be_observed_no_outcome(financing_on, label, expected):
    activity = event('last_verified_activity', '2026-01-01')
    candidate = event('other_financing', financing_on, round_label=label).model_copy(
        update={'event_id': 'unresolved_financing'}
    )
    result = assess(entry(), [candidate, activity], search('2026-01-01'))
    assert result['status'] == expected
    if expected == 'unknown':
        assert result['censor_on'] is None
        assert result['observed_at_36_months'] is None


def test_follow_up_cannot_add_a_seed_or_use_future_activity():
    activity = event('last_verified_activity', '2024-01-01').model_dump()
    data = dict(
        format_version='nz-cohort-follow-up:1',
        as_of='2026-11-20',
        sources=[
            dict(
                source_id='later_release',
                title='Test release',
                publisher='Test',
                url='https://example.org/releases',
                kind='press_release',
                published_on='2024-01-01',
                retrieved_on='2026-11-20',
            )
        ],
        events=[activity],
        reviews=[search('2024-01-01').model_dump()],
    )
    assert OutcomeEvidence.model_validate(data).reviews[0].activity_event_id == 'test_event'
    too_early = deepcopy(data)
    too_early['reviews'][0]['searched_through'] = '2023-12-31'
    with pytest.raises(ValidationError, match='dated activity within'):
        OutcomeEvidence.model_validate(too_early)
    data['events'][0].update(kind='seed', round_label='Seed round')
    with pytest.raises(ValidationError, match='cannot alter the entry'):
        OutcomeEvidence.model_validate(data)


def test_real_audit_gate_retains_unknowns_and_reports_verified_lower_bound():
    report = run_audit()
    follow = report['follow_up']
    assert follow['decisions']['public_supie']['status'] == 'closed_before_outcome'
    assert follow['decisions']['public_partly']['status'] == 'reached_outcome'
    tiro = follow['decisions']['public_tirolifesciencesltd']
    assert tiro['status'] == 'unknown'
    assert {event['kind'] for event in tiro['events']} == {'closed_liquidation', 'closed_register_removal'}
    assert follow['decisions']['discovery_cropsy']['observed_at_36_months'] is None
    assert follow['verified_observed_at_36_months'] > 0
    assert follow['observed_at_36_months'] is None
    assert sum(follow['statuses'].values()) == report['counts']['included']
    assert not follow['gate_ready']
    assert 'fewer_than_150_eligible_companies' in follow['gate_blockers']


def test_bounded_searches_cover_original_50_with_a_public_filing_index():
    audit = run_audit()
    follow = audit['follow_up']
    searches = [item['search'] for item in follow['decisions'].values() if item['search']]
    assert follow['searched_companies'] == len(searches) == 50
    assert len({row['registry']['company_number'] for row in searches}) == 50
    assert all(
        row['registry']['filings_url'].endswith('/documents')
        and row['public_leads']
        and row['news_query']
        and row['fund_query']
        for row in searches
    )
    partly = follow['decisions']['public_partly']['secondary']
    assert partly['status'] == 'reached_outcome'
    assert partly['outcome_event_id'] == 'partly_priced_series_a'
    assert partly['event_time_basis'] == 'bounded_by_primary'
    assert partly['event_time_bounds'] == {'earliest_on': '2020-10-08', 'latest_on': '2022-12-16'}
    assert partly['observed_at_36_months'] is False
    assert follow['secondary']['statuses']['reached_outcome'] == follow['statuses']['reached_outcome'] == 2
    assert follow['decisions']['public_supie']['secondary']['status'] == 'closed_before_outcome'


def test_halter_outcomes_preserve_window_and_reported_precision():
    follow = run_audit()['follow_up']
    halter = follow['decisions']['discovery_halter']
    assert halter['status'] == 'reached_outcome'
    assert halter['latest_horizon'] == '2019-12-31'
    events = {event['event_id']: event for event in halter['events']}
    series_a = events[halter['outcome_event_id']]
    assert series_a['date'] == {'value': '2018-01', 'precision': 'month'}
    assert follow['witnesses']['witness_halter_idealog_2018']['available_on'] == '2018-06-22'
    assert events['halter_promus_seed_candidate']['instrument'] == 'unknown'
    assert halter['secondary']['status'] == 'reached_outcome'
    assert halter['secondary']['event_time_basis'] == 'bounded_by_primary'
    assert halter['secondary']['event_time_bounds'] == {'earliest_on': '2016-12-01', 'latest_on': '2018-01-31'}


def test_primary_provides_secondary_bounds_without_a_separate_proof():
    anchor = entry('2020-06', 'month')
    series_b = event('series_b', '2022-04-01', round_label='Series B', instrument='priced_equity')
    series_b = series_b.model_copy(update={'date': EventDate(value='2022-04', precision='month')})
    primary = assess(anchor, [series_b], None)
    secondary = assess_secondary(
        anchor, [series_b], None, primary, lambda candidate: 'unknown' if candidate.kind == 'series_b' else None
    )
    assert secondary['status'] == 'reached_outcome'
    assert secondary['outcome_event_id'] == 'test_event'
    assert secondary['event_time_bounds'] == {'earliest_on': '2020-06-01', 'latest_on': '2022-04-30'}
    assert secondary['censor_on'] is None
    assert secondary['observed_at_36_months'] is False


@pytest.mark.parametrize(
    ('when', 'instrument'),
    [
        ('2023-06-16', 'priced_equity'),
        ('2022-04-01', 'equity_unspecified'),
    ],
)
def test_out_of_window_or_unpriced_lettered_round_provides_no_secondary_bound(when, instrument):
    anchor = entry()
    series_a = event('series_a', when, round_label='Series A', instrument=instrument)
    primary = assess(anchor, [series_a], None)
    secondary = assess_secondary(
        anchor, [series_a], None, primary, lambda candidate: 'unknown' if candidate.kind == 'series_a' else None
    )
    assert secondary['status'] == 'unknown'
    assert secondary['outcome_event_id'] is None
    assert secondary['event_time_bounds'] is None


def test_secondary_requires_distinct_new_priced_capital_and_keeps_its_own_gate(tmp_path):
    from json import dumps

    path = tmp_path / 'follow-up.json'
    new_seed = event('other_financing', '2021-04-01', round_label='Seed', instrument='priced_equity').model_dump()
    data = dict(
        format_version='nz-cohort-follow-up:1',
        as_of='2026-11-20',
        sources=[
            dict(
                source_id='later_release',
                title='Test release',
                publisher='Test',
                url='https://example.org/releases',
                kind='press_release',
                published_on='2021-04-01',
                retrieved_on='2026-11-20',
            )
        ],
        events=[new_seed],
        reviews=[],
    )
    path.write_text(dumps(data))
    assert outcome_audit([entry()], [], path)['secondary']['statuses']['unknown'] == 1
    data['next_round_proofs'] = [
        dict(
            event_id='test_event',
            priced_at='Price per new share',
            new_company_equity='New share issue',
            distinct_from_entry='Separate closing',
        )
    ]
    path.write_text(dumps(data))
    result = outcome_audit([entry()], [], path)
    assert result['statuses']['reached_outcome'] == 0
    assert result['secondary']['statuses']['reached_outcome'] == 1
    assert result['decisions']['public_case']['secondary']['event_time_bounds'] == {
        'earliest_on': '2021-04-01',
        'latest_on': '2021-04-01',
    }
    assert 'fewer_than_30_secondary_outcomes' in result['secondary']['gate_blockers']
    assert outcome_audit([entry('2021-04-01')], [], path)['secondary']['statuses']['unknown'] == 1
    series_a = event('series_a', '2021-04-30', round_label='Series A', instrument='priced_equity').model_dump()
    series_a['event_id'] = 'series_a_event'
    data['sources'][0]['published_on'] = '2021-04-30'
    data['events'].append(series_a)
    path.write_text(dumps(data))
    direct = outcome_audit([entry()], [], path)['decisions']['public_case']['secondary']
    assert direct['outcome_event_id'] == 'test_event'
    assert direct['event_time_basis'] == 'direct'
    assert direct['event_time_bounds'] == {'earliest_on': '2021-04-01', 'latest_on': '2021-04-01'}
    new_seed.update(kind='convertible_note')
    with pytest.raises(ValidationError, match='dated, linked, priced financing'):
        OutcomeEvidence.model_validate(data)
    new_seed.update(kind='other_financing', instrument='equity_unspecified')
    with pytest.raises(ValidationError, match='dated, linked, priced financing'):
        OutcomeEvidence.model_validate(data)


def test_both_gates_require_strictly_under_a_quarter_unknown_and_lost():
    reached = {'status': 'reached_outcome', 'observed_at_36_months': False}
    observed = {'status': 'observed_no_outcome', 'observed_at_36_months': True}
    lost = {'status': 'lost_to_follow_up', 'observed_at_36_months': False}
    unknown = {'status': 'unknown', 'observed_at_36_months': None}
    rows = [reached] * 30 + [observed] * 90 + [lost] * 20 + [unknown] * 20
    assert gate(rows, 'primary')['gate_blockers'] == ['follow_up_below_required_coverage']
    rows[-1] = observed
    assert gate(rows, 'secondary')['gate_ready']
    rows[0] = observed
    assert gate(rows, 'secondary')['gate_blockers'] == ['fewer_than_30_secondary_outcomes']
