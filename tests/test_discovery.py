"""Discovery staging tests on supplied leads; synthetic failures/reviews stay temporary."""

import csv
import io
import json
import sqlite3
import pytest
from jsonschema.exceptions import ValidationError
from fastapi.testclient import TestClient
from backend.database import connect
from backend.ingestion import load_seed
from backend.discovery import (
    PACK,
    import_discovery,
    decode_packet,
    validate_packet,
    promotion_preview,
    import_decisions,
)
from backend.main import create_app


def snapshot(db):
    with sqlite3.connect(db) as c:
        return {
            r[0]: c.execute('SELECT * FROM "' + r[0] + '" ORDER BY rowid').fetchall()
            for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }


@pytest.fixture
def db(tmp_path):
    p = tmp_path / 'discovery.sqlite'
    load_seed(p)
    return p


@pytest.fixture
def staged(db):
    import_discovery(db)
    return TestClient(create_app(db)), db


def test_counts_repeat_preservation_and_overlap(db):
    before = snapshot(db)
    report = import_discovery(db)
    assert (
        report['counts']['candidates'] == 274
        and report['counts']['organisations'] == 27
        and report['counts']['listings'] == 365
        and report['promoted'] == 0
    )
    after = snapshot(db)
    for t in before:
        if not t.startswith('discovery_'):
            assert before[t] == after[t], t
    import_discovery(db)
    assert snapshot(db) == after
    with connect(db) as c:
        assert c.execute('SELECT raw_bytes FROM discovery_imports').fetchone()[0] == PACK.read_bytes()
        assert not c.execute('PRAGMA foreign_key_check').fetchall()
        assert c.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'


def test_failure_after_sources_and_immutable_conflict_roll_back(db, tmp_path):
    before = snapshot(db)

    def fail(stage, c):
        if stage == 'sources':
            raise RuntimeError('Synthetic failure after earlier writes')

    with pytest.raises(RuntimeError):
        import_discovery(db, failure_injector=fail)
    assert snapshot(db) == before
    import_discovery(db)
    before = snapshot(db)
    payload = decode_packet(PACK.read_bytes())
    payload['candidates'][0]['display_name'] = 'Synthetic conflicting replacement'
    p = tmp_path / 'conflict.json'
    p.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match='immutable'):
        import_discovery(db, p)
    assert snapshot(db) == before


def test_invalid_reference_and_unsupported_fields_before_writes(tmp_path):
    payload = decode_packet(PACK.read_bytes())
    payload['listings'][0]['source_id'] = 'missing'
    p = tmp_path / 'invalid.json'
    p.write_text(json.dumps(payload))
    db = tmp_path / 'absent.sqlite'
    with pytest.raises(ValueError, match='reference'):
        import_discovery(db, p)
    assert not db.exists()
    payload['candidates'][0]['invented_score'] = 0.9
    with pytest.raises(Exception):
        validate_packet(payload, '2026-11-18')


def test_queue_filters_alias_cases_and_promotion_refusal(staged):
    client, db = staged
    page = client.get('/api/discovery').json()
    assert page['total'] == page['staged_total'] == 274 and page['source_families_total'] == 27
    assert page['promoted_total'] == 0 and page['accepted_nz_population'] is None
    assert client.get('/api/discovery?year=2021').json()['total'] == 2
    assert client.get('/api/discovery?unknown_period=true').json()['total'] == 270
    assert client.get('/api/discovery?family=org_matu').json()['total'] > 1
    assert client.get('/api/discovery?gap=nz_inclusion').json()['total'] == 274
    view = client.get('/api/discovery/candidates/discovery_kura').json()
    assert any(d['id'] == 'discovery_kuradynamics' for d in view['duplicate_candidates'])
    alias = client.get('/api/discovery/candidates/discovery_aplenty').json()
    assert alias['name_links'][0]['other_name'] == 'Hot Lime Labs' and not alias['accepted']
    refusal = client.get('/api/discovery/candidates/discovery_rosterlab/promotion').json()
    assert refusal['writes'] == 0 and not refusal['ready_for_research_import'] and refusal['blockers']
    assert client.get('/api/ventures').json()['total'] == 10


def test_export_round_trip_preserves_nulls_and_grain(staged):
    client, db = staged
    response = client.get('/api/discovery/exports/candidates.csv')
    assert response.status_code == 200
    rows = list(csv.DictReader(io.StringIO(response.text)))
    assert len(rows) == len({r['record_id'] for r in rows}) == 274
    expected = {r['discovery_id']: r for r in decode_packet(PACK.read_bytes())['candidates']}
    for r in rows:
        assert json.loads(r['raw_json']) == expected[r['record_id']]
    assert all(json.loads(r['raw_json'])['first_investment_date'] is None for r in rows)
    assert client.get('/api/discovery/exports/invented.csv').status_code == 404


def test_review_actor_date_source_scope_and_adapter_preview(db, tmp_path):
    import_discovery(db)
    p = decode_packet(PACK.read_bytes())
    candidate = next(c for c in p['candidates'] if c['discovery_id'] == 'discovery_rosterlab')
    decisions = {
        'format_version': 'discovery-decisions:1',
        'decisions': [
            dict(
                decision_id='synthetic-' + kind,
                discovery_id=candidate['discovery_id'],
                kind=kind,
                disposition='resolved',
                actor_role='owner',
                actor_id='Synthetic test fixture only',
                decided_on='2026-11-18',
                source_ids=candidate['source_ids'][:1],
                evidence_date={'precision': 'year', 'lower_bound': '2026-01-01', 'upper_bound': '2026-12-31'},
                rationale='Synthetic review fixture, not an actual acceptance',
                target_research_subject_id='subj_rosterlab' if kind == 'identity' else None,
            )
            for kind in ('identity', 'nz_inclusion', 'period_scope')
        ],
    }
    path = tmp_path / 'synthetic.json'
    path.write_text(json.dumps(decisions))
    import_decisions(db, path)
    before = snapshot(db)
    import_decisions(db, path)
    assert snapshot(db) == before
    from backend.research_adapter import EXAMPLE

    with connect(db) as c:
        view = promotion_preview(c, 'discovery_rosterlab', EXAMPLE)
        assert (
            view['adapter_report']['status'] == 'valid_dry_run' and not view['ready_for_research_import']
        )  # source checked is not accepted
        assert any('acceptance' in b for b in view['blockers'])
    decisions['decisions'][0]['actor_role'] = 'assistant'
    path.write_text(json.dumps(decisions))
    with pytest.raises(ValueError):
        import_decisions(db, path)
    assert snapshot(db) == before


def test_invalid_discovery_source_urls_never_write(tmp_path):
    for url in ('https://invalid host/source', 'https://', 'https://user:secret@example.org/source'):
        payload = decode_packet(PACK.read_bytes())
        payload['sources'][0]['url'] = url
        path = tmp_path / 'bad-url.json'
        path.write_text(json.dumps(payload))
        db = tmp_path / 'never-created.sqlite'
        with pytest.raises((ValueError, ValidationError)):
            import_discovery(db, path)
        assert not db.exists()
