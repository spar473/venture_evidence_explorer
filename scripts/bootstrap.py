#!/usr/bin/env python3
"""Offline seed import. Standard library only; no collection or model calls."""
import argparse
import csv
import hashlib
import json
import sqlite3
import sys
import os
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.database import migrate

TABLES = ("sources", "ventures", "observations", "awards", "connections", "annotations")
KEYS = dict(zip(TABLES, ("source_id", "venture_id", "observation_id", "award_id", "connection_id", "annotation_id")))

def require(condition, message):
    if not condition:
        raise ValueError(message)

def validate(data):
    require(data["metadata"]["schema_version"] == 1, "Unsupported schema version")
    indexes = {}
    for table in TABLES:
        ids = [row[KEYS[table]] for row in data[table]]
        require(len(ids) == len(set(ids)), "Duplicate IDs in " + table)
        indexes[table] = {row[KEYS[table]]: row for row in data[table]}
    for venture in data["ventures"]:
        require(bool(venture["display_name"].strip()), "Missing venture name")
        require(isinstance(venture["aliases"], list), "Aliases must be a list")
    for source in data["sources"]:
        require(source["url"].startswith("https://"), "Source needs HTTPS URL")
        pub, ret = date.fromisoformat(source["published_at"]), date.fromisoformat(source["retrieved_at"])
        require(pub <= ret, "Publication after retrieval")
    for table in ("observations", "awards", "connections", "annotations"):
        for row in data[table]:
            require(row["venture_id"] in indexes["ventures"], "Unknown venture in " + table)
    for row in data["observations"] + data["awards"]:
        require(row["source_id"] in indexes["sources"], "Unknown source")
        require(bool(row["locator"].strip()), "Missing passage locator")
        require(bool(row["review_status"].strip()), "Missing review status")
    for row in data["observations"]:
        require(bool(row["value_text"].strip()), "Empty observation")
        require(row["assertion_type"] == "publisher_report", "Unsupported seed assertion type")
        if row["effective_at"]:
            date.fromisoformat(row["effective_at"])
    for row in data["awards"]:
        require(row["programme"] in ("velocity_100k", "velocity_ideas"), "Unknown programme")
        require(type(row["award_year"]) is int, "Award year must be integer")
        require(row["award_year"] <= date.fromisoformat(indexes["sources"][row["source_id"]]["published_at"]).year, "Award year after report")
        if row["event_date"]:
            event = date.fromisoformat(row["event_date"])
            require(event.year == row["award_year"], "Event year mismatch")
            source = indexes["sources"][row["source_id"]]
            require(event <= date.fromisoformat(source["published_at"]), "Award event after report")
        require(row["place"] is None or (type(row["place"]) is int and row["place"] > 0), "Invalid place")
    for row in data["connections"]:
        obs = indexes["observations"].get(row["observation_id"])
        require(obs is not None and obs["venture_id"] == row["venture_id"], "Connection evidence subject mismatch")
        require(obs["field"] == "uoa_connection", "Connection needs relationship evidence")
    for row in data["annotations"]:
        require(row["origin"] == "analyst_proposed" and row["review_status"] == "proposed", "Seed annotations must remain proposed")
        require(bool(row["basis_observation_ids"]), "Annotation needs evidence basis")
        for oid in row["basis_observation_ids"]:
            obs = indexes["observations"].get(oid)
            require(obs is not None and obs["venture_id"] == row["venture_id"], "Annotation evidence subject mismatch")
    return indexes

def db_record(row):
    result = {}
    for key, value in row.items():
        if isinstance(value, list):
            result[key + "_json"] = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        else:
            result[key] = value
    return result

def insert_immutable(conn, table, record, key):
    # Table/key names are fixed by this module, never user-provided.
    allowed = {row[1] for row in conn.execute("PRAGMA table_info(" + table + ")")}
    require(set(record) == allowed, "Unexpected or missing columns in " + table)
    columns = sorted(allowed)
    existing = conn.execute(
        "SELECT " + ",".join(columns) + " FROM " + table + " WHERE " + key + "=?", (record[key],)
    ).fetchone()
    values = tuple(record[c] for c in columns)
    if existing is not None:
        require(tuple(existing) == values, "Conflicting immutable record: " + table + "/" + str(record[key]))
        return
    conn.execute("INSERT INTO " + table + " (" + ",".join(columns) + ") VALUES (" + ",".join("?" for _ in columns) + ")", values)

def load_seed(db_path, seed_path=None):
    seed_path = Path(seed_path or ROOT / "data/seed.json")
    raw = seed_path.read_bytes()
    data = json.loads(raw)
    validate(data)
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        conn.executescript((ROOT / "schema/schema.sql").read_text())
        migrate(conn)
        with conn:
            for table in TABLES:
                for row in data[table]:
                    insert_immutable(conn, table, db_record(row), KEYS[table])
            for row in data["annotations"]:
                for oid in row["basis_observation_ids"]:
                    conn.execute("INSERT OR IGNORE INTO annotation_evidence VALUES (?,?)", (row["annotation_id"], oid))
            conn.execute("INSERT OR IGNORE INTO imports VALUES (?,?,?)",
                         (hashlib.sha256(raw).hexdigest(), 1, data["metadata"]["prepared_at"]))
            require(not conn.execute("PRAGMA foreign_key_check").fetchall(), "Foreign-key check failed")
    finally:
        conn.close()
    return data

def export_csv(conn, sql, destination):
    cursor = conn.execute(sql)
    rows = cursor.fetchall()
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, pending = tempfile.mkstemp(prefix="."+destination.name, dir=destination.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow([item[0] for item in cursor.description])
            # Formula-leading strings are prefixed for safe spreadsheet opening.
            writer.writerows([
                "'" + val if isinstance(val, str) and val.startswith(("=", "+", "-", "@", "\t", "\r")) else val
                for val in row
            ] for row in rows)
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
    print(json.dumps({"database":str(args.db), "rows":counts, "exports":str(args.output_dir)}, indent=2))

if __name__ == "__main__":
    main()

