# Validation

Current record, refreshed on 2026-11-21 after the pre-demo polish sprint. CI is the source of truth: every pull request and every push to `main` runs the workflow in `.github/workflows/checks.yml`. The original 17 November release record is kept in [docs/archive/VALIDATION-2026-11-17.md](docs/archive/VALIDATION-2026-11-17.md).

## What CI runs

| Job | What it checks |
|---|---|
| `lint` | `ruff check` and `ruff format --check` on `backend/`, `scripts/` and `tests/`; `prettier --check` on `frontend/src` and `frontend/e2e` |
| `backend` (Python 3.10, 3.11, 3.12, 3.13) | bootstrap, `verify.py`, `check_migrations.py`, research example validation, `verify_research.py`, **pytest (213 tests)**, `export_contract.py --check` (OpenAPI and generated TypeScript in sync), evaluation, research and discovery imports, frozen evaluation workbench, academic demo |
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
