# Requirements, verification and usefulness validation

| Requirement | Implementation | Executable verification |
|---|---|---|
| F1 migration ownership | Explicit SQLite BEGIN/COMMIT/ROLLBACK and active-caller refusal | `tests/test_ingestion.py`, `scripts/check_migrations.py` inject failed table/view/trigger migrations and retry; checksummed applied files remain immutable |
| F2 strict nested import | `backend/ingestion.py`; schema 1 adapter and schema 2 historical extensions | Nested alias/ID/type/extra-field failures, validation locations, atomic conflicts and no writes on malformed input |
| Historical assertions | Additive migration 003; canonical date intervals, source availability and correction links | Unknown dates, leap months, partial years, chronology, supersession cycles, subject links, retained raw bytes, immutable metadata |
| Separate evidence policies | Raw profile hydration versus shared exploration/accepted/cutoff selection | Original unreviewed seed works under exploration; acceptance requires real supplied review events; cutoff without availability abstains |
| Efficient directory and comparison | Bounded summaries, lightweight corpus and shortlist-only detail batches | Five directory SELECTs, comparison query count independent of 10/1,010 identity count, pagination and same-award-row/overlap tests |
| Typed public contract | Pydantic responses, OpenAPI and generated TypeScript | `scripts/export_contract.py --check`; frontend TypeScript build; typed partial date/financial/event display |
| Preserve B0 | Historical scoring/morphology/mode boundaries and stable IDs | Ten saved pre-change golden rankings, scores, terms, coverage and abstentions |
| Reproducible runs | Read snapshot, logical corpus digest, selected evidence/reviews, request/result signature, export/replay | Identical run outputs; tamper and changed-corpus refusal; API replay and browser JSON download |
| Modular accessible UI | Directory, profile, drawer, comparison, analytics, shared transport/hooks | Browser flows, keyboard focus/Escape, pagination/lazy load, cancellation, stale-response guard, narrow layout and tab state |
| Label-gated evaluation | Development-query exports, explicit grade validation and unknown-label handling | Blank judgments yield null relevance metrics; incomplete corpus suppresses nDCG; invalid/duplicate labels refused |
| Optional E2 optimiser | Declared synthetic budget/utility fixture, enumeration/greedy | Independent subset verification, feasibility/precedence/coverage constraints and budget sensitivity |

These checks establish software behavior. Analyst relevance, usefulness, time savings, agreement and external validity require actual independent review on an adequately sourced corpus. The existing sample is selected historical reporting; no population acceptance, causal programme claim or investment prediction follows from passing tests.
