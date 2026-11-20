from copy import deepcopy

import pytest
from pydantic import ValidationError

from backend.cohort_audit import run_audit
from backend.cohort_follow_up import CoverageReview, OutcomeEvidence, assess, gate, outcome_audit
from backend.reference_pool import PoolEvent


def entry(value='2020-06-15', precision='day'):
    return dict(company_id='public_case', source_id='seed_release', name='Example venture', sector='Software',
                first_basis='explicit_first', date={'value':value,'precision':precision},
                label='Seed round', institutional_investor='Example Fund',
                locator='Opening', passage='Test entry.')


def event(kind, value, **fields):
    return PoolEvent(event_id='test_event', company_id='public_case', kind=kind,
                     date={'value':value,'precision':'day'}, date_basis='reported_occurrence',
                     source_id='later_release', passage='Date and activity', claim='Test observation.', **fields)


def search(day, activity='test_event'):
    return CoverageReview(company_id='public_case', reviewed_on='2026-11-20', searched_through=day,
                          scope='Bounded synthetic coverage', source_ids=['later_release'], activity_event_id=activity)


def test_later_operating_evidence_and_partial_entry_bounds():
    early = event('last_verified_activity','2023-05-15')
    result = assess(entry(), [early], search('2023-05-15'))
    assert result['status'] == 'lost_to_follow_up'
    assert result['observed_at_36_months'] is False
    result = assess(entry('2020','year'), [early], search('2023-05-15'))
    assert result['observed_at_36_months'] is None
    late = event('last_verified_activity','2024-01-01')
    result = assess(entry('2020','year'), [late], search('2024-01-01'))
    assert result['observed_at_36_months'] is True


def test_competing_event_requires_bounded_financing_check():
    closure = event('closed_register_removal','2022-06-15',closure_evidence='register_removal')
    assert assess(entry(), [closure], None)['status'] == 'unknown'
    assert assess(entry(), [closure], search('2022-06-14',None))['status'] == 'unknown'
    result = assess(entry(), [closure], search('2022-06-15',None))
    assert result['status'] == 'closed_before_outcome'
    assert result['observed_at_36_months'] is False


def test_follow_up_cannot_add_a_seed_or_use_future_activity():
    activity = event('last_verified_activity','2024-01-01').model_dump()
    data = dict(format_version='nz-cohort-follow-up:1',as_of='2026-11-20',
                sources=[dict(source_id='later_release', title='Test release', publisher='Test',
                              url='https://example.org/releases', kind='press_release',
                              published_on='2024-01-01', retrieved_on='2026-11-20')],
                events=[activity], reviews=[search('2024-01-01').model_dump()])
    assert OutcomeEvidence.model_validate(data).reviews[0].activity_event_id == 'test_event'
    too_early = deepcopy(data)
    too_early['reviews'][0]['searched_through'] = '2023-12-31'
    with pytest.raises(ValidationError,match='dated activity within'):
        OutcomeEvidence.model_validate(too_early)
    data['events'][0].update(kind='seed',round_label='Seed round')
    with pytest.raises(ValidationError,match='cannot alter the entry'):
        OutcomeEvidence.model_validate(data)


def test_real_audit_gate_retains_unknowns_and_reports_verified_lower_bound():
    report = run_audit()
    follow = report['follow_up']
    assert follow['decisions']['public_supie']['status'] == 'closed_before_outcome'
    assert follow['decisions']['public_partly']['status'] == 'reached_outcome'
    tiro = follow['decisions']['public_tirolifesciencesltd']
    assert tiro['status'] == 'unknown'
    assert {event['kind'] for event in tiro['events']} == {'closed_liquidation','closed_register_removal'}
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
    assert all(row['registry']['filings_url'].endswith('/documents') and row['public_leads']
               and row['news_query'] and row['fund_query'] for row in searches)
    assert follow['decisions']['public_partly']['secondary']['status'] == 'unknown'
    assert follow['decisions']['public_supie']['secondary']['status'] == 'closed_before_outcome'


def test_secondary_requires_distinct_new_priced_capital_and_keeps_its_own_gate(tmp_path):
    from json import dumps

    path = tmp_path / 'follow-up.json'
    new_seed = event('other_financing', '2021-04-01', round_label='Seed', instrument='priced_equity').model_dump()
    data = dict(format_version='nz-cohort-follow-up:1', as_of='2026-11-20',
                sources=[dict(source_id='later_release', title='Test release', publisher='Test',
                              url='https://example.org/releases', kind='press_release',
                              published_on='2021-04-01', retrieved_on='2026-11-20')],
                events=[new_seed], reviews=[])
    path.write_text(dumps(data))
    assert outcome_audit([entry()], [], path)['secondary']['statuses']['unknown'] == 1
    data['next_round_proofs'] = [dict(event_id='test_event', priced_at='Price per new share',
                                     new_company_equity='New share issue', distinct_from_entry='Separate closing')]
    path.write_text(dumps(data))
    result = outcome_audit([entry()], [], path)
    assert result['statuses']['reached_outcome'] == 0
    assert result['secondary']['statuses']['reached_outcome'] == 1
    assert 'fewer_than_30_secondary_outcomes' in result['secondary']['gate_blockers']
    assert outcome_audit([entry('2021-04-01')], [], path)['secondary']['statuses']['unknown'] == 1
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
