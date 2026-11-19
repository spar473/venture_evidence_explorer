from copy import deepcopy

import pytest
from pydantic import ValidationError

from backend.cohort_audit import run_audit
from backend.cohort_follow_up import CoverageReview, OutcomeEvidence, assess
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
    assert follow['decisions']['discovery_cropsy']['observed_at_36_months'] is None
    assert follow['verified_observed_at_36_months'] > 0
    assert follow['observed_at_36_months'] is None
    assert sum(follow['statuses'].values()) == report['counts']['included']
    assert not follow['gate_ready']
    assert 'fewer_than_150_eligible_companies' in follow['gate_blockers']
