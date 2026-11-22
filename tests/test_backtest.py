"""Preview contracts, preregistered evidence clocks and numeric cross-checks."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys

from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest

from backend.backtest import BacktestInputs, FROZEN_OUTCOME_DATE, date_bounds, render_backtest
from backend.backtest_coverage import PREVIEW_LABEL, SUBJECTS
from backend.main import create_app
from backend.precedent_similarity_general import categorical_score, description_idf, normalise, score
from backend.reference_pool import EventDate
from backend.witnessed_snapshots import BacktestSnapshotPacket
from scripts.healthtech_demo import prepare_demo


@pytest.fixture(scope='module')
def inputs():
    return BacktestInputs()


@pytest.mark.parametrize('company_id', SUBJECTS)
@pytest.mark.parametrize('mode', ['strict', 'lenient'])
def test_preview_payload_provenance_and_historical_clocks(inputs, company_id, mode):
    cutoff = render_backtest(inputs, company_id, mode).subject.cutoff
    with TestClient(create_app()) as client:
        response = client.get(f'/api/backtest/{company_id}?witness_mode={mode}')
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload['provisional'] is True and payload['label'] == PREVIEW_LABEL
    assert payload['peer_history'] == 'as_of_anchor' and not payload['hindsight']
    assert company_id not in payload['eligible_peer_ids']
    for peer_id in payload['eligible_peer_ids']:
        peer_entry = EventDate.model_validate(inputs.entries[peer_id]['date'])
        assert date_bounds(peer_entry)[1] < cutoff
    groups = [payload['subject'], *payload['nearest_available'], *payload['nearest_candidates'], *payload['comps']]
    for group in groups:
        for field in group['fields']:
            source = field['source']
            assert (
                source['source_id']
                and source['locator']
                and source['publisher']
                and source['url'].startswith('https://')
            )
            assert source['witness_id'] and source['witness_on'] <= source['available_on'] <= cutoff
            start = date_bounds(EventDate.model_validate(group['entry']))[0]
            assert (source['published_on'] or source['witness_on']) <= source['available_on']
            assert field['review_state'] == 'ai_adjudicated'
            if mode == 'strict' or group == payload['subject']:
                assert source['available_on'] <= start and field['delay_days'] == 0
            else:
                assert 0 <= field['delay_days'] <= 90
        for event in group.get('history', {}).get('events', []):
            assert not event['hindsight'] and event['source']['witness_id'] and event['source']['locator']
            assert date_bounds(EventDate.model_validate(event['date']))[1] <= cutoff
            assert event['source']['available_on'] <= cutoff
    assert all(peer['not_a_comp'] for peer in payload['nearest_available'])
    assert not re.search(r'\b(?:ceiling|typical|floor)\b', str(payload['nearest_available']), re.I)
    reveal = payload.pop('reveal')
    for event in reveal['events'] + reveal['later_events']:
        assert date_bounds(EventDate.model_validate(event['date']))[0] > cutoff
        assert event['event_id'] not in str(payload)
        assert event['review_state'] and event['source']['url'] and event['source']['locator']
        assert event['source']['available_on']
    # Includes dates embedded in prose, URLs and locators, not just typed date fields.
    assert all(date <= cutoff for date in re.findall(r'\b\d{4}-\d{2}-\d{2}\b', str(payload)))
    assert reveal['evidence_reviews'] or not payload['subject']['fields']


def test_current_subject_results_and_hindsight(inputs):
    supie = render_backtest(inputs, 'public_supie')
    assert supie.subject.entry_round_source and supie.qualifying_count == 0
    assert supie.abstention == 'too_few_peers' and not supie.comps
    assert supie.reveal and supie.reveal.status == 'closed_before_outcome'
    assert [event.kind for event in supie.reveal.events] == ['voluntary_administration', 'closed_liquidation']
    assert [event.kind for event in supie.reveal.later_events] == ['closed_register_removal']
    today = render_backtest(inputs, 'public_supie', history='today')
    assert today.hindsight and today.corpus_sha256 == supie.corpus_sha256
    assert today.nearest_candidates == supie.nearest_candidates
    assert any(event.hindsight for peer in today.nearest_available for event in peer.history.events)
    for peer in today.nearest_available:
        for event in peer.history.events:
            assert event.hindsight == (event.source.available_on > supie.subject.cutoff)
            assert event.source.available_on <= FROZEN_OUTCOME_DATE
    for company in ('public_partly', 'discovery_halter'):
        case = render_backtest(inputs, company)
        assert case.abstention == 'no_subject_evidence' and not case.nearest_available
        assert case.reveal and case.reveal.status == 'reached_outcome'


def test_strict_refusal_and_labelled_preview_errors():
    with TestClient(create_app()) as client:
        result = client.get('/api/backtest/public_supie?track=strict').json()
        assert result['abstention'] == 'strict_gate'
        assert not result['provisional'] and not result['strict_gate_passed']
        assert not result['subject']['fields'] and result['reveal'] is None
        for query, status in (('unknown', 404), ('public_supie?peer_history=future', 422)):
            response = client.get(f'/api/backtest/{query}')
            assert response.status_code == status
            assert response.json()['provisional'] and response.json()['label'] == PREVIEW_LABEL


def test_vocabulary_exact_partial_cross_branch_flat_root_and_unknown():
    assert categorical_score('buyer', 'enterprise', 'enterprise') == 1
    assert categorical_score('buyer', 'business', 'enterprise') == 0.5
    assert categorical_score('buyer', 'enterprise', 'small_business') == 0.5
    assert categorical_score('buyer', 'small_business', 'household') == 0
    assert categorical_score('buyer', 'business', 'consumer') == 0
    assert categorical_score('buyer', 'root', 'root') is None
    assert categorical_score('buyer', 'unsupported', 'unsupported') is None
    assert categorical_score('market_focus', 'new_zealand', 'international') == 0
    assert categorical_score('market_focus', 'geographic', 'new_zealand') is None
    assert normalise({'buyer': '  SMBs  ', 'sector_normalised': ' CLEAN   TECHNOLOGY '}) == (
        {'buyer': 'small_business', 'sector_normalised': 'cleantech'},
        {},
    )
    assert normalise({'buyer': 'wholesalers'}) == ({}, {'buyer': 'wholesalers'})
    assert not score({}, {}, {}).fields
    assert score({'description': 'the'}, {'description': 'of the'}, {}).coverage == 0
    numeric = score(
        {'round_size_band': 'lt0.5m', 'months_since_founding': 121, 'prototype': 'yes'},
        {'round_size_band': '5m_to_lt10m', 'months_since_founding': 0, 'prototype': 'no'},
        {},
    )
    assert numeric.fields == {'prototype': 0, 'round_size_band': 0.25, 'months_since_founding': 0}
    assert score({'months_since_founding': 30}, {'months_since_founding': 60}, {}).fields == {
        'months_since_founding': 0.75
    }


def test_hand_checked_real_pairs(inputs):
    supie = render_backtest(inputs, 'public_supie')
    top = supie.nearest_available[0]
    assert top.company_id == 'public_socialclub'
    assert top.similarity == pytest.approx(0.5236665852, abs=0.0005)
    assert top.coverage == pytest.approx(0.5125, abs=0.0005)
    assert [(d.similarity, d.coverage) for d in top.dimensions] == [
        (pytest.approx(0.0183807661), 0.75),
        (0.75, 1),
        (1, 1 / 3),
        (None, 0),
    ]
    narrative = render_backtest(inputs, 'public_narrative')
    social = next(peer for peer in narrative.nearest_available if peer.company_id == 'public_socialclub')
    assert social.similarity == pytest.approx(0.6875, abs=0.0005)
    assert social.coverage == pytest.approx(0.4375, abs=0.0005)
    assert [(d.similarity, d.coverage) for d in social.dimensions] == [(0.5, 0.75), (0.5, 0.5), (1, 1 / 3), (None, 0)]


def test_uncovered_and_future_descriptions_do_not_fit_idf(inputs):
    case = render_backtest(inputs, 'public_supie')
    assert set(case.corpus_ids) == {'public_supie', *case.covered_peer_ids}
    idf = description_idf([{'description': 'only covered text'}])
    assert idf['outofcorpus'] > idf['covered']
    modified = deepcopy(inputs)
    original = case.corpus_sha256
    # Synthetic attack bypasses Pydantic to probe the runtime cap independently.
    field = next(item for item in modified.profiles['public_narrative'] if item.name == 'description')
    field.value = 'FUTURE_DESCRIPTION_MUST_NOT_LEAK'
    field.effective_on = '2021-11-10'
    with pytest.raises(ValidationError, match='entry evidence cutoff'):
        BacktestSnapshotPacket.model_validate(modified.packet.model_dump())
    assert 'FUTURE_DESCRIPTION_MUST_NOT_LEAK' not in render_backtest(modified, 'public_supie').model_dump_json()
    field.timing = 'lenient'
    strict = render_backtest(modified, 'public_supie')
    lenient = render_backtest(modified, 'public_supie', mode='lenient')
    assert strict.corpus_sha256 != original
    assert lenient.corpus_sha256 == strict.corpus_sha256
    assert 'FUTURE_DESCRIPTION_MUST_NOT_LEAK' not in lenient.model_dump_json()


def test_historical_role_does_not_use_later_publication_or_mutable_register(inputs):
    history = deepcopy(inputs.history)
    company = 'discovery_halter'
    entry = inputs.entries[company]
    when = EventDate.model_validate(entry['date'])
    known, role = history.peer(entry, when, '2018-06-22', 'as_of_anchor')
    assert any(event.kind == 'series_a' for event in known.events)
    assert role and role.rank == 3
    before, role = history.peer(entry, when, '2018-06-21', 'as_of_anchor')
    assert not any(event.kind == 'series_a' for event in before.events) and role is None
    history.witnesses['halter_idealog_2018'].clear()
    no_proof, role = history.peer(entry, when, '2018-06-22', 'as_of_anchor')
    assert not any(event.kind == 'series_a' for event in no_proof.events) and role is None
    assert history.events('public_supie', FROZEN_OUTCOME_DATE, allow_retrospective=False) == []


def test_preview_run_is_byte_reproducible_and_separately_labelled(tmp_path):
    files = []
    for name in ('first', 'second'):
        destination = tmp_path / name
        run = subprocess.run(
            [sys.executable, 'scripts/preview_backtest.py', '--output-dir', str(destination)],
            check=True,
            capture_output=True,
            text=True,
        )
        assert PREVIEW_LABEL in run.stdout
        files.append(next(destination.glob('backtest-*.json')))
        assert next(destination.glob('environment-*.json')).exists()
    assert files[0].read_bytes() == files[1].read_bytes()
    assert files[0].stem == 'backtest-' + sha256(files[0].read_bytes()).hexdigest()


def test_witnessed_profile_http_bytes_match_main(tmp_path):
    # Raw response hashes captured from main at 0b7e5d839553768c479639adc7717cb6cbd91672.
    cases = (Path(__file__).parent / 'fixtures/witnessed-b0-main.jsonl').read_text().splitlines()
    with TestClient(create_app(prepare_demo(tmp_path)['database'])) as client:
        for case in cases:
            path, digest = json.loads(case)
            response = client.get(path)
            assert response.status_code == 200
            assert response.json()['similarity_version'] == 'witnessed-gower-b0:3'
            assert sha256(response.content).hexdigest() == digest
