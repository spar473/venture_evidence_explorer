# Continue from another desktop

Repository: https://github.com/spar473/venture_evidence_explorer

Working branch: `implementation/vee-workbench`

```sh
git clone --branch implementation/vee-workbench https://github.com/spar473/venture_evidence_explorer.git
cd venture_evidence_explorer
```

In GitHub Desktop, clone this repository, then select **implementation/vee-workbench** from Current Branch.

Clone this branch first:

```sh
git clone --branch implementation/vee-workbench https://github.com/spar473/venture_evidence_explorer.git
cd venture_evidence_explorer
```

This branch contains the actual implemented application, research contracts/fixtures, discovery inventory, tests, supplied handovers/reviews, executed verification records, screenshots and a consistent evidence-database snapshot. The Mac working directory was an exported folder without Git metadata; its contents were copied into this repository's existing history. Local dependencies, caches and credentials are not transferred.

## Checkout

```sh
git clone --branch implementation/vee-workbench https://github.com/spar473/venture_evidence_explorer.git
cd venture_evidence_explorer
```

Authenticate with GitHub on that desktop for this private repository. No Mac filesystem path in an archived log is a required setup path.

## Windows PowerShell

Use Python 3.12 and Node 22. The following Windows commands are provided as instructions; Windows execution was not tested on the Mac.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe scripts/restore_handover_snapshot.py
Push-Location frontend
npm ci
npm run build
Pop-Location
.\.venv\Scripts\python.exe scripts/serve.py --port 8170
```

Open http://127.0.0.1:8170. Stop the process with Ctrl+C. To resume an already installed checkout, run the final serve command; do not restore over an existing working database.

## macOS / Linux shell

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python scripts/restore_handover_snapshot.py
cd frontend
npm ci
npm run build
cd ..
.venv/bin/python scripts/serve.py --port 8170
```

Use an available compatible Python executable if it has a different name. Locked dependencies remain unchanged. Previous verification passed on macOS; Linux/Python 3.13 and remote CI were not executed during the implementation/review-fix tasks.

## Data and verification

`restore_handover_snapshot.py` copies the archived SQLite snapshot into ignored `outputs/venture_evidence.sqlite`. It refuses an existing destination. Never serve/edit the tracked snapshot directly. Its manifest includes all six applied migration checksums and exact counts. The snapshot retains 10 core ventures, 2 research dossiers, 274 discovery leads in staging, two proposed mappings, zero promotions, zero saved drafts and zero human acceptance decisions. These are evidence-record grains, not a national population.

For a deliberately fresh database instead, run `scripts/bootstrap.py`, then explicit research/discovery import commands in the README. Do not run bootstrap/import merely to start an already restored snapshot. Optional `VEE_DB` selects another existing migrated database (`$env:VEE_DB='C:\absolute\working.sqlite'` in PowerShell or `VEE_DB=/absolute/working.sqlite` in a shell).

Read `engineering_completion.md` for the latest fixes and results: 133 backend passes on Python 3.12; 131 passes plus 2 version skips on Python 3.10; 32 bundled-Chromium browser passes. These are observed historical Mac results, not a promise that a new desktop has already been tested. Backend checks use disposable databases. In PowerShell, use `.\.venv\Scripts\python.exe -m pytest -q` and `.\.venv\Scripts\python.exe scripts/export_contract.py --check`.

For browser tests, run `npx playwright install chromium` from `frontend/`, set `VEE_PYTHON` to the absolute local virtual-environment Python path, and run `npx playwright test`. Use Node 22; the recorded Node 26 browser extraction issue and successful Node 22 retry are retained in the verification history. Do not point browser tests at a live evidence database.

## Where to read next

- `handover/README.md`: package map and authoritative current versus historical material.
- `engineering_completion.md`: latest implemented state, observed checks and boundaries.
- `handover/inputs/`: supplied instructions, frozen references and reviews, unchanged.
- `handover/verification/`: core, pilot, later prompts and review-fix evidence/logs.
- `research/framework-v0.2.1/`: unchanged research contract/schema/validator/example.
- `docs/intake.md`, `docs/research_import.md`, `docs/discovery.md`: working workflows.
- `evaluation/protocol-v1/`: blank human-review inputs; no invented people or grades.

Continue implementation on the working branch. Keep source and handover updates in Git; working databases and installed dependencies remain local. A future reviewed change may be merged into the default branch explicitly. No deployment is included in this handover.
