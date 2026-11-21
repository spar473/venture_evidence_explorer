"""Pilot integration contracts. Mutations/decisions here are synthetic fixtures."""

import hashlib
import json
import sqlite3
from pathlib import Path

import pytest
from backend.database import connect
from backend.ingestion import load_seed
from backend.research_adapter import (
    EXAMPLE,
    _proposal_id,
    dry_run_research,
    get_research_packet,
    import_research,
    import_research_connection,
    list_research_records,
    research_time_interval,
)
from backend.research_validation import (
    ResearchValidationError,
    decode_packet,
    validate_research_packet,
    validate_supplied_regressions,
)
from backend.retrieval import compare

AS_OF = '2026-11-18'


def snapshot(path):
    with sqlite3.connect(path) as conn:
        return {
            row[0]: conn.execute('SELECT * FROM "' + row[0] + '" ORDER BY rowid').fetchall()
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        }


def write_packet(tmp_path, packet, name='packet.json'):
    result = tmp_path / name
    result.write_text(json.dumps(packet, indent=2))
    return result


@pytest.fixture
def packet():
    return json.loads(EXAMPLE.read_bytes())


@pytest.fixture
def db(tmp_path):
    result = tmp_path / 'test.sqlite'
    load_seed(result)
    return result


def test_supplied_validator_and_regressions_unchanged(packet):
    counts = validate_research_packet(packet, AS_OF)
    assert counts['observations'] == 34 and counts['events'] == 6 and counts['review_events'] == 0
    result = validate_supplied_regressions(packet, AS_OF)
    assert len(result['negative_cases']) == 14 and len(result['regressions']) == 22


def test_dry_run_exhaustive_fields_without_creating_database(tmp_path):
    missing = tmp_path / 'must-not-exist.sqlite'
    report = dry_run_research(EXAMPLE, missing, as_of=AS_OF)
    assert report['status'] == 'valid_dry_run' and report['writes'] == 0 and not missing.exists()
    accounting = report['accounting']
    assert accounting['leaf_count'] == sum(accounting['totals'].values()) == len(accounting['fields'])
    assert len({field['path'] for field in accounting['fields']}) == len(accounting['fields'])
    assert accounting['totals']['unsupported'] == 0
    paths = {field['path'] for field in accounting['fields']}
    assert '/review_events' in paths and '/observations/0/related_party_id' in paths
    assert '/subjects/0/legal_name/value' in paths
    assert all(
        mapping['state'] == 'proposed' and mapping['decision_actor'] is None for mapping in report['identity_mappings']
    )


def test_apply_fresh_repeat_full_row_equality_and_raw_packet(tmp_path):
    db = tmp_path / 'fresh.sqlite'
    import_research(db, EXAMPLE, as_of=AS_OF)
    before = snapshot(db)
    import_research(db, EXAMPLE, as_of=AS_OF)
    assert snapshot(db) == before
    with connect(db) as conn:
        assert get_research_packet(conn) == json.loads(EXAMPLE.read_bytes())
        row = conn.execute('SELECT raw_bytes,packet_sha256 FROM research_imports').fetchone()
        assert row[0] == EXAMPLE.read_bytes() and row[1] == hashlib.sha256(row[0]).hexdigest()
        assert len(list_research_records(conn, 'observations')) == 34
        assert len(list_research_records(conn, 'subjects')) == 2
        assert conn.execute('SELECT COUNT(*) FROM research_identity_mappings').fetchone()[0] == 2
        assert (
            conn.execute('SELECT COUNT(*) FROM research_records WHERE collection=?', ('review_events',)).fetchone()[0]
            == 0
        )
        assert not conn.execute('PRAGMA foreign_key_check').fetchall()
        assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'


def test_original_rows_reviews_and_b0_unchanged(db):
    with sqlite3.connect(db) as conn:
        conn.execute(
            "INSERT INTO review_events VALUES ('synthetic-preservation-review','v_formus_product',NULL,'needs_review','synthetic reviewer','2026-11-18','Test preservation only')"
        )
    before = snapshot(db)
    with connect(db) as conn:
        ranking_before = compare(conn, query='clinical images software surgical planning')
    import_research(db, EXAMPLE, as_of=AS_OF)
    after = snapshot(db)
    for table, rows in before.items():
        if not table.startswith('research_'):
            assert after[table] == rows, table
    with connect(db) as conn:
        ranking_after = compare(conn, query='clinical images software surgical planning')
        from backend.comparison_runs import result_signature

        assert result_signature(ranking_after) == result_signature(ranking_before)
        assert ranking_after['run']['selected_observations'] == ranking_before['run']['selected_observations']
        assert ranking_after['run']['corpus_digest'] != ranking_before['run']['corpus_digest']


@pytest.mark.parametrize('point', ['after_source', 'during_events'])
def test_entire_graph_and_ledger_roll_back_on_injected_failure(db, point):
    before = snapshot(db)

    def fail(stage, conn):
        assert conn.in_transaction
        if stage == point:
            raise RuntimeError('Injected ' + point)

    with pytest.raises(RuntimeError, match=point):
        import_research(db, EXAMPLE, as_of=AS_OF, failure_injector=fail)
    assert snapshot(db) == before
    import_research(db, EXAMPLE, as_of=AS_OF)
    assert len(snapshot(db)['research_imports']) == 1


def test_refuses_caller_transaction_without_committing(db):
    with sqlite3.connect(db) as conn:
        conn.execute('BEGIN')
        conn.execute('CREATE TABLE synthetic_caller_owned(id)')
        with pytest.raises(ValueError, match='active transaction'):
            import_research_connection(conn, EXAMPLE, as_of=AS_OF)
        assert conn.in_transaction
        conn.rollback()
        assert not conn.execute("SELECT name FROM sqlite_master WHERE name='synthetic_caller_owned'").fetchall()


def test_changed_semantic_content_conflicts_without_writes(db, packet, tmp_path):
    import_research(db, EXAMPLE, as_of=AS_OF)
    before = snapshot(db)
    packet['observations'][0]['paraphrase'] = 'Synthetic mutation of source wording; not research evidence'
    changed = write_packet(tmp_path, packet)
    report = dry_run_research(changed, db, as_of=AS_OF)
    assert report['status'] == 'rejected' and report['immutable_conflicts']
    with pytest.raises(ValueError, match='Conflicting immutable research'):
        import_research(db, changed, as_of=AS_OF)
    assert snapshot(db) == before


def test_changed_whitespace_retains_new_raw_packet_without_duplicate_evidence(db, packet, tmp_path):
    import_research(db, EXAMPLE, as_of=AS_OF)
    before = snapshot(db)
    changed = tmp_path / 'whitespace.json'
    changed.write_text(json.dumps(packet, sort_keys=True, indent=5) + '\n\n')
    assert changed.read_bytes() != EXAMPLE.read_bytes()
    import_research(db, changed, as_of=AS_OF)
    after = snapshot(db)
    for table in ('research_records', 'research_links', 'research_time_values', 'research_identity_mappings'):
        assert after[table] == before[table]
    assert len(after['research_imports']) == 2
    assert len({row[5] for row in after['research_imports']}) == 1  # same semantic digest


def test_unsupported_fields_accounted_and_refused_before_database(tmp_path, packet):
    packet['observations'][0]['unsupported_payload'] = {'score': 0.95}
    path = write_packet(tmp_path, packet)
    db = tmp_path / 'never-created.sqlite'
    report = dry_run_research(path, db, as_of=AS_OF)
    assert report['status'] == 'rejected'
    assert any(
        row['path'] == '/observations/0/unsupported_payload/score' and row['category'] == 'unsupported'
        for row in report['accounting']['fields']
    )
    with pytest.raises(ResearchValidationError):
        import_research(db, path, as_of=AS_OF)
    assert not db.exists()


@pytest.mark.parametrize('raw', [b'{"metadata":{},"metadata":{}}', b'{"x":NaN}', b'{"x":1e9999}'])
def test_ambiguous_or_nonfinite_json_refused(raw):
    with pytest.raises(ResearchValidationError):
        decode_packet(raw)


def test_graph_semantics_rejected_before_writes(tmp_path, packet):
    packet['events'][0]['subject_id'] = 'subj_rosterlab'
    path = write_packet(tmp_path, packet)
    db = tmp_path / 'never-created.sqlite'
    with pytest.raises(ResearchValidationError, match='subject'):
        import_research(db, path, as_of=AS_OF)
    assert not db.exists()


def test_unknown_currency_targets_and_duplicate_candidates_survive(db):
    import_research(db, EXAMPLE, as_of=AS_OF)
    with connect(db) as conn:
        observations = list_research_records(conn, 'observations')
        prices = [o for o in observations if o['money']]
        assert len(prices) == 4 and all(o['money']['currency']['value'] is None for o in prices)
        events = list_research_records(conn, 'events')
        targets = [e for e in events if e['scenario'] == 'target']
        assert len(targets) == 1 and targets[0]['target_time']['value'] == '2025'
        assert targets[0]['occurrence_time']['value'] is None and targets[0]['event_state'] != 'completed'
        assert len([e for e in events if e['identity_resolution'] == 'unresolved_possible_duplicate']) == 2
        assert (
            conn.execute(
                "SELECT COUNT(*) FROM research_time_values WHERE precision='unknown' AND (lower_bound IS NOT NULL OR upper_bound IS NOT NULL)"
            ).fetchone()[0]
            == 0
        )
        assert research_time_interval(targets[0]['target_time']) == {
            'precision': 'year',
            'lower_bound': '2025-01-01',
            'upper_bound': '2025-12-31',
        }
        assert all(
            s['legal_name']['value'] is None and s['registration_id']['value'] is None
            for s in list_research_records(conn, 'subjects')
        )


def decision_document():
    return {
        'format_version': 'identity-mappings:1',
        'decisions': [
            {
                'mapping_id': 'synthetic-owner-mapping-decision',
                'subject_id': 'subj_rosterlab',
                'venture_id': 'v_rosterlab',
                'state': 'resolved',
                'scope': 'brand_project_only',
                'actor_role': 'owner',
                'actor_id': 'Synthetic test actor; not a real decision',
                'decided_on': AS_OF,
                'evidence_ids': ['obs_rl_problem'],
                'rationale': 'Synthetic mapping audit fixture only',
                'supersedes_mapping_id': _proposal_id('subj_rosterlab'),
            }
        ],
    }


def test_supplied_mapping_decision_lineage_without_legal_or_factual_acceptance(db, tmp_path):
    # This synthetic decision exists only in this disposable test database.
    path = write_packet(tmp_path, decision_document(), 'decision.json')
    import_research(db, EXAMPLE, as_of=AS_OF, mapping_decisions_path=path)
    before = snapshot(db)
    import_research(db, EXAMPLE, as_of=AS_OF, mapping_decisions_path=path)
    assert before == snapshot(db)
    with connect(db) as conn:
        decision = dict(conn.execute("SELECT * FROM research_identity_mappings WHERE state='resolved'").fetchone())
        assert decision['supersedes_mapping_id'] == _proposal_id('subj_rosterlab')
        assert decision['legal_identity_state'] == 'unresolved'
        assert conn.execute('SELECT COUNT(*) FROM review_events').fetchone()[0] == 0
        assert conn.execute("SELECT legal_name FROM ventures WHERE venture_id='v_rosterlab'").fetchone()[0] is None
        assert conn.execute('SELECT raw_bytes FROM research_mapping_documents').fetchone()[0] == path.read_bytes()


def test_missing_mapping_decision_actor_and_assistant_resolution_refused(db, tmp_path):
    before = snapshot(db)
    for field, value in (('actor_id', ''), ('actor_role', 'assistant'), ('scope', 'legal_identity')):
        document = decision_document()
        document['decisions'][0][field] = value
        path = write_packet(tmp_path, document, 'decision.json')
        with pytest.raises(ValueError):
            import_research(db, EXAMPLE, as_of=AS_OF, mapping_decisions_path=path)
        assert before == snapshot(db)


def test_invalid_source_uri_and_integer_app_schema_are_refused(tmp_path, packet):
    packet['sources'][0]['url'] = 'invalid url'
    path = write_packet(tmp_path, packet)
    report = dry_run_research(path, tmp_path / 'missing.sqlite', as_of=AS_OF)
    assert report['status'] == 'rejected' and any('/sources/0/url' == e['path'] for e in report['errors'])
    assert not (tmp_path / 'missing.sqlite').exists()
    from backend.ingestion import validate

    with pytest.raises(ValueError):
        validate(json.loads(EXAMPLE.read_bytes()))
    seed = Path(__file__).resolve().parents[1] / 'data/seed.json'
    assert dry_run_research(seed, as_of=AS_OF)['status'] == 'rejected'


def test_external_mapping_target_missing_is_preserved_quarantined(db, tmp_path, packet):
    packet['subjects'][0]['proposed_application_id'] = 'v_missing_no_invention'
    path = write_packet(tmp_path, packet)
    report = dry_run_research(path, db, as_of=AS_OF)
    mapping = next(m for m in report['identity_mappings'] if m['subject_id'] == packet['subjects'][0]['subject_id'])
    assert mapping['target_exists'] is False and mapping['state'] == 'proposed'
    import_research(db, path, as_of=AS_OF)
    with connect(db) as conn:
        assert not conn.execute("SELECT * FROM ventures WHERE venture_id='v_missing_no_invention'").fetchall()
        assert (
            next(
                s
                for s in list_research_records(conn, 'subjects')
                if s['subject_id'] == packet['subjects'][0]['subject_id']
            )['proposed_application_id']
            == 'v_missing_no_invention'
        )


def test_research_migration_failure_retry_keeps_no_partial_schema(tmp_path, monkeypatch):
    from backend import database

    directory = tmp_path / 'schema/migrations'
    directory.mkdir(parents=True)
    application_root = Path(__file__).resolve().parents[1]
    migration_source = application_root / 'schema/migrations/004_research_pilot.sql'
    migration = directory / migration_source.name
    migration.write_text(migration_source.read_text() + '\nINSERT INTO research_missing_table VALUES (1);\n')
    conn = sqlite3.connect(tmp_path / 'upgrade.sqlite')
    conn.execute('PRAGMA foreign_keys=ON')
    conn.executescript((application_root / 'schema/schema.sql').read_text())
    conn.execute('CREATE TABLE schema_migrations(version TEXT PRIMARY KEY,sha256 TEXT NOT NULL)')
    for original in sorted((application_root / 'schema/migrations').glob('00[123]_*.sql')):
        conn.executescript(original.read_text())
        conn.execute(
            'INSERT INTO schema_migrations VALUES (?,?)',
            (original.name, hashlib.sha256(original.read_bytes()).hexdigest()),
        )
        conn.commit()
    monkeypatch.setattr(database, 'ROOT', tmp_path)
    with pytest.raises(sqlite3.OperationalError, match='research_missing_table'):
        database.migrate(conn)
    assert not conn.execute("SELECT name FROM sqlite_master WHERE name LIKE 'research_%'").fetchall()
    assert conn.execute('SELECT COUNT(*) FROM schema_migrations').fetchone()[0] == 3
    migration.write_bytes(migration_source.read_bytes())
    database.migrate(conn)
    assert conn.execute('SELECT COUNT(*) FROM schema_migrations').fetchone()[0] == 4
    assert not conn.execute('PRAGMA foreign_key_check').fetchall()
    conn.close()


def test_connection_mapping_report_uses_actual_database(db, tmp_path):
    sidecar = write_packet(tmp_path, decision_document(), 'decision.json')
    with sqlite3.connect(db) as conn:
        report = import_research_connection(conn, EXAMPLE, as_of=AS_OF, mapping_decisions_path=sidecar)
        assert report['status'] == 'imported' and report['mapping_errors'] == []
        assert all(mapping['target_exists'] for mapping in report['identity_mappings'])
        assert not conn.in_transaction


def test_import_report_does_not_reread_input_after_validation(db, tmp_path):
    source = tmp_path / 'input.json'
    original = EXAMPLE.read_bytes()
    source.write_bytes(original)

    def mutate_path_after_validation(stage, conn):
        if stage == 'after_source':
            source.write_text('{"changed_after_validation":true}')

    report = import_research(db, source, as_of=AS_OF, failure_injector=mutate_path_after_validation)
    assert report['status'] == 'imported'
    assert report['packet_sha256'] == hashlib.sha256(original).hexdigest()
    with connect(db) as conn:
        assert conn.execute('SELECT raw_bytes FROM research_imports').fetchone()[0] == original
