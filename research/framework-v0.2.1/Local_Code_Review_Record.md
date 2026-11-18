# Local code verification — 18 November 2026

This is a direct rerun against an isolated copy of the local application's source, using its already installed dependencies. It is not a fresh installation, a GitHub/CI run, a full independent architectural audit or research-import verification. The original application/database were not modified. No local `.git` metadata was found; `Application_Source_Manifest.json` identifies the 87 copied source/configuration files.

The separate `engineering_completion.md` is an unchanged copy of the report found in the engineering chat's outputs. Its baseline, migration, benchmark, preservation and platform statements are **reported there**. The following table identifies the checks actually rerun for this review.

| Executed check | Observed result |
|---|---|
| `scripts/bootstrap.py` | Pass on disposable copy: 10 ventures, 7 sources, 20 observations, 7 awards, 10 connections, 50 annotations. |
| `scripts/verify.py` | Pass: referential integrity, unknown handling, repeat import, atomic conflict refusal and evidence-subject checks. |
| `python -m pytest -q -p no:cacheprovider` | **59 passed, 2 skipped**, 1 upstream Starlette/AnyIO deprecation warning; 1.08 s. Python 3.10 suite; skips require 3.12 autocommit. |
| `scripts/check_migrations.py`, Python 3.10.10 / SQLite 3.39.4 | Pass: two transaction modes, rollback of injected table/view/trigger/ledger failure, retry and active caller-transaction refusal. |
| Same migration script, Python 3.12.15 / SQLite 3.54.1 | Pass: three modes including `autocommit=True`. This is targeted portability verification, not a full 3.12 backend suite. |
| `scripts/export_contract.py --check` | Pass: OpenAPI and generated TypeScript match. |
| `npm run build` | Pass: TypeScript and Vite production build, 26 modules. |
| Playwright, macOS installed Chrome, isolated disposable server/DB on 127.0.0.1:8147 | **13 passed**, 12.1 s. Directory/filter/evidence/unknowns, comparison and abstention, source links, CSV, loading/error, stale requests, tabs, replay, historical presentation, keyboard and narrow layout. |
| App `validate` only, research 0.2.1 packet | Rejected as expected with 792 schema errors; this is shape incompatibility, not failed research evidence checks. SQLite access was fail-fast prohibited during this probe. |

Backend tests include full-row equality on repeat import and rollback after a preceding new source, immutable evidence/review behaviour, input type/calendar validation, date intervals, filtering, B0 golden outcomes and run provenance/replay. These substantiate the tested cases; they do not prove arbitrary future adapter transactions correct.

## Commands and environment

Commands ran from `work/research/framework_v021/app_snapshot` under this research chat; frontend commands used its `frontend` subdirectory. This directory is disposable, not the user's app checkout. `PY` below denotes the existing `/Users/kevinnn.park/Documents/venture_evidence_explorer/.venv/bin/python`. Python commands used `PYTHONDONTWRITEBYTECODE=1`.

```sh
PY scripts/bootstrap.py
PY scripts/verify.py
PY -m pytest -q -p no:cacheprovider
PY scripts/check_migrations.py
/opt/homebrew/bin/python3.12 scripts/check_migrations.py
PY scripts/export_contract.py --check
npm run build
VEE_PYTHON=... VEE_TEST_PORT=8147 CHROME_PATH='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' ./node_modules/.bin/playwright test --output=../outputs/browser-tests
```

Node was 26.12.1. Python dependencies came from the app's existing virtual environment. Frontend dependencies were copied from installed `node_modules`; npm executable links were retained locally. The first symlink-based build attempt could not create Vite's cache outside the workspace. Copying dependencies initially dereferenced executable links; restoring those local relative links resolved the second harness failure. Neither was an application-code defect. The normal sandbox refused loopback binding; the approved local browser run then passed. Non-failing Node deprecation/color-environment warnings remain.

## Still unverified / pending

Fresh locked dependency installation; the configured Linux CI matrix and bundled Chromium installation; full backend suites across all Python versions; new research adapter; genuine identity/review decisions; independently judged relevance/usefulness; realistic end-to-end performance. Benchmark numbers in the engineering report were not rerun here. Fewer SELECTs alone do not establish lower latency.

Browser tests use seeded evidence and synthetic historical fixtures. They do not freshly verify publisher text, source availability, legal identity, historic web availability or real venture outcomes. Existing blank relevance judgments remain blank.

The review ZIP includes copied source, this research package and the attributed engineering report. It excludes virtual environments, node_modules, compiled assets, live SQLite files, backup databases, caches and Git metadata. The snapshot manifest covers source/configuration only, not those exclusions. Preservation and artifact hashes are in `Validation_Record.json`.
