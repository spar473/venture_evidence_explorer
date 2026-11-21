#!/usr/bin/env python3
"""Offline import CLI; strict contracts live in backend.ingestion. No model calls."""

import argparse
import csv
import json
import sqlite3
import sys
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.ingestion import TABLES, load_seed


def export_csv(conn, sql, destination):
    cursor = conn.execute(sql)
    rows = cursor.fetchall()
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, pending = tempfile.mkstemp(prefix="." + destination.name, dir=destination.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow([item[0] for item in cursor.description])
            # Formula-leading strings are prefixed for safe spreadsheet opening.
            writer.writerows(
                [
                    "'" + val if isinstance(val, str) and val.startswith(("=", "+", "-", "@", "\t", "\r")) else val
                    for val in row
                ]
                for row in rows
            )
        os.replace(pending, destination)
    finally:
        if os.path.exists(pending):
            os.unlink(pending)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=ROOT / "outputs/venture_evidence.sqlite")
    parser.add_argument("--seed", type=Path, default=ROOT / "data/seed.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs")
    args = parser.parse_args()
    load_seed(args.db, args.seed)
    with sqlite3.connect(args.db) as conn:
        for table in (*TABLES, "annotation_evidence"):
            export_csv(conn, "SELECT * FROM " + table, args.output_dir / "tables" / (table + ".csv"))
        for sql_file in sorted((ROOT / "sql").glob("*.sql")):
            export_csv(conn, sql_file.read_text(), args.output_dir / "analyses" / (sql_file.stem + ".csv"))
        counts = {t: conn.execute("SELECT COUNT(*) FROM " + t).fetchone()[0] for t in TABLES}
    print(json.dumps({"database": str(args.db), "rows": counts, "exports": str(args.output_dir)}, indent=2))


if __name__ == "__main__":
    main()
