# Venture Evidence Explorer — Prompt 1 completion

18 November 2026, Pacific/Auckland. **Two-dossier integration pilot implemented and locally verified.** Research interchange 0.2.1 remains distinct from application input versions 1 and 2. Prompts 2–5 remain subsequent milestones; saved intake, discovery staging, empirical relevance evaluation and clean-install release verification are not claimed here.

## Revision and preservation

Current application: `/Users/kevinnn.park/Documents/venture_evidence_explorer`. No local Git metadata/HEAD exists. Before edits, all **87 files** from the handover kit's frozen application snapshot matched the current source. The frozen copy was never extracted over the application. Current source/user changes were snapshotted and guarded by SHA-256 checks before copy-back. Applied migrations 001–003, the seed, existing evidence/reviews and prior research/reference documents were preserved. No push, remote CI trigger or deployment was performed.

Applied migration 004 and the supplied research graph to the local database after a SQLite backup. Every row in **14 existing data/review/metadata tables** is unchanged; original migration ledger entries are preserved. A second real import produced full-row equality across every table. FK/integrity and baseline ranking/eligibility preservation passed.

Backups and full preservation details are in `outputs/pilot/preservation-and-apply.json` and `outputs/pilot/backups/` under this Codex chat workspace. The prior core completion report is preserved as `outputs/pilot/previous_core_engineering_completion.md`. The current root report supersedes its implementation status; the unchanged reports inside `research/framework-v0.2.1/` remain attributed historical references. `PILOT_SHA256SUMS.txt` describes the new source; earlier manifests remain historical.

## Delivered functionality

| Requirement | Implemented behavior |
|---|---|
| Distinct adapter | `backend/research_adapter.py` and `scripts/import_research.py` validate the supplied JSON Schema and semantic graph before writes, with explicit external validation date. No app-v1/v2 reinterpretation. |
| Mapping/loss report | Every collection and **2,430 leaf paths** accounted: **605 mapped**, **1,767 preserved research-only**, **58 quarantined**, **0 unsupported** in the supplied packet. Nulls/empty arrays remain explicit. Unknown schema fields/types are refused with paths; no unsupported meaning is silently discarded. |
| Transactional storage | Additive migration 004 stores immutable raw packet/hash, semantic digest, 92 top-level records, 17 nested requirements/conclusions, typed links, canonical date intervals, import membership and mapping audit. Entire research graph plus ledger is one explicit transaction. |
| Identity | Auditable proposed/resolved/rejected brand/project mapping states, separate from legal identity and factual review. Actual supplied sidecars require actor, date, rationale, subject-correct evidence, scope and predecessor. **Both real pilot mappings remain proposed**, with no human decision actor/date. |
| Dossiers | Working RosterLab and QuickMas views under research subject IDs: atomic attribution/speaker roles, sources/access/version/date precision, target/event/report distinctions, scoped supported and withheld conclusions, unknowns, open cases and access gaps. Keyboard/Escape/focus, filters and narrow layout verified. |
| Analytical exports | Sixteen CSV grains plus original raw packet JSON and an export manifest. Stable IDs, namespace, packet/source lineage, precision/basis/missing reasons, review/actor disposition and raw `record_json` retained. Download in UI/API or use `scripts/export_research.py`. |
| Verification | Backend, schema/type drift, build, browser, integrity, transaction rollback/retry, full-row repeat equality, raw-byte preservation and baseline isolation checks executed. |

Strict JSON decoding also refuses duplicate keys and non-finite values (including exponent overflow). The JSON Schema URI checker is explicitly installed/pinned and its presence checked, rather than silently skipping source URI validation. Successful imports report their originally validated bytes and actual target connection, even if the input file changes during processing.

## Honest research boundaries

The stored packet contains 2 research subjects, 4 parties, 6 source references, 34 observations, 6 event candidates, 6 reports, 21 explicit unknowns, 2 proposed annotations, 6 question assessments, 3 open cases, 2 access gaps and **zero human review events/accepted records**. These counts describe editorial records, not a verified venture population or completed milestones.

RosterLab's two financing candidates remain possibly duplicate, linked to the open case; no distinct-round count or funding total is produced. Investor cheque, round total and advertised price remain different monetary scopes. Currency remains null with a reason. Adoption does not establish payer, procurement authority, contracting party or completed IT integration. QuickMas's 2025 launch target retains year precision and unknown occurrence; passing the target year establishes neither launch nor failure/cancellation.

Supported conclusions remain source-checked, attributed and scoped; stronger requested conclusions remain withheld. Source reading/access statements are inherited from the supplied research packet and were not freshly fact-checked on publisher websites. Browser source-link checks verify preserved hrefs, not publisher truth or live availability. Research-as-of is not historical web availability; no archive witnesses were fabricated.

Pending identity does not block import or dossier operation. A nonexistent proposed app target is preserved/quarantined without inventing an app venture. A genuine brand/project resolution would still leave legal identity, imported proposals/cases and assertion review separate. Synthetic decision actors and deliberately malformed facts exist only in disposable tests. The importer checks represented audit lineage; it cannot authenticate a human decision.

Research remains separate from the legacy ten-venture/twenty-observation corpus. No imported research row becomes a B0 description, award, UoA connection or accepted structured feature. Historical B0 golden scores/order and selected observation eligibility are unchanged. The existing run digest hashes **all user tables**, so migration/import conservatively invalidates old run digests despite unchanged ranking; retain the pre-import database/code snapshot for old replay. No digest/scoring behavior was silently changed.

## Transactions and compatibility

Application schema preparation/migrations precede the research transaction. Research graph, source bytes, all extensions/links/time values, mapping records and ledger then commit together or roll back together. Active caller transactions are refused. Explicit SQL COMMIT/ROLLBACK avoids Python autocommit assumptions. Exact repeat imports produce full-row equality. Formatting-only changes retain another raw document/membership without duplicating evidence; changed semantic content under an immutable editorial ID is refused. Source versions need new IDs/history.

New date projections reuse `HistoricalDate` validation; the separate namespaced table is required by the legacy date-owner constraints. Raw year/month/day/unknown precision remains alongside calendar bounds, which are never presented as actual occurrence days. The whole raw packet can be downloaded byte-for-byte. A dossier's scoped reference-closure graph is explicitly **not** a standalone import packet; shared question evidence can include the counterpart subject.

Dependencies added/pinned: jsonschema 4.26.0, attrs 26.1.0, jsonschema-specifications 2025.9.1, referencing 0.37.0, rpds-py 0.30.0, rfc3986-validator 0.1.1. Existing dependencies were not blanket upgraded. Verification reused installed dependencies copied into a disposable environment, and the required validation libraries were sourced from exact locally installed distributions. **This is not a fresh-install or cross-platform reproducibility claim.**

## Executed verification

- Baseline source match: 87/87; baseline bootstrap/integrity passed; **59 backend tests passed, 2 skipped**; baseline build and **13 browser tests passed**.
- Supplied research validator: schema/semantic pass; **32 rejection cases and 4 permitted counterexamples** passed. Vendored research reference bytes remain unchanged.
- Final backend in staging: **89 passed, 2 skipped**, one upstream Starlette/AnyIO deprecation warning, 6.18 seconds. The skips require Python 3.12's autocommit parameter under the Python 3.10 full suite.
- Final schema/OpenAPI/generated TypeScript drift check passed. Final TypeScript/Vite build passed (29 modules).
- Integrated browser: **17 passed**, 15.8 seconds, disposable imported database, installed macOS Chrome on loopback port 8158. Includes old workflows plus both dossiers, source/claim attribution, null currency, prospective target/unknown occurrence, duplicate financing, withheld conclusions, linked counterpart evidence, packet-byte SHA, CSVs, keyboard and mobile behavior.
- `scripts/verify_research.py` passed: no-write dry-run byte/row preservation, original table preservation, lossless graph roundtrip, repeated full-row equality, immutable-conflict rollback, caller transaction refusal, FK/integrity, B0 signature preservation and accepted-only isolation.
- Import regressions additionally exercise failure after source insertion and during event/time/link extension writes; ledger and all graph writes roll back. Migration 004 failure/retry leaves no orphan research schema or version row.
- Migration portability script passed on Python 3.10.10 / SQLite 3.39.4 and Python 3.12.15 / SQLite 3.54.1 (including autocommit=True). These are targeted probes, not a full 3.12 backend suite.
- Export CLI ran successfully: sixteen CSVs plus exact original packet and manifest. Dependency `pip check` passed.

Final checks **from the applied repository**: **89 backend tests passed, 2 skipped**, one upstream deprecation warning (4.70 seconds); build/type check passed; **17 browser tests passed** (13.2 seconds); OpenAPI/type drift, ordinary integrity verification, research verification and dependency check passed. Real-database API smoke verified both dossiers, every one of the sixteen subject-filtered CSVs, exact packet bytes, proposed/null identity decisions, the original ten-venture directory and B0/replay. Live HTTP smoke passed against the current frontend and both dossiers at **http://127.0.0.1:8170**. The demo is loopback-only and reads the preserved local database; existing app processes were not stopped.

Exact final in-place commands (repository root unless stated):

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/pilot/applied-tests
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/verify_research.py --output /Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/outputs/pilot/applied-disposable-verification.json
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/verify.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/export_contract.py --check
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pip check
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/export_research.py --db outputs/venture_evidence.sqlite --output-dir /Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/outputs/pilot/analytical-exports
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/import_research.py --db outputs/venture_evidence.sqlite --as-of 2026-11-18 --report /Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/outputs/pilot/mapping-loss-dry-run.json
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/serve.py --port 8170
# From frontend/:
npm run build
VEE_PYTHON=/Users/kevinnn.park/Documents/venture_evidence_explorer/.venv/bin/python VEE_TEST_PORT=8158 CHROME_PATH='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' npx playwright test --output=/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/pilot/applied-browser
```

Copy-back used `work/pilot/apply_pilot.py`; targeted local validation-library copying used `work/pilot/copy_validation_deps.py` into the app environment, with conflict refusal and no network or existing dependency replacement. These are local dependency reuse and focused additions, not Prompt 5's fresh install. Current stored graph is 109 editorial/derived records, 401 links and 138 time projections; one packet import and two proposed mappings, zero decision documents or acceptance events. All 14 prior data/review/metadata tables remain unchanged and the second real import is full-row identical.

Dossier screenshots and analytical files are saved under this chat's `outputs/pilot/`: `rosterlab-desktop.png`, `quickmas-desktop.png`, `quickmas-mobile.png`, `quickmas-launch-target.png`, `analytical-exports/manifest.json`, `mapping-loss-dry-run.json`, `actual-import-report.json`, `runtime-measurements.json` and preservation/backup records. All seventeen export payload hashes match their manifest.

Fresh locked installs, Linux bundled Chromium, remote CI, full Python-version matrix, real relevance judgments/usefulness and broad inventory import were **not executed**. The workflow was extended to run the pilot checks, without triggering it. One build command initially ran from the repository root without package.json; running it from `frontend/` passed. Early browser test wording mismatches were corrected; final runs above are actual passes. No unsupported empirical metrics are reported.

## Measurements

Measured on macOS 26.5.1 arm64, Python 3.10.10 / SQLite 3.39.4. Warm **in-process ASGI API** latency includes serialization and comparison digest, excludes browser/network transport. SELECT counts are separately measured service/repository statements. Thirty repeats per endpoint; see `outputs/pilot/runtime-measurements.json`.

| Operation | SELECTs | Median ms | p95 ms |
|---|---:|---:|---:|
| Legacy directory | 5 | 1.522 | 1.653 |
| B0 comparison including full-store digest | 40 | 9.576 | 10.490 |
| Research subject directory | 2 | 2.029 | 2.660 |
| RosterLab dossier | 4 | 5.730 | 6.380 |
| QuickMas dossier | 4 | 7.231 | 7.548 |

Legacy corpus remains 10 ventures/20 observations/7 sources; research contributes 92 editorial records and derived graph metadata. New tables increase conservative digest cost. These are implementation measurements, not evidence of analyst usefulness or a production scalability claim, and are not directly comparable with the prior report's repository-only timings.

## Commands

From the repository, with updated dependencies available:

```sh
.venv/bin/python scripts/import_research.py --db outputs/venture_evidence.sqlite --as-of 2026-11-18 --report outputs/research-dry-run.json
# Explicit import only after the SQLite backup:
.venv/bin/python scripts/import_research.py --db outputs/venture_evidence.sqlite --as-of 2026-11-18 --apply --report outputs/research-import.json
.venv/bin/python scripts/verify_research.py --as-of 2026-11-18
.venv/bin/python scripts/export_research.py --db outputs/venture_evidence.sqlite --output-dir outputs/research-exports
.venv/bin/python scripts/verify.py
.venv/bin/python scripts/check_migrations.py
.venv/bin/python scripts/export_contract.py --check
.venv/bin/python -m pytest -q -p no:cacheprovider
.venv/bin/python research/framework-v0.2.1/validate_research_example.py --as-of 2026-11-18
cd frontend
npm run build
VEE_PYTHON=/absolute/path/to/.venv/bin/python VEE_TEST_PORT=8158 CHROME_PATH='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' npx playwright test
```

Actual isolated verification used `/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/pilot/env/bin/python` from `work/pilot/repository`, `--db ../pilot-verification.sqlite`, reports under this chat's `outputs/pilot/`, and browser `--output=.../work/pilot/final-browser`. Exact rerunnable commands and artifacts are also in `docs/research_import.md` / `docs/research_api.md`. The final copy-back script records source hashes and database preservation before any real import.

To demonstrate: start/restart `.venv/bin/python scripts/serve.py` on an unused local port, choose **Research dossiers**, then open **RosterLab** and **QuickMas**. Inspect events, questions, unknowns, open cases and exports. No dossiers are automatically imported on startup. API exact packet download is `/api/research/packets/{sha256}.json`; CSVs are `/api/research/exports/{name}.csv`.

## Implemented versus pending

**Implemented and verified:** two-dossier graph import/dry run, safe repeat/rollback, raw provenance, proposed/resolved mapping facility, independent pending-subject views, supported/withheld readiness display, lossless analytical exports and relevant code/browser checks.

**Pending real decisions/evidence:** actual identity acceptance, financing event reconciliation, legal/payer/procurement/integration facts, source capture/availability, factual review authority and a versioned accepted-feature projection. No owner decision is needed to inspect the pilot, and none was manufactured.

**Subsequent prompts, not completed here:** Prompt 2 saved new-venture intake; Prompt 3 274-lead discovery staging (inventory remains untouched); Prompt 4 real-label evaluation/review workflow; Prompt 5 fresh-install/CI reproducibility. Existing academic E1/E3 remain scaffolded, E2 has an implemented synthetic-only demonstration, and E4/sequential work remains deferred. Blank human judgments stay blank.

Next priorities: obtain genuine brand/project/event decisions if desired; proceed to the separately scoped saved-intake milestone; run clean-install verification and collect real task labels before any usefulness/relevance claim.
