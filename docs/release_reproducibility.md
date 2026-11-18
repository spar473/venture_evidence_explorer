# Local release verification and recovery — Prompt 5

Use a new disposable source directory, with no `.venv`, `node_modules`, built assets or database. Preserve the original project/environment/database while checking installation. Do not change pins to conceal failures. A package-manager wheel cache is compatible with a fresh virtual environment; copied installed packages are not a fresh install.

```sh
python3 -m venv /absolute/disposable/env
/absolute/disposable/env/bin/python -m pip install -r requirements.lock.txt
/absolute/disposable/env/bin/python -m pip check
/absolute/disposable/env/bin/python scripts/bootstrap.py
/absolute/disposable/env/bin/python scripts/verify.py
/absolute/disposable/env/bin/python scripts/check_migrations.py
/absolute/disposable/env/bin/python -m pytest -q -p no:cacheprovider
/absolute/disposable/env/bin/python scripts/export_contract.py --check
/absolute/disposable/env/bin/python scripts/verify_research.py
/absolute/disposable/env/bin/python research/framework-v0.2.1/validate_research_example.py --as-of 2026-11-18
/absolute/disposable/env/bin/python scripts/import_research.py --db outputs/venture_evidence.sqlite --as-of 2026-11-18 --apply --report outputs/research-import.json
/absolute/disposable/env/bin/python scripts/import_discovery.py --db outputs/venture_evidence.sqlite --apply --report outputs/discovery-import.json
/absolute/disposable/env/bin/python scripts/import_discovery.py --db outputs/venture_evidence.sqlite --apply --report outputs/discovery-repeat.json
cd frontend
npm ci
npm run build
PLAYWRIGHT_BROWSERS_PATH=/absolute/disposable/browsers npx playwright install chromium
PLAYWRIGHT_BROWSERS_PATH=/absolute/disposable/browsers VEE_PYTHON=/absolute/disposable/env/bin/python VEE_TEST_PORT=8159 npx playwright test
```

Browser tests import the research and discovery fixtures into their own temporary database. Their synthetic draft assertions never enter the original database. `CHROME_PATH` is an explicit installed-browser alternative and must be disclosed; it does not prove a bundled-browser installation. Linux `--with-deps` belongs to the configured Ubuntu workflow and is not a macOS verification claim. No remote workflow was triggered. Exact executed commands, exit codes, runtimes and logs are in this chat's `outputs/remaining/fresh-install/`; the root completion report separates tested environments from unexecuted matrix entries.

Before applying source to an existing project, compare every baseline source hash and refuse overlapping user edits. Preserve a copy of every replaced file and make a consistent SQLite backup using `sqlite3.Connection.backup`, not an unsafe copy of a potentially active WAL database. Apply additive checksummed migrations 005/006 without editing 001–004. Discovery imports are explicit, transactional staging operations; startup never imports or accepts evidence. Compare every original data/review/metadata row and existing migration checksum before/after; repeat the staging import and compare full rows. Check foreign keys, integrity and the original B0 result/evidence signature. Old comparison digests conservatively change when new tables/rows appear; old replay requires its matching database and software snapshot.

For recovery, stop the task's own service, retain the current database as another snapshot (including any new drafts/reviews), and use a **separate recovery directory** containing the saved pre-change database and backed-up source. Do not overwrite a live/current database or delete new audit history. Run matching-source verification there, choose an unused loopback port with `VEE_DB=/absolute/recovery.sqlite python scripts/serve.py --port 8171`, and reconcile genuine later records before any replacement. Applied migration files are immutable; fix later defects with an additive migration. A prior-manifest mismatch is expected after an upgrade; do not rewrite historical provenance manifests.

Run the installed release from its repository with `.venv/bin/python scripts/serve.py --port 8170`, or another unused local port. The service binds loopback. Evidence exploration is read-only; explicit intake create/revision routes append unreviewed local drafts. Keep source/research review files, backup manifests and the human-evaluation templates together. Frozen evaluation refuses input/software drift and never overwrites nonempty experiment/review directories. No credentials, paid model calls, remote publication or deployment are required.

## Observed browser installation runtime issue

On this host, Node 26.12.1 downloaded Chromium revision 1208 but extraction made no further progress; the full installer timed out after 600 seconds, and a separate headless-only attempt was stopped after 222.8 seconds. Both logs are retained. Retrying the same locked Playwright 1.58.2 browser revision under a disposable Node 22.23.5 runtime completed in 22.2 seconds. The configured CI major is Node 22; use that major for reproducibility. This observation does not establish a general root cause or a Linux result. Project dependency versions and both lockfiles were unchanged.
