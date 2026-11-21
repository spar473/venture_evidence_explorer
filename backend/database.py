"""Explicit, checksummed migrations shared by the importer and application."""

import hashlib
import sqlite3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / 'outputs/venture_evidence.sqlite'


def migrate(conn):
    """Own each migration transaction; never commit a caller's transaction."""
    if conn.in_transaction:
        raise ValueError('migrate requires a connection without an active transaction')
    conn.execute('BEGIN IMMEDIATE')
    try:
        conn.execute('CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, sha256 TEXT NOT NULL)')
        conn.execute('COMMIT')
    except BaseException:
        if conn.in_transaction:
            conn.execute('ROLLBACK')
        raise
    for path in sorted((ROOT / 'schema/migrations').glob('*.sql')):
        raw = path.read_bytes()
        sql = raw.decode('utf-8')
        digest = hashlib.sha256(raw).hexdigest()
        # Read and apply under the same lock, including ledger insertion.
        conn.execute('BEGIN IMMEDIATE')
        try:
            existing = conn.execute('SELECT sha256 FROM schema_migrations WHERE version=?', (path.name,)).fetchone()
            if existing:
                if existing[0] != digest:
                    raise ValueError('Applied migration changed: ' + path.name)
            else:
                statement = ''
                for char in sql:
                    statement += char
                    if char == ';' and sqlite3.complete_statement(statement):
                        # Migration files must not escape our transaction ownership.
                        meaningful = re.sub(r'--[^\n]*|/\*.*?\*/', '', statement, flags=re.S).strip()
                        if meaningful.split(None, 1)[0].upper().rstrip(';') in {
                            'BEGIN',
                            'COMMIT',
                            'END',
                            'ROLLBACK',
                            'SAVEPOINT',
                            'RELEASE',
                        }:
                            raise ValueError('Transaction control in migration: ' + path.name)
                        conn.execute(statement)
                        statement = ''
                if re.sub(r'--[^\n]*|/\*.*?\*/', '', statement, flags=re.S).strip():
                    raise ValueError('Incomplete migration: ' + path.name)
                conn.execute('INSERT INTO schema_migrations VALUES (?,?)', (path.name, digest))
            conn.execute('COMMIT')
        except BaseException:
            if conn.in_transaction:
                conn.execute('ROLLBACK')
            raise


def connect(path=DEFAULT_DB):
    conn = sqlite3.connect(f'file:{Path(path).resolve()}?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    return conn
