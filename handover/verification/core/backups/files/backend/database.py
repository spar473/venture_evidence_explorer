"""Explicit, checksummed migrations shared by the importer and application."""
import hashlib
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / 'outputs/venture_evidence.sqlite'


def migrate(conn):
    conn.execute('CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, sha256 TEXT NOT NULL)')
    for path in sorted((ROOT / 'schema/migrations').glob('*.sql')):
        sql = path.read_text()
        digest = hashlib.sha256(sql.encode()).hexdigest()
        existing = conn.execute('SELECT sha256 FROM schema_migrations WHERE version=?', (path.name,)).fetchone()
        if existing:
            if existing[0] != digest:
                raise ValueError('Applied migration changed: ' + path.name)
            continue
        # executescript commits implicitly; complete_statement preserves trigger bodies
        # while allowing the whole migration and its version to be one transaction.
        with conn:
            statement = ''
            for line in sql.splitlines(keepends=True):
                statement += line
                if sqlite3.complete_statement(statement):
                    conn.execute(statement)
                    statement = ''
            if statement.strip():
                raise ValueError('Incomplete migration: ' + path.name)
            conn.execute('INSERT INTO schema_migrations VALUES (?,?)', (path.name, digest))


def connect(path=DEFAULT_DB):
    conn = sqlite3.connect(f'file:{Path(path).resolve()}?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    return conn
