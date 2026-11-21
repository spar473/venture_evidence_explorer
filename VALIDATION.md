# Validation

Current record, refreshed on 2026-11-21 after the pre-demo polish sprint. CI is the source of truth: every pull request and every push to `main` runs the workflow in `.github/workflows/checks.yml`. The original 17 November release record is kept in [docs/archive/VALIDATION-2026-11-17.md](docs/archive/VALIDATION-2026-11-17.md).

## 22 November 2026 · Pre-demo cleanup verification

Local macOS checks after the repository and language cleanup:

- Python 3.11: **211 passed, 2 skipped**; the OpenAPI and generated TypeScript check passed.
- Production TypeScript/Vite build, Ruff lint and formatting, Prettier and `git diff --check` passed.
- **49 Playwright tests passed**, using the project's `.venv` and the matching bundled Chromium build (`PLAYWRIGHT_BROWSERS_PATH=/private/tmp/vee-playwright-pinned.wdrZyd`). This includes sidebar overflow checks at desktop and 390 px width and the updated evidence labels. No system Chrome override was used.
- A credential-pattern scan found no matches in 266 tracked files and 953 historical blobs across locally available refs. This is a limited pattern scan, not a guarantee that every sensitive value is detectable.

The first browser attempts could not start because the default system Python lacked dependencies and Chromium's headless shell was missing from the default cache. The successful run used `VEE_PYTHON` and the matching preinstalled browser cache. README check commands now explicitly select the project's Python.

## Time Machine coverage checkpoint

The new packet and audit have 22 regression cases covering proposed versus confirmed data, fixed peer counts, duplicate fields, source/witness timing, partial entry dates, mutable-page old dates, review chronology, changed anchors and cohort input digests, unknown vocabulary, and lenient evidence excluded from strict coverage. The common subject cutoff applies to witness, publication, revision and effective dates; a backtest archive witness cannot predate publication. The full Python 3.11 suite passed with **233 passed, 2 skipped**; API contract, Ruff, frontend build and Prettier checks passed. The actual packet has no human-confirmed fields; a passing validator is not acceptance of the proposed facts.

The existing 49 Playwright tests passed. Twenty-four canonical b0:3 API responses (six subjects, two anchors and both witness modes at 2026-11-21) were byte-identical against `main` at `0b7e5d8`; combined SHA-256 `7c619d8a04d7859199b3661b9f2283e7e0481577a2d6511b25d0b437db20f4ca`. This checks the existing profile, not the unimplemented general profile.

The coverage command validates the graph and reports the shortfall with exit 0 for CI. `--require-gate` exits 1 while fewer than 15 eligible Partly peers have five confirmed strict fields. No Time Machine scoring, ablation, sensitivity or outcome-hit run has been performed.

## What CI runs

| Job | What it checks |
|---|---|
| `lint` | `ruff check` and `ruff format --check` on `backend/`, `scripts/` and `tests/`; `prettier --check` on `frontend/src` and `frontend/e2e` |
| `backend` (Python 3.10, 3.11, 3.12, 3.13) | bootstrap, `verify.py`, `check_migrations.py`, research example validation, `verify_research.py`, Time Machine packet/coverage audit, **pytest (235 tests)**, `export_contract.py --check` (OpenAPI and generated TypeScript in sync), evaluation, research and discovery imports, frozen evaluation workbench, academic demo |
| `browser` (Ubuntu 24.04, Chromium) | production build, then **49 Playwright tests** against a disposable database, with screenshots and the HTML report uploaded as an artifact |

## Coverage of the critical rules

Backend line coverage is about 95% overall. The modules that carry the comparison and outcome rules:

| Module | Lines covered | What the tests pin |
|---|---|---|
| `precedents.py` | 100% | Latest-status ladder, including closure vs exit ordering and overlap; alternate-clock outcomes; frozen outcomes withheld before the follow-up cutoff |
| `precedent_similarity.py` | 100% | Gower scoring and missingness; thresholds; top-k; ceiling, typical and floor; all-unresolved abstention; nearest candidates without outcomes |
| `witnessed_snapshots.py` | 100% | All ten packet rejections (late publication, contemporaneous field scope, witness timing, milestone Yes/No and others) |
| `precedent_evidence.py` | 99% | As-of filters on pool and research claims; latest-day review disputes; anchor selection |
| `workbench_gates.py` | 100% | Gate counts and blockers; `validation_state` is always `not_validated` |

## Sealed estimator

- `backend/precedent_outlook.py` (the Aalen–Johansen estimator) is imported only by its own tests.
- It returns nothing unless the gate is ready and n_eff ≥ 10.
- The live gate is withheld: 55 of 150 companies, 2 of 30 outcomes, and unknown or lost far above 25%.
- A browser test injects a synthetic probability into the gates response and confirms that the UI never shows it.

## Known limits

- **Data has not been re-verified end to end.**
  - The 2026-11-21 spot check found no contradiction in 17 entry claims.
  - The seven PwC Young Company Finance rows were hand-checked against the PDFs on 2026-11-21, and all match. One cited URL (HiNZ) is still dead (see [STATUS.md](STATUS.md)).
  - Tests check rules and provenance structure, not the truth of what the publishers report.
- **Browser coverage** is Chromium on Ubuntu 24.04 only. That pin is deliberate until Playwright is upgraded.
- **Observed intermittent failure.** On 2026-11-21, one run of `healthtech.spec.ts › directory counts distinct ventures…` failed with a `socket hang up` on a CSV download through `page.request`. The rerun passed. That code path was unchanged. The likely cause is a reused keep-alive connection closed by the server; watch for it before changing the server config. Retries are deliberately not enabled.
- **No relevance or usefulness metrics.** The six evaluation queries have no human labels, so nothing is claimed about precision, usefulness or time saved.
