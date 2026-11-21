"""Reproducibility and eligibility tests; reviews below are temporary fixtures."""

import copy
import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from backend.comparison_runs import replay
from backend.database import connect
from backend.main import create_app
from backend.retrieval import compare
from scripts.bootstrap import load_seed


@pytest.fixture
def database(tmp_path):
    path = tmp_path / 'comparison.sqlite'
    load_seed(path)
    return path


def test_historical_b0_golden_signatures(database):
    cases = json.loads((Path(__file__).parent / 'fixtures/b0_historical.json').read_text())
    with connect(database) as conn:
        for case in cases:
            result = compare(conn, **case['request'])
            signature = [
                [r['venture']['venture_id'], r['ranking_score'], r['query_token_coverage'], r['matched_terms']]
                for r in result['results']
            ]
            assert signature == case['signature']
            assert result['abstention_reason'] == case['abstention_reason']
            assert result['method']['version'] == 'b0-token-overlap-1.0'


def test_same_corpus_config_exports_identical_and_replays(database):
    with connect(database) as conn:
        first = compare(conn, query='clinical images software surgical planning')
        second = compare(conn, query='clinical images software surgical planning')
        assert first == second
        run = first['run']
        assert len(run['corpus_digest']) == 64
        assert len(run['selected_observations']) == 10
        assert {o['review_status'] for o in run['selected_observations']} == {'source_checked_owner_review_pending'}
        assert replay(conn, json.loads(json.dumps(run))) == first
    client = TestClient(create_app(database))
    response = client.post('/api/compare', json={'query': 'clinical images software surgical planning'}).json()
    replayed = client.post('/api/comparison-runs/replay', json=response['run'])
    assert replayed.status_code == 200
    assert replayed.json() == response


def test_record_refuses_tampering_and_changed_corpus(database):
    with connect(database) as conn:
        run = compare(conn, subject_id='v_formus')['run']
        altered = copy.deepcopy(run)
        altered['request']['query'] = 'changed'
        with pytest.raises(ValueError, match='checksum'):
            replay(conn, altered)
    with sqlite3.connect(database) as conn:
        conn.execute(
            "INSERT INTO review_events VALUES ('fixture-review','v_formus_product',NULL,'rejected','synthetic-test-reviewer','2026-11-18','Temporary fixture only')"
        )
    with connect(database) as conn:
        with pytest.raises(ValueError, match='Corpus changed'):
            replay(conn, run)
        changed = compare(conn, query='clinical images software surgical planning')
        assert changed['run']['corpus_digest'] != run['corpus_digest']
        assert 'v_formus_product' not in {o['observation_id'] for o in changed['run']['selected_observations']}
    client = TestClient(create_app(database))
    response = client.post('/api/comparison-runs/replay', json=run)
    assert response.status_code == 409


def test_unreviewed_seed_usable_only_under_disclosed_exploration(database):
    with connect(database) as conn:
        exploration = compare(conn, query='clinical images software surgical planning')
        accepted = compare(conn, query='clinical images software surgical planning', policy='accepted')
        historical = compare(conn, query='clinical images software surgical planning', cutoff='2026-11-18')
        assert (
            exploration['results'] and 'unreviewed publisher reports' in exploration['evidence_policy']['description']
        )
        assert not accepted['results'] and not accepted['run']['selected_observations']
        assert not historical['results'] and not historical['run']['selected_observations']
    client = TestClient(create_app(database))
    assert client.post('/api/compare', json={'cutoff': '2026-99-99'}).status_code == 422


def test_comparison_respects_caller_transaction_and_releases_own_snapshot(database):
    with connect(database) as conn:
        assert not conn.in_transaction
        compare(conn, query='clinical image software')
        assert not conn.in_transaction
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute(
            "INSERT INTO review_events VALUES ('pending-fixture','v_formus_product',NULL,'accepted','synthetic-test-reviewer','2026-11-18','Temporary uncommitted fixture')"
        )
        assert conn.in_transaction
        result = compare(conn, query='clinical image software', policy='accepted')
        assert conn.in_transaction
        assert any(o['observation_id'] == 'v_formus_product' for o in result['run']['selected_observations'])
        conn.rollback()
        assert (
            conn.execute("SELECT COUNT(*) FROM review_events WHERE review_event_id='pending-fixture'").fetchone()[0]
            == 0
        )
    finally:
        conn.close()


@pytest.mark.skipif(not hasattr(sqlite3, 'LEGACY_TRANSACTION_CONTROL'), reason='Python 3.12 explicit autocommit API')
def test_snapshot_released_with_python312_true_autocommit(database):
    conn = sqlite3.connect(database, autocommit=True)
    conn.row_factory = sqlite3.Row
    try:
        compare(conn, query='clinical image software')
        assert not conn.in_transaction
        with pytest.raises(LookupError):
            compare(conn, subject_id='missing')
        assert not conn.in_transaction
    finally:
        conn.close()
