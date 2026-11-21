#!/usr/bin/env python3
"""Verify the research pilot on disposable SQLite only; never writes research data."""

import argparse
import copy
import hashlib
import json
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.database import connect
from backend.ingestion import load_seed
from backend.research_adapter import dry_run_research, get_research_packet, import_research, import_research_connection
from backend.retrieval import compare


def snapshot(db):
    with sqlite3.connect(db) as conn:
        tables = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
        return {table: conn.execute('SELECT * FROM "' + table + '" ORDER BY 1,2').fetchall() for table in tables}


def signature(result):
    return [(r['venture']['venture_id'], r['ranking_score'], r['matched_terms']) for r in result['results']]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--packet', type=Path, default=ROOT / 'research/framework-v0.2.1/Two_Dossier_Research_Example.json'
    )
    parser.add_argument('--as-of', default='2026-11-18')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    original = json.loads(args.packet.read_bytes())
    with tempfile.TemporaryDirectory(prefix='vee-pilot-verify-') as temporary:
        db = Path(temporary) / 'pilot.sqlite'
        load_seed(db)
        baseline = snapshot(db)
        with connect(db) as conn:
            before_signature = signature(compare(conn, query='clinical images software surgical planning'))
        before_bytes = hashlib.sha256(db.read_bytes()).hexdigest()
        dry_run_research(args.packet, db_path=db, as_of=args.as_of)
        assert snapshot(db) == baseline
        assert hashlib.sha256(db.read_bytes()).hexdigest() == before_bytes, 'Dry run modified DB bytes'
        import_research(db, args.packet, as_of=args.as_of)
        imported = snapshot(db)
        for table, rows in baseline.items():
            if not table.startswith('research_'):
                assert imported[table] == rows, 'Original table changed: ' + table
        with connect(db) as conn:
            packet = get_research_packet(conn)
            assert packet == original, 'Research graph lost or changed fields'
            assert signature(compare(conn, query='clinical images software surgical planning')) == before_signature
            assert not compare(conn, query='clinical image software', policy='accepted')['results']
            assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
            assert not conn.execute('PRAGMA foreign_key_check').fetchall()
        import_research(db, args.packet, as_of=args.as_of)
        assert snapshot(db) == imported, 'Repeat import changed rows'
        conflict = copy.deepcopy(original)
        conflict['sources'].append(dict(conflict['sources'][0], source_id='src_synthetic_rollback_fixture'))
        conflict['observations'][0]['paraphrase'] = 'Synthetic immutable-conflict fixture, never research evidence.'
        conflict_path = Path(temporary) / 'conflict.json'
        conflict_path.write_text(json.dumps(conflict))
        try:
            import_research(db, conflict_path, as_of=args.as_of)
        except ValueError:
            pass
        else:
            raise AssertionError('Changed immutable record was accepted')
        assert snapshot(db) == imported, 'Failed graph import left partial writes'
        active = sqlite3.connect(db)
        try:
            active.execute('BEGIN')
            try:
                import_research_connection(active, args.packet, as_of=args.as_of)
            except ValueError as error:
                assert 'transaction' in str(error).lower()
            else:
                raise AssertionError('Active caller transaction accepted')
            assert active.in_transaction
            active.rollback()
        finally:
            active.close()
    report = {
        'status': 'PASS',
        'scope': 'Disposable database code verification; not source entailment or human acceptance',
        'checks': [
            'dry run leaves database bytes/rows unchanged',
            'original tables and review history preserved',
            'lossless packet graph roundtrip',
            'repeat import full-row equality',
            'immutable conflict whole-graph rollback',
            'active caller transaction refusal',
            'foreign keys/integrity',
            'B0 rankings preserved',
            'accepted-only isolation',
        ],
        'packet_sha256': hashlib.sha256(args.packet.read_bytes()).hexdigest(),
        'research_format': original['metadata']['format_version'],
        'accepted_records': original['metadata']['accepted_records_count'],
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
