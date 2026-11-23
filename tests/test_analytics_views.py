from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys

from fastapi.testclient import TestClient
import pytest

from backend.analytics_views import PRESETS, cohort_payload, dump_json, live_inputs, profile_payload, robustness
from backend.backtest_coverage import SUBJECTS
from backend.main import create_app
from scripts.export_static import export

ROOT = Path(__file__).resolve().parents[1]
SUPIE = 'public_supie'


@pytest.mark.parametrize('company_id', SUBJECTS)
def test_entry_profile_evidence_has_provenance_and_no_later_facts(company_id):
    profile = profile_payload(live_inputs(), company_id)
    assert profile['provisional']
    assert profile['cutoff'] == profile['recorded']['cutoff']
    for field in [*profile['fields'], *(fact for facts in profile['peer_facts'].values() for fact in facts)]:
        source = field['source']
        assert source['url'].startswith('https://')
        assert source['witness_on'] <= source['available_on'] <= profile['cutoff']
        assert source['locator']
        assert field['review_state'] == 'ai_adjudicated'
    assert 'events' not in profile
    assert set(profile['reveal']) == {'evidence_reviews'}
    assert all(review['reviewed_on'] for review in profile['reveal']['evidence_reviews'])
    for fact in [*profile['fields'], *(field for fields in profile['peer_facts'].values() for field in fields)]:
        assert 'reviewed_on' not in fact
    for key in profile['scorer']['peers']:
        cohort = cohort_payload(live_inputs())
        row = next(row for row in cohort['companies'] if row['company_id'] == key)
        assert row['end'] < profile['cutoff']


def test_cohort_counts_and_sources_match_frozen_audit():
    inputs = live_inputs()
    cohort = cohort_payload(inputs)
    assert cohort['candidate_records'] == 453
    assert cohort['provisional'] and not cohort['strict_gate_passed']
    assert len(cohort['companies']) == cohort['gates']['entries'] == 55
    counts = Counter(info['status'] for info in cohort['reveal'].values())
    assert counts == {key: value for key, value in inputs.cohort['follow_up']['statuses'].items() if value}
    assert counts['reached_outcome'] == 2
    assert counts['unknown'] == 33
    assert cohort['gates']['primary']['unknown_or_lost'] == 43
    for row in cohort['companies']:
        info = cohort['reveal'][row['company_id']]
        assert list(info['status_clock']) == sorted(info['status_clock'])
        for datum in [row['entry'], *info['events'], *info['fields'].values()]:
            assert datum['source']['locator'] and datum['source']['available_on']
            assert datum['source']['url'].startswith('https://') and datum['review_state']
    supie = cohort['reveal'][SUPIE]
    assert supie['status'] == 'closed_before_outcome'
    assert all(status != 'closed_before_outcome' for when, status, _ in supie['status_clock'] if when < '2023-11-09')


def test_scenario_endpoint_matches_expected_supie_presets_and_validates_overrides():
    client = TestClient(create_app())
    catalog = client.get(f'/api/views/profile/{SUPIE}').json()
    snapshots = dump_json(catalog['scorer']['peers'])
    for (key, (_, overrides)), total in zip(PRESETS.items(), (0, 4, 5, 3, 7, 0), strict=True):
        response = client.post(f'/api/scenario/{SUPIE}', json={'overrides': overrides})
        assert response.status_code == 200
        payload = response.json()
        assert payload == next(preset['result'] for preset in catalog['presets'] if preset['id'] == key)
        assert payload['scenario'] and payload['provisional'] and payload['qualifying_count'] == total
        assert payload['similarity_version'] == 'general-gower-b1:1'
        assert payload['cutoff'] == '2021-11-09'
        if key == 'business':
            scores = {peer['company_id']: peer['similarity'] for peer in payload['peers'] if peer['qualifies']}
            assert scores['public_socialclub'] == pytest.approx(0.669, abs=0.0005)
            assert scores['public_firstaml'] == pytest.approx(0.661, abs=0.0005)
            assert scores['public_narrative'] == pytest.approx(0.615, abs=0.0005)
            assert 'public_parcelport' in scores
    for overrides in (
        {'buyer': 'invented'},
        {'no_such_field': 'yes'},
        {'paid_pilot_or_revenue': 'unknown'},
        {'months_since_founding': -1},
        {'description': 'the'},
        {'market_focus': 'geographic'},
    ):
        assert client.post(f'/api/scenario/{SUPIE}', json={'overrides': overrides}).status_code == 422
    assert client.post(f'/api/scenario/{SUPIE}', json={'overrides': {'buyer': True}}).status_code == 422
    assert client.post('/api/scenario/missing', json={'overrides': {}}).status_code == 404
    assert dump_json(client.get(f'/api/views/profile/{SUPIE}').json()['scorer']['peers']) == snapshots


def test_robustness_reproducible_renormalised_and_tie_inclusive():
    inputs = live_inputs()
    first = robustness(inputs, SUPIE, 2000, 7)
    robustness.cache_clear()
    assert dump_json(robustness(inputs, SUPIE, 2000, 7)) == dump_json(first)
    expected = {
        'Product and customer': (0.476, 0.573),
        'Stage evidence': (0.480, 0.565),
        'Market': (0.507, 0.540),
        'Funding context': (0.524, 0.524),
    }
    actual = first['ranges']['public_socialclub']
    assert {key: tuple(round(value, 3) for value in bounds) for key, bounds in actual.items()} == expected
    assert first['baseline_ranks'][0] == ['public_socialclub']
    assert first['boundary_ties'][0]['draws'] == 2000
    assert len(first['boundary_ties'][0]['companies']) == 4
    assert set(first['membership'].values()) == {2000}
    assert len(first['perturbations']) == 8
    for row in first['perturbations']:
        assert sum(row['weights'].values()) == pytest.approx(1)
    client = TestClient(create_app())
    assert client.get(f'/api/robustness/{SUPIE}?draws=0').status_code == 422
    assert dump_json(client.get(f'/api/robustness/{SUPIE}?draws=2000&seed=7').json()) == dump_json(first)


def test_synthetic_cli_runs_without_the_real_cohort_or_analytics_modules(tmp_path):
    for filename in ('scripts/synthetic_cohort.py', 'backend/synthetic_method.py', 'backend/precedent_outlook.py'):
        isolated = tmp_path / filename
        isolated.parent.mkdir(exist_ok=True)
        shutil.copyfile(ROOT / filename, isolated)
    cmd = [sys.executable, '-I', 'scripts/synthetic_cohort.py', '--seed', '7']
    first, second = tmp_path / 'first', tmp_path / 'second'
    for destination in (first, second):
        subprocess.run([*cmd, '--output-dir', str(destination)], check=True, cwd=tmp_path, capture_output=True)
    for path in first.iterdir():
        data = path.read_bytes()
        assert data == (second / path.name).read_bytes()
        result = json.loads(data)
        assert result['synthetic'] and result['label'] == 'Synthetic cohort, no real company'
    assert len(json.loads((first / 'cohort.json').read_bytes())['companies']) == 500


def test_export_covers_all_views_subjects_and_presets(tmp_path):
    export(tmp_path)
    manifest = json.loads((tmp_path / 'manifest.json').read_bytes())['sha256']
    assert set(manifest) == {
        'views/cohort',
        'views/method',
        *(f'views/profile/{company_id}' for company_id in SUBJECTS),
        *(f'views/overview/{company_id}' for company_id in SUBJECTS),
        *(f'robustness/{company_id}' for company_id in SUBJECTS),
    }
    for path, digest in manifest.items():
        contents = (tmp_path / f'{path}.json').read_bytes()
        assert sha256(contents).hexdigest() == digest
        result = json.loads(contents)
        if path.startswith('views/profile/'):
            assert len(result['presets']) == len(PRESETS)
            overview_path = path.replace('views/profile/', 'views/overview/')
            overview = json.loads((tmp_path / f'{overview_path}.json').read_bytes())
            assert overview == {key: value for key, value in result.items() if key not in ('presets', 'scorer')}
