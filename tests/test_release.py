"""Behavioural contracts: provenance, identity, filters, abstention, atomicity."""

import copy
import csv
import io
import json
import sqlite3

import pytest
from fastapi.testclient import TestClient
from backend.database import connect
from backend.main import create_app
from backend.repository import browse
from scripts.bootstrap import ROOT, TABLES, load_seed


@pytest.fixture
def dataset(tmp_path):
    db = tmp_path / 'test.sqlite'
    original = load_seed(db)
    return db, original


@pytest.fixture
def client(dataset):
    with TestClient(create_app(dataset[0])) as c:
        yield c


def snapshot(db):
    with sqlite3.connect(db) as conn:
        return {
            t: conn.execute('SELECT * FROM ' + t + ' ORDER BY 1').fetchall()
            for t in (*TABLES, 'annotation_evidence', 'imports', 'review_events', 'schema_migrations')
        }


def import_variant(db, data, tmp_path):
    p = tmp_path / 'variant.json'
    p.write_text(json.dumps(data))
    return load_seed(db, p)


def test_repeat_and_atomic_conflict(dataset, tmp_path):
    db, original = dataset
    before = snapshot(db)
    load_seed(db)
    assert before == snapshot(db)
    broken = copy.deepcopy(original)
    broken['sources'].append(dict(broken['sources'][0], source_id='new_source'))
    broken['ventures'][0]['display_name'] = 'Changed'
    with pytest.raises(ValueError, match='Conflicting immutable'):
        import_variant(db, broken, tmp_path)
    assert snapshot(db) == before


def test_column_injection_and_schema_drift_refused(dataset, tmp_path):
    db, original = dataset
    before = snapshot(db)
    for key in ['unexpected', 'display_name) VALUES (1); DROP TABLE ventures; --']:
        broken = copy.deepcopy(original)
        broken['ventures'][0][key] = 'value'
        with pytest.raises(ValueError, match='columns'):
            import_variant(db, broken, tmp_path)
        assert snapshot(db) == before


def test_evidence_subject_and_dates(dataset, tmp_path):
    db, original = dataset
    for mutate in [
        lambda d: d['connections'][0].update(observation_id='v_rosterlab_connection'),
        lambda d: d['sources'][0].update(published_at='2027-01-01'),
        lambda d: d['annotations'][0].update(review_status='accepted'),
        lambda d: d['observations'][0].update(value_text=''),
    ]:
        broken = copy.deepcopy(original)
        mutate(broken)
        with pytest.raises(ValueError):
            import_variant(db, broken, tmp_path)
    with sqlite3.connect(db) as conn:
        assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        assert not conn.execute('PRAGMA foreign_key_check').fetchall()


def test_original_evidence_immutable_and_reviews_append(dataset):
    db, _ = dataset
    with sqlite3.connect(db) as conn:
        with pytest.raises(sqlite3.IntegrityError, match='Immutable'):
            conn.execute("UPDATE observations SET value_text='replacement'")
        conn.execute(
            "INSERT INTO review_events VALUES ('review-test','v_formus_product',NULL,'needs_review','actual-test-fixture','2026-11-17','Test event; not a real review')"
        )
        with pytest.raises(sqlite3.IntegrityError, match='Immutable'):
            conn.execute("DELETE FROM review_events")
        assert conn.execute('SELECT COUNT(*) FROM observations').fetchone()[0] == 20


def test_same_name_distinct_ids_and_aliases(dataset, tmp_path):
    db, original = dataset
    variant = copy.deepcopy(original)
    variant['ventures'].append(dict(variant['ventures'][0], venture_id='different_identity'))
    import_variant(db, variant, tmp_path)
    with connect(db) as conn:
        assert len(browse(conn, q='IVF support tool')['items']) == 2
    c = TestClient(create_app(db))
    result = c.post('/api/compare', json={'query': 'IVF support tool'}).json()
    assert 'Ambiguous' in result['abstention_reason']
    alias = c.get('/api/ventures?q=FormusLabs').json()
    assert alias['items'][0]['venture_id'] == 'v_formus'


def test_filter_overlap_actual_tables(dataset, tmp_path):
    db, original = dataset
    variant = copy.deepcopy(original)
    variant['awards'].append(
        dict(
            variant['awards'][0],
            award_id='test_overlap_award',
            programme='velocity_ideas',
            award_year=2026,
            event_date=None,
            source_id='src_ideas_2026',
        )
    )
    variant['connections'].append(
        dict(
            variant['connections'][0],
            connection_id='test_overlap_connection',
            connection_type='uoa_programme_participation',
        )
    )
    import_variant(db, variant, tmp_path)
    c = TestClient(create_app(db))
    query = lambda s: c.get('/api/ventures?' + s).json()['items']
    assert len(query('programme=velocity_100k&year=2025')) == 3
    assert any(
        v['venture_id'] == 'v_ivf_tool'
        for v in query('programme=velocity_ideas&year=2026&connection_type=uoa_programme_participation')
    )
    assert not query('programme=velocity_100k&year=2026')  # Cannot combine different award rows.
    roster = query('q=RosterLab')[0]
    assert roster['selection_bucket'] == 'uoa_origin'
    client_detail = c.get('/api/ventures/' + roster['venture_id']).json()
    assert any(c['connection_type'] == 'uoa_research_origin' for c in client_detail['connections'])


def test_all_assertions_resolve_correct_sources(client, dataset):
    _, original = dataset
    source_map = {s['source_id']: s for s in original['sources']}
    observations = {o['observation_id']: o for o in original['observations']}
    seen = 0
    for summary in client.get('/api/ventures').json()['items']:
        v = client.get('/api/ventures/' + summary['venture_id']).json()
        assert all(
            v[x] is None for x in ('legal_name', 'registration_id', 'current_operating_status', 'current_funding_stage')
        )
        for e in [*v['observations'], *v['awards']]:
            source = source_map[e['source_id']]
            assert e['venture_id'] == v['venture_id']
            assert all(e[k] == source[k] for k in ('url', 'publisher', 'published_at', 'retrieved_at'))
            assert e['locator'] and e['review_status']
            seen += 1
        for c in v['connections']:
            assert c['evidence']['value_text'] == observations[c['observation_id']]['value_text']
            assert c['evidence']['venture_id'] == v['venture_id']
        assert all(a['review_status'] == 'proposed' for a in v['proposed_annotations'])
    assert seen == 27
    formus = client.get('/api/ventures/v_formus').json()
    assert formus['awards'] == []
    alimetry = client.get('/api/ventures/v_alimetry').json()
    assert alimetry['observations'][0]['published_at'] == '2021-04-08'


def test_missing_empty_errors_and_injection(client, tmp_path):
    assert client.get('/api/ventures?q=unfindable').json()['filtered_ventures'] == 0
    assert client.get('/api/ventures?q=%25').json()['filtered_ventures'] == 0
    assert client.get("/api/ventures?q=' OR 1=1 --").json()['filtered_ventures'] == 0
    assert client.get('/api/ventures/missing').status_code == 404
    assert client.get('/api/ventures?year=word').status_code == 422
    assert client.get('/api/exports/missing.csv').status_code == 404
    broken = TestClient(create_app(tmp_path / 'missing.sqlite'))
    assert broken.get('/api/ventures').status_code == 503


def test_comparison_modes_self_exclusion_and_proposals(client):
    for mode in ('product_customer', 'commercialisation'):
        a = client.post('/api/compare', json={'subject_id': 'v_formus', 'mode': mode}).json()
        b = client.post('/api/compare', json={'subject_id': 'v_formus', 'mode': mode}).json()
        assert a == b and 0 < len(a['results']) <= 3
        assert not a['annotations_used']
        assert all(r['venture']['venture_id'] != 'v_formus' for r in a['results'])
        assert a['method']['version'] == 'b0-token-overlap-1.0'
        for r in a['results']:
            assert len(r['matched_terms']) >= 2 and r['query_token_coverage'] >= 0.15
            assert all(e['observation']['field'] in a['method']['fields'][mode] for e in r['evidence'])
    alias = client.post('/api/compare', json={'query': 'FormusLabs'}).json()
    assert alias['subject']['venture_id'] == 'v_formus'
    assert all(r['venture']['venture_id'] != 'v_formus' for r in alias['results'])
    described = client.post('/api/compare', json={'query': 'Formus Labs imaging software surgery planning'}).json()
    assert described['subject']['venture_id'] == 'v_formus'
    assert all(r['venture']['venture_id'] != 'v_formus' for r in described['results'])
    stage = client.post('/api/compare', json={'mode': 'stage_milestone', 'query': 'first paid sales'}).json()
    assert not stage['results'] and 'Insufficient' in stage['abstention_reason']
    assert client.post('/api/compare', json={'subject_id': 'missing'}).status_code == 404
    assert client.post('/api/compare', json={'mode': 'invented'}).status_code == 422


def test_irrelevant_empty_and_proposed_only_queries(client):
    for text in (
        '',
        'the and university venture',
        'blockchain quantum cryptocurrency',
        'Clinical data access, validation and clinician workflow',
    ):
        # Last phrase appears in proposed comparison angles, not eligible product descriptions.
        a = client.post('/api/compare', json={'query': text}).json()
        assert a['results'] == [] and a['abstention_reason']
    result = client.post('/api/compare', json={'query': 'clinical images software surgical planning'}).json()
    assert result['results']
    for r in result['results']:
        assert r['evidence'] and r['unavailable_evidence']
        assert 'unknown' in r['wording_differences']['meaning']


def test_proposal_changes_cannot_change_retrieval(dataset, tmp_path):
    db, original = dataset
    before = (
        TestClient(create_app(db))
        .post('/api/compare', json={'query': 'clinical images software surgical planning'})
        .json()
    )
    # Add new proposed annotations, which must not enter features or ranking.
    variant = copy.deepcopy(original)
    a = dict(
        variant['annotations'][0], annotation_id='new_proposal', value_text='clinical images software surgical planning'
    )
    variant['annotations'].append(a)
    import_variant(db, variant, tmp_path)
    after = (
        TestClient(create_app(db))
        .post('/api/compare', json={'query': 'clinical images software surgical planning'})
        .json()
    )
    signature = lambda x: [(r['venture']['venture_id'], r['ranking_score'], r['matched_terms']) for r in x['results']]
    assert signature(before) == signature(after)


def test_csvs_analytics_and_denominators(client):
    data = client.get('/api/analytics').json()
    assert 'Selected sample' in data['scope']
    assert sum(r['recorded_awards'] for r in data['tables']['programme_recognition']) == 7
    assert len(data['tables']['source_coverage']) == 10
    for name in (
        'programme_recognition',
        'connection_coverage',
        'source_coverage',
        'raw_observations',
        'proposed_annotations',
    ):
        response = client.get('/api/exports/' + name + '.csv')
        assert response.status_code == 200
        records = list(csv.DictReader(io.StringIO(response.text)))
        assert records
    ages = data['tables']['source_coverage']
    assert all(r['as_of_date'] and r['latest_source_age_days'] >= 0 for r in ages)


def test_unreviewed_evaluation_templates_untouched():
    assert all(q['relevance_labels'] is None for q in json.loads((ROOT / 'evaluation/queries.json').read_text()))
    rows = list(csv.DictReader((ROOT / 'evaluation/judgments.csv').open()))
    assert all(not r.get('relevance_grade') for r in rows)
