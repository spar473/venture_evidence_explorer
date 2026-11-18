# Executed commands and results

Exact command records and complete logs are retained below. Before-fix failures are expected reproduction controls, not successful fixes.

- **applied-backend310**: exit 0, 18.042 s · [log](checks/applied-backend310.log)
  CWD: `/Users/kevinnn.park/Documents/venture_evidence_explorer`

  ```sh
  /Users/kevinnn.park/Documents/venture_evidence_explorer/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/current-review/applied-tests
  ```

- **applied-type-drift**: exit 0, 0.674 s · [log](checks/applied-type-drift.log)
  CWD: `/Users/kevinnn.park/Documents/venture_evidence_explorer`

  ```sh
  /Users/kevinnn.park/Documents/venture_evidence_explorer/.venv/bin/python scripts/export_contract.py --check
  ```

- **baseline-backend**: exit 0, 11.956 s · [log](checks/baseline-backend.log)
  CWD: `/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/current-review/repository`

  ```sh
  /Users/kevinnn.park/Documents/venture_evidence_explorer/.venv/bin/python -m pytest -q -p no:cacheprovider
  ```

- **before-browser-regressions**: exit 1, 43.837 s · [log](checks/before-browser-regressions.log)
  CWD: `/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/current-review/baseline/frontend`

  ```sh
  /Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/remaining/npm-node22-cache/_npx/52027bd8fc0022aa/node_modules/node/bin/node node_modules/playwright/cli.js test intake-recovery.spec.ts -g 'delayed save prevents|reload retains' --output=/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/current-review/before-browser
  ```

- **before-chronology-regression**: exit 1, 2.832 s · [log](checks/before-chronology-regression.log)
  CWD: `/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/current-review/repository`

  ```sh
  /Users/kevinnn.park/Documents/venture_evidence_explorer/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_mapping_chronology.py::test_direct_and_indirect_backdating_rejected_before_writes
  ```

- **build**: exit 0, 4.457 s · [log](checks/build.log)
  CWD: `/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/current-review/repository/frontend`

  ```sh
  npm run build
  ```

- **final-backend312-verified**: exit 0, 15.229 s · [log](checks/final-backend312-verified.log)
  CWD: `/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/current-review/repository`

  ```sh
  /Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/remaining/fresh-env312/bin/python -m pytest -q -p no:cacheprovider
  ```

- **final-backend312**: exit 0, 15.634 s · [log](checks/final-backend312.log)
  CWD: `/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/current-review/repository`

  ```sh
  /Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/remaining/fresh-env312/bin/python -m pytest -q -p no:cacheprovider
  ```

- **final-browser**: exit 0, 33.052 s · [log](checks/final-browser.log)
  CWD: `/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/current-review/repository/frontend`

  ```sh
  /Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/remaining/npm-node22-cache/_npx/52027bd8fc0022aa/node_modules/node/bin/node node_modules/playwright/cli.js test --output=/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/current-review/final-browser
  ```

- **final-build**: exit 0, 3.373 s · [log](checks/final-build.log)
  CWD: `/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/current-review/repository/frontend`

  ```sh
  npm run build
  ```

- **focused-backend**: exit 0, 5.91 s · [log](checks/focused-backend.log)
  CWD: `/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/current-review/repository`

  ```sh
  /Users/kevinnn.park/Documents/venture_evidence_explorer/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_mapping_chronology.py tests/test_intake.py
  ```

- **focused-browser**: exit 0, 11.44 s · [log](checks/focused-browser.log)
  CWD: `/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/current-review/repository/frontend`

  ```sh
  /Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/remaining/npm-node22-cache/_npx/52027bd8fc0022aa/node_modules/node/bin/node node_modules/playwright/cli.js test intake-recovery.spec.ts intake.spec.ts --output=/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/current-review/focused-browser
  ```

- **full-backend310**: exit 0, 16.31 s · [log](checks/full-backend310.log)
  CWD: `/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/current-review/repository`

  ```sh
  /Users/kevinnn.park/Documents/venture_evidence_explorer/.venv/bin/python -m pytest -q -p no:cacheprovider
  ```

- **full-backend312**: exit 0, 16.768 s · [log](checks/full-backend312.log)
  CWD: `/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/current-review/repository`

  ```sh
  /Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/remaining/fresh-env312/bin/python -m pytest -q -p no:cacheprovider
  ```

- **full-browser**: exit 0, 34.667 s · [log](checks/full-browser.log)
  CWD: `/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/current-review/repository/frontend`

  ```sh
  /Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/remaining/npm-node22-cache/_npx/52027bd8fc0022aa/node_modules/node/bin/node node_modules/playwright/cli.js test --output=/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/current-review/full-browser
  ```

- **integrity**: exit 0, 0.313 s · [log](checks/integrity.log)
  CWD: `/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/current-review/repository`

  ```sh
  /Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/remaining/fresh-env312/bin/python scripts/verify.py
  ```

- **migrations**: exit 0, 0.086 s · [log](checks/migrations.log)
  CWD: `/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/current-review/repository`

  ```sh
  /Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/remaining/fresh-env312/bin/python scripts/check_migrations.py
  ```

- **research-preservation**: exit 0, 1.018 s · [log](checks/research-preservation.log)
  CWD: `/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/current-review/repository`

  ```sh
  /Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/remaining/fresh-env312/bin/python scripts/verify_research.py --output /Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/outputs/current-review-fixes/research-verification.json
  ```

- **type-drift**: exit 0, 0.663 s · [log](checks/type-drift.log)
  CWD: `/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/current-review/repository`

  ```sh
  /Users/kevinnn.park/Documents/venture_evidence_explorer/.venv/bin/python scripts/export_contract.py --check
  ```

- **verified-build**: exit 0, 2.72 s · [log](checks/verified-build.log)
  CWD: `/Users/kevinnn.park/Documents/Codex/2026-11-18/read-vee-engineering-review-implementation-handover/work/current-review/repository/frontend`

  ```sh
  npm run build
  ```

Browser environment: Node 22.23.5 first on PATH; PLAYWRIGHT_BROWSERS_PATH points to this chat’s work/remaining/node22-browsers; VEE_PYTHON points to work/remaining/fresh-env312/bin/python. Final disposable browser port: 8189. Dependencies/browser were reused, not freshly installed for this task.

Additional executed local scripts: `work/current-review/check_b0.py before` and `after`; `apply_fixes.py`; `capture_live.mjs`; `finalize.py`. Copy-back/source writes used sandbox escalation for the authorized repository; all evidence database connections were read-only except isolated test databases.
