# Contributing to Venture Evidence Explorer

Start with the [local setup](README.md#run-locally) in the README. The demo launcher imports research packets and the reference pool into a disposable SQLite database. For a base-data workspace, run `.venv/bin/python scripts/bootstrap.py` followed by `.venv/bin/python scripts/serve.py`. See the [research import guide](docs/research_import.md) for loading the remaining packets.

## Report a bug or evidence correction

Use the [issue templates](https://github.com/spar473/venture_evidence_explorer/issues/new/choose). For an app issue, include the view URL or local command and the steps that reproduce it. For a correction, identify the company and record, explain the proposed change, and include a dated public source and locator if you have them. See the [data-use policy](DATA_USE.md#requesting-a-correction-or-removal) for requests to correct or remove a record.

## Check a change locally

Run the checks relevant to your change. For a pull request, describe the behaviour that changed and the checks you ran. Include screenshots for a visual change. GitHub Actions runs the backend matrix, browser tests and static build.

```sh
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python scripts/export_contract.py --check
.venv/bin/ruff check backend scripts tests
.venv/bin/ruff format --check backend scripts tests
.venv/bin/pyright --pythonpath .venv/bin/python

(cd frontend && npm run build && npm run format:check)
(cd frontend && npx playwright install chromium)
(cd frontend && VEE_PYTHON="$PWD/../.venv/bin/python" npx playwright test)
```

When the API contract changes, run `.venv/bin/python scripts/export_contract.py` to regenerate OpenAPI and the frontend types together. See the [API documentation](docs/research_api.md) and [architecture](docs/architecture.md).

## Build the GitHub Pages demo

Run from the repository root after installing the [local dependencies](README.md#run-locally).

```sh
.venv/bin/python scripts/export_static.py
(cd frontend && node --experimental-strip-types --test test/scorer-parity.mjs)
npm run build:static --prefix frontend
.venv/bin/python -m http.server 8000 --bind 127.0.0.1 --directory frontend/dist
```

Open [localhost:8000](http://127.0.0.1:8000). The export includes dated evidence, scenario presets, robustness results, and a SHA-256 manifest. Custom scenarios run in the browser. The [Pages workflow](.github/workflows/pages.yml) tests the static build and deploys from `main`.

## Reproduce the evidence checks

```sh
.venv/bin/python scripts/preview_backtest.py
.venv/bin/python scripts/synthetic_cohort.py --seed 7
```

The preview writes a run under `outputs/preview/` with its SHA-256 in the filename. The synthetic command writes the labelled Method lab files under `outputs/method-lab/`. Compare the results with the digests in the [analytics evaluation](docs/ANALYTICS_EVALUATION.md#reproduction).

To try a different field decision, edit a copy of [the review CSV](research/healthtech-pilot/backtest-review-decisions.csv) and record the date of the decision. Pass `--decisions /path/to/copy.csv` to `scripts/ingest_backtest_review.py`, `scripts/audit_backtest_coverage.py`, and `scripts/preview_backtest.py`. The local demo reloads changes to the checked-in CSV on the next request. Keep the preregistered scoring and evidence rules visible in any comparison. [Historical comparison protocol](docs/design/BACKTEST_PREREG.md)

## Legacy workspaces

The local server also serves the research workspace at `?mode=research` and the previous workbench at `?mode=workbench`. The older `?page=timemachine` and `?page=precedents` links open Company profile by default. To open the original Time Machine directly, use `?mode=workbench&page=timemachine`. Set `VITE_TIME_MACHINE_SUBJECT=public_partly` at build time to change the original Time Machine’s starting case. Build with `VITE_TIME_MACHINE_TRACK=strict` to inspect its strict mode. The strict endpoint currently withholds the run because the human review gate is unmet.
