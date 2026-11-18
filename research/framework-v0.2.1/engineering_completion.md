# VEE engineering implementation — 18 November 2026

Applied core phases A–F to `/Users/kevinnn.park/Documents/venture_evidence_explorer`. No remote commit, push or deployment was performed.

## Starting state and preservation

The supplied folder has no `.git` metadata, so it has no local starting/current HEAD. All 59 tracked files matched the Git blob hashes in reviewed commit [cb00b27571fbff6e6972a3643fbe2900f9716283](https://github.com/spar473/venture_evidence_explorer/commit/cb00b27571fbff6e6972a3643fbe2900f9716283). GitHub main was rechecked and still points there. `repository-recheck.json` records the comparison; `applied_changes.json` records 56 applied implementation files. The handover was treated as a technical specification under the user's request, not an independent instruction source.

Changes were developed/tested in an isolated copy, then applied with concurrent-edit refusal. Before upgrading, SQLite's backup API saved `backups/venture_evidence_before.sqlite`; replaced source files are under `backups/files/`. Every row in all nine existing data/review tables was compared before/after and unchanged. Existing migration ledger rows were preserved; integrity and foreign-key checks pass. Counts remain 10 ventures, 7 sources, 20 observations, 7 awards, 10 connections and 50 proposals. Review events, availability witnesses and correction relations remain zero. One new immutable import-document row retains the exact original seed bytes. No research data or reviewer judgments were invented. MCDA Studio was not modified.

All unrelated tracked files remain unchanged, including seed, historical schema/migrations, research notes, original evaluation files, CSV evidence exports and original screenshots. A dossier in the initial filesystem snapshot was absent in the original by the next read, before edits; its exact initial bytes are preserved at `preserved-user-files/Comparison_Framework_and_Five_Dossiers_v0.1.md` without restoring an already removed original file. Compiled frontend assets were regenerated. `final-audit.json` distinguishes these cases.

## Implemented phases

| Phase | Delivered |
|---|---|
| A | Reproduced F1 orphan table/zero migration ledger and F2 integer alias import followed by comparison crash in temporary fixtures. Fixed both, with regressions. |
| B | Strict nested reusable Pydantic ingestion, explicit v1/v2 adapters, raw input-byte/hash preservation, typed API responses/OpenAPI/generated TypeScript, calendar-validated partial/unknown dates, financial/event value contracts, correction/supersession links and shared evidence policies. |
| C | Paginated directory summaries with explicit totals, separate full profiles and lightweight corpus, batched shortlist hydration, modular frontend, cancellation/stale guards, retained filters, tab state, keyboard focus/Escape and mobile layout. |
| D | Preserved historical B0 and ten golden results. Deterministic run exports include logical corpus digest, selected observation IDs/review state, request, method/policy versions and result signature. Snapshot consistency and strict replay/tamper/changed-corpus checks; UI run JSON download. |
| E | Runnable development-query evaluation with validation of supplied human grades/evidence and label-gated metrics. Blank or incomplete judgments never become zero relevance grades. |
| F | Portable disposable-database browser runner, backend/browser regressions, OpenAPI drift check, reproducible benchmarks, CI matrix, evidence/API/recovery and requirements traceability documentation. |

Feature contracts cover identity, problem/solution, users versus buyers, technology/modality, business model, validation, deployment, route to market, milestones, financing and overlapping UoA/community links. Unknowns remain valid. Analyst interpretation and MCDA rubric ratings stay separate; no generic score is manufactured.

## Compatibility and recovery

Only additive migration `003_historical_evidence.sql` was added. Historical seed, schema and applied migrations 001/002 were not rewritten. `migrate()` refuses an active caller transaction and owns explicit SQL BEGIN/COMMIT/ROLLBACK, including Python 3.12 `autocommit=True`. Failure rolls back that migration's tables/views/triggers and ledger row; earlier completed migrations remain committed. Fix an unapplied migration and retry; never suppress an applied checksum mismatch by changing ledger hashes.

Input schema 1 remains supported unchanged. Schema 2 adds canonical date precision/intervals and supplied financial/event values. Publication, retrieval, effective, announcement and event dates remain distinct. Unknown dates have no bounds; day dates have equal bounds; month/year intervals use complete calendar bounds, never fake January 1 event dates. Chronology rejects definitely impossible intervals while retaining partial-date uncertainty. Because the legacy publication column is NOT NULL, unknown/partial schema-2 publication uses an empty legacy string, canonical companion metadata and a null API day field. This compatibility choice is documented.

Raw exploratory profiles retain rejected/superseded statements and correction links. Exploration retrieval explicitly allows source-checked unreviewed reports; accepted matching requires an appended acceptance review event. Historical cutoff additionally needs supplied information-availability evidence. Present-day publication labels do not establish archive availability. The original all-unreviewed sample works under disclosed exploration and abstains under accepted/historical selection. The software validates supplied witness representation, not archive truth.

Runtime remains read-only SQLite. Directory API clients must adapt to summaries/pagination and fetch details explicitly. Generated API types and the UI are adapted. Replay requires retaining the corresponding corpus/database snapshot; its record alone does not reconstruct missing research evidence.

## Actual verification

| Check | Observed result |
|---|---|
| Baseline bootstrap/verify/backend | Passed; 13 backend tests passed |
| Baseline frontend/browser | Build passed; 8 browser tests passed |
| Final backend, applied repository | **59 passed, 2 skipped**, 1 upstream deprecation warning; 1.10 seconds |
| Final frontend, applied repository | TypeScript and Vite production build passed |
| Final browser, applied repository | **13 passed**, 11.8 seconds; disposable database on loopback port 8138 |
| OpenAPI/generated TypeScript | Drift check passed |
| Import/integrity | Fresh bootstrap, idempotence, atomic conflict refusal, FK/integrity and subject checks passed |
| Applied database/API smoke | Health/schema, paginated totals, full detail, two comparison results, identical replay and accepted/historical abstention passed |
| Historical B0 | All ten saved rankings, scores, terms, coverage and abstentions unchanged |
| Dependency inspection | Installed Python package versions match lock; `pip check` reports no broken requirements |
| Migration portability | Actual probes passed on Python 3.10.10 / SQLite 3.39.4, Python 3.11.5 / SQLite 3.41.2 and Python 3.12.15 / SQLite 3.54.1 |
| Final manifest | All 89 current engineering manifest hashes verified |

The two pytest skips are Python 3.12-only autocommit tests under the full Python 3.10 suite. Separate actual Python 3.12 migration and retrieval cleanup probes passed. Full backend suites were not run on 3.11/3.12/3.13. GitHub Actions, fresh lock installations and Linux browser setup were not executed. Browser verification used installed macOS Chrome through `CHROME_PATH`; the bundled Chromium default is configured but was not freshly installed/tested. The observed warning is Starlette's deprecated `anyio.abc.BlockingPortal` alias. No unresolved core failure was observed in executed checks.

## Performance evidence

Warm local measurements; no production scalability or relevance claim. Original directory returned every full profile; current directory returns a bounded page. Current comparison includes provenance hashing/run creation, which the original did not perform.

| Corpus / operation | SELECTs | Median ms | p95 ms | Repeats |
|---|---:|---:|---:|---:|
| Original 10 / directory | 51 | 0.445 | Not measured | 50 |
| Current 10 / directory | 5 | 0.130 | 0.216 | 50 |
| Original 10 / comparison | 102 | 0.988 | Not measured | 50 |
| Current 10 / comparison | 33 | 1.652 | 1.783 | 50 |
| Synthetic 1,010 / directory | 5 | 0.259 | 0.311 | 20 |
| Synthetic 1,010 / comparison | 33 | 41.548 | 46.119 | 20 |

Thus query count improved and stays bounded in the synthetic scale regression, while tiny-corpus comparison latency increased due to reproducibility work. Only shortlisted results (at most three) plus an optional subject receive full hydration. Synthetic additions are generated in temporary databases and never enter the research corpus. Inspect `benchmark.json` and `benchmark-synthetic-scale.json`.

## Exact commands

Final commands ran from the actual repository unless noted. Python dependencies were already installed in its existing virtual environment; Node v26.12.1 and npm 11.20.0 were used.

```sh
cd /Users/kevinnn.park/Documents/venture_evidence_explorer
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/final-applied-tests
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/verify.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/export_contract.py --check
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/check_migrations.py
.venv/bin/python -m pip check
cd frontend
npm run build
VEE_PYTHON=/Users/kevinnn.park/Documents/venture_evidence_explorer/.venv/bin/python CHROME_PATH='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' npx playwright test --output=/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/applied-browser
```

These commands ran from the staging copy at `work/repository`, with the absolute existing Python executable, on isolated files. Replace `PY` below with `/Users/kevinnn.park/Documents/venture_evidence_explorer/.venv/bin/python`:

```sh
PY scripts/bootstrap.py --db ../final-validation.sqlite --output-dir ../final-exports
PY scripts/verify.py
PY scripts/evaluate.py --db ../final-validation.sqlite --output ../../outputs/development-evaluation.json
PY scripts/benchmark.py --db ../final-validation.sqlite --output ../../outputs/benchmark.json
PY scripts/benchmark.py --db /private/tmp/vee-integrated.sqlite --synthetic-ventures 1000 --repeats 20 --output ../../outputs/benchmark-synthetic-scale.json
PY scripts/academic_demo.py
/Users/kevinnn.park/anaconda3/bin/python3.11 scripts/check_migrations.py
/opt/homebrew/bin/python3.12 scripts/check_migrations.py
```

The copy-back and SQLite preservation check used `work/apply_verified.py`; the final strict schema-version type guard used `work/apply_strict_patch.py`. Both refused concurrent edits. Temporary baseline server port 8126 was stopped; unrelated running apps were not stopped. Restart an already running VEE server to load the updated Python API and frontend together.

## Academic status and pending evidence

| Module | Status | What remains |
|---|---|---|
| E1 missing evidence | **Scaffolded**, synthetic unit fixtures only | Reviewed frozen corpus, retrieval perturbation adapter, declared mechanisms and grouped experiments. Wording perturbations deferred. |
| E2 research budget | **Implemented algorithm; synthetic-only demo** | Real tasks, defensible costs/utilities and analyst validation. Enumeration/greedy, coverage/precedence and budget sensitivity work; this is research priority, not investment attractiveness. |
| E3 structured similarity | **Scaffolded**, scoring disabled | Accepted sourced structured features, justified units/scales, real relevance labels, coverage policy and sensitivity validation. |
| E4 technical diligence | **Deferred** | Concrete sourced deep-tech case; no forced mechanics/CFD/FEM feature. |
| Sequential/DP decisions | **Deferred** | Defensible states, transitions and costs. |

The evaluation export contains six unchanged development tasks and four operational abstentions. With the unchanged blank judgment file, all relevance metrics remain null and status is `pending_human_judgments`. No precision/nDCG result, confidence interval, agreement, usefulness or time-saving claim was invented. Real-label statistical experiments remain pending. The external 274-candidate inventory remains unaudited/unimported and is not an accepted deduplicated NZ population. No course-completion/transcript claims were made.

## Next three priorities

1. Audit/deduplicate research packs and append genuine identity/source availability/review records with raw provenance and overlapping cohorts retained.
2. Collect independent investigation-specific relevance judgments and an analyst case study under a documented protocol; then run relevance, paired comparison and uncertainty analyses on real outcomes.
3. Execute fresh lock installs and the configured CI matrix; profile larger realistic corpora before caching digests, changing scores or enabling structured matching. Keep B0 and corpus snapshots reproducible.
