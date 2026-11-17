#!/usr/bin/env python3
"""Verify integrity, repeat import and atomic conflict refusal on temporary data."""
import copy
import json
import sqlite3
import tempfile
from pathlib import Path
from bootstrap import ROOT, TABLES, load_seed

def counts(db):
    with sqlite3.connect(db) as conn:
        return {t:conn.execute("SELECT COUNT(*) FROM " + t).fetchone()[0] for t in (*TABLES, "imports")}

def main():
    with tempfile.TemporaryDirectory() as temp:
        db = Path(temp) / "verify.sqlite"
        original = load_seed(db)
        first = counts(db)
        assert first["ventures"] == 10 and first["awards"] == 7 and first["sources"] == 7
        load_seed(db)
        assert counts(db) == first, "Repeat import created duplicates"
        with sqlite3.connect(db) as conn:
            assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            assert not conn.execute("PRAGMA foreign_key_check").fetchall()
            assert conn.execute("SELECT COUNT(*) FROM ventures WHERE current_funding_stage IS NOT NULL OR current_operating_status IS NOT NULL").fetchone()[0] == 0
            # Link tables must support multiple relationships without implying exclusive cohorts.
            assert conn.execute("SELECT COUNT(*) FROM connections").fetchone()[0] == 10

        conflict = copy.deepcopy(original)
        conflict["sources"].append(dict(conflict["sources"][0], source_id="src_new_before_conflict"))
        conflict["ventures"][0]["display_name"] = "Conflicting replacement"
        conflict_path = Path(temp) / "conflict.json"
        conflict_path.write_text(json.dumps(conflict))
        try:
            load_seed(db, conflict_path)
        except ValueError as error:
            assert "Conflicting immutable record" in str(error)
        else:
            raise AssertionError("Conflicting record was accepted")
        assert counts(db) == first, "Rejected import left partial writes"

        invalid = copy.deepcopy(original)
        invalid["connections"][0]["observation_id"] = "v_rosterlab_connection"
        invalid_path = Path(temp) / "invalid.json"
        invalid_path.write_text(json.dumps(invalid))
        try:
            load_seed(db, invalid_path)
        except ValueError as error:
            assert "subject mismatch" in str(error)
        else:
            raise AssertionError("Wrong-subject evidence was accepted")
        assert counts(db) == first
    print("PASS: referential integrity, unknown handling, idempotent imports, atomic conflict refusal and evidence-subject checks")

if __name__ == "__main__":
    main()

