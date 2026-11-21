import json

import pytest

from backend.cohort_audit import ENTRIES, PACK, EntryReport, PublicEntryEvidence, decide, run_audit


def report(**changes):
    return EntryReport.model_validate(
        {
            'company_id': 'public_test',
            'name': 'Sample venture',
            'source_id': 'release',
            'locator': 'Opening',
            'sector': 'Software',
            'date': {'precision': 'day', 'value': '2018-02-14'},
            'date_basis': 'announced_completed',
            'label': 'Seed round',
            'institutional_investor': 'Example Fund',
            'nz_basis': 'founded_or_headquartered',
            'first_basis': 'explicit_first',
            'passage': 'Source claim',
            **changes,
        }
    )


def test_full_rule_and_boundaries():
    assert decide([report()], False)[0] == 'included'
    assert (
        decide([report(date={'value': '2012', 'precision': 'year'}, date_basis='reported_occurrence')], False)[0]
        == 'included'
    )
    assert (
        decide([report(date={'value': '2022-12', 'precision': 'month'}, date_basis='reported_month')], False)[0]
        == 'included'
    )
    assert decide([report(date={'value': '2023-01-01', 'precision': 'day'})], False)[0] == 'outside_entry_window'
    assert decide([report(label='seed extension')], False)[2] == ['qualifying_round_label']
    assert decide([report(label='Pre-Series A')], False)[2] == ['qualifying_round_label']


def test_historical_round_one_and_current_portfolio_cannot_establish_entry():
    candidate = report(first_basis='publisher_round_one', nz_basis='reported_location', institutional_investor=None)
    assert decide([candidate], False)[2] == [
        'first_institutional_round',
        'named_institutional_investor',
        'nz_founding_or_headquarters',
    ]
    assert decide([], False) == ('unresolved', None, ['dated_entry_evidence'])
    assert decide([report()], True)[2] == ['company_identity']


def test_earlier_seed_lead_prevents_picking_a_later_known_round():
    prior = report(
        date={'value': '2017-12', 'precision': 'month'},
        date_basis='reported_month',
        first_basis='publisher_round_one',
        institutional_investor=None,
    )
    assert decide([prior, report()], False)[2] == ['earlier_or_conflicting_round']
    corroboration = report(
        date={'value': '2018-02', 'precision': 'month'}, date_basis='reported_month', first_basis='publisher_round_one'
    )
    assert decide([corroboration, report()], False)[0] == 'included'


def test_evidence_rejects_future_dates_and_unknown_corroboration():
    record = report().model_dump()
    source = dict(
        publisher='Test',
        url='https://example.org/release',
        retrieved_on='2026-11-20',
        publication={'value': '2018-02-13', 'precision': 'day'},
        scope='Fixture for validation',
    )
    raw = dict(
        format_version='nz-cohort-entry-evidence:1',
        captured_on='2026-11-20',
        reports=[record],
        sources={'release': source},
        benchmarks=[],
    )
    with pytest.raises(ValueError, match='event follows'):
        PublicEntryEvidence.model_validate(raw)
    source['publication']['value'] = '2018-02-14'
    record['corroborating_source_ids'] = ['unknown']
    with pytest.raises(ValueError, match='corroborating entry'):
        PublicEntryEvidence.model_validate(raw)


def test_bundled_run_is_stable_and_does_not_promote_portfolio_listings():
    result = run_audit()
    assert result == run_audit()
    assert result['candidate_records'] > result['discovery_leads'] == 274
    assert result['discovery_listings_with_investment_date'] == 0
    assert sum(result['counts'].values()) == result['candidate_records']
    assert sum(result['included_by_vintage'].values()) == result['counts']['included']
    assert sum(result['included_by_sector'].values()) == result['counts']['included']
    assert result['outcome_gate'] == 'withheld'
    assert result['follow_up']['observed_at_36_months'] is None
    rows = {row['company_id']: row for row in result['decisions']}
    assert rows['discovery_formuslabs']['status'] == 'included'
    assert rows['discovery_halter']['status'] == 'included'
    assert rows['discovery_halter']['entry']['date']['value'] == '2016-12'
    assert rows['discovery_toku']['status'] == rows['discovery_tokueyes']['status'] == 'unresolved'


def test_entry_does_not_use_outcomes_and_registry_requires_positive_source(tmp_path):
    original = run_audit()
    discovery = json.loads(PACK.read_bytes())
    discovery['targeted_outcome_events'] = []
    staged = tmp_path / 'without-outcomes.json'
    staged.write_text(json.dumps(discovery))
    evidence = json.loads(ENTRIES.read_bytes())
    statuses = evidence.pop('registry_statuses')
    audit_input = tmp_path / 'without-registry.json'
    audit_input.write_text(json.dumps(evidence))
    entry_only = run_audit(staged, audit_input)
    assert entry_only['decisions'] == original['decisions']
    assert entry_only['follow_up']['registry_confirmed_closures'] == 0
    assert original['follow_up']['registry_confirmed_closures'] >= 12
    assert [row['status'] for row in statuses if row['company_id'] == 'public_supie'] == [
        'voluntary_administration',
        'liquidation',
        'removed',
    ]
    assert [row['status'] for row in statuses if row['company_id'] == 'public_photonicinnovationsltd'] == ['removed']
    evidence['registry_statuses'] = [row for row in statuses if row['status'] == 'voluntary_administration']
    audit_input.write_text(json.dumps(evidence))
    assert run_audit(staged, audit_input)['follow_up']['registry_confirmed_closures'] == 0
    evidence['registry_statuses'] = statuses
    evidence['sources']['supie_register']['url'] = 'https://example.org/7775376'
    with pytest.raises(ValueError, match='official company-number record'):
        PublicEntryEvidence.model_validate(evidence)


def test_expansion_preserves_first_round_dates_aliases_and_open_conflicts():
    report = run_audit()
    decisions = {row['company_id']: row for row in report['decisions']}
    expected = {
        'discovery_aplenty': '2017-11',
        'public_rocos': '2017-11',
        'discovery_maramalabs': '2019-02',
        'public_safestack': '2021-09',
        'discovery_liquium': '2022-05',
    }
    for company_id, month in expected.items():
        decision = decisions[company_id]
        assert decision['status'] == 'included'
        assert decision['entry']['date'] == {'value': month, 'precision': 'month'}
    assert len(decisions['public_rocos']['source_reports']) == 2
    assert 'public_rocosgloballimited' not in decisions
    assert 'public_safestacklimited' not in decisions
    assert all(
        decisions[key]['status'] == 'unresolved'
        for key in (
            'public_nectar',
            'public_googlyinclimited',
            'public_croplogic',
            'public_veritideltd',
        )
    )
