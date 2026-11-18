#!/usr/bin/env python3
"""Standard-library migration portability check, including Python 3.12 autocommit."""
import sqlite3
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend import database


def check_mode(settings):
    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary)
        migrations=root/'schema/migrations'
        migrations.mkdir(parents=True)
        path=migrations/'probe.sql'
        valid='''CREATE TABLE probe(value TEXT);
CREATE VIEW probe_view AS SELECT * FROM probe;
CREATE TRIGGER probe_trigger AFTER INSERT ON probe BEGIN UPDATE probe SET value=upper(NEW.value); END;
'''
        path.write_text(valid+'INSERT INTO nonexistent VALUES (1);\n')
        previous=database.ROOT
        database.ROOT=root
        try:
            with sqlite3.connect(root/'probe.sqlite',**settings) as conn:
                try:
                    database.migrate(conn)
                except sqlite3.OperationalError:
                    pass
                else:
                    raise AssertionError('Injected failure was accepted')
                assert not conn.in_transaction
                assert not conn.execute("SELECT name FROM sqlite_master WHERE name LIKE 'probe%'").fetchall()
                assert conn.execute('SELECT COUNT(*) FROM schema_migrations').fetchone()[0]==0
                path.write_text(valid)
                database.migrate(conn)
                assert not conn.in_transaction
                assert conn.execute('SELECT COUNT(*) FROM schema_migrations').fetchone()[0]==1
                conn.execute('BEGIN')
                try:
                    database.migrate(conn)
                except ValueError as error:
                    assert 'active transaction' in str(error)
                else:
                    raise AssertionError('Caller transaction accepted')
                assert conn.in_transaction
                conn.execute('ROLLBACK')
        finally:
            database.ROOT=previous


if __name__=='__main__':
    modes=[{}, {'isolation_level':None}]
    if sys.version_info >= (3,12):
        modes.append({'autocommit':True})
    for mode in modes:
        check_mode(mode)
    print(f'PASS: Python {sys.version.split()[0]}, SQLite {sqlite3.sqlite_version}; {len(modes)} transaction modes; failure rollback, retry and caller transaction refusal')
