#!/usr/bin/env python3
"""Restore the archived handover to a new local database; never overwrite one."""

import argparse
import json
import sqlite3
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--from', dest='source', type=Path, default=ROOT / 'handover/snapshots/vee-2026-11-18.sqlite')
    p.add_argument('--to', dest='destination', type=Path, default=ROOT / 'outputs/venture_evidence.sqlite')
    a = p.parse_args()
    source = a.source.resolve()
    destination = a.destination.resolve()
    if not source.is_file():
        p.error(
            'Snapshot not found: '
            + str(source)
            + '. handover/ moved to the GitHub release archive/handover-2026-11-21; see docs/archive/HANDOVER.md.'
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        destination.touch(exist_ok=False)
    except FileExistsError:
        p.error('Destination already exists; refusing to overwrite: ' + str(destination))
    try:
        with (
            closing(sqlite3.connect(source.as_uri() + '?mode=ro', uri=True)) as src,
            closing(sqlite3.connect(destination)) as dst,
        ):
            src.backup(dst)
            if (
                dst.execute('PRAGMA integrity_check').fetchone()[0] != 'ok'
                or dst.execute('PRAGMA foreign_key_check').fetchall()
            ):
                raise ValueError('Restored snapshot failed integrity checks')
            count = dst.execute('SELECT COUNT(*) FROM ventures').fetchone()[0]
    except BaseException:
        destination.unlink(missing_ok=True)
        raise
    print(
        json.dumps(
            {'database': str(destination), 'ventures': count, 'archived_snapshot_unchanged': True, 'overwritten': False}
        )
    )


if __name__ == '__main__':
    main()
