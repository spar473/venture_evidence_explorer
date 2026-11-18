# Venture Evidence Explorer — current-state review fixes

18 November 2026, Pacific/Auckland. **Implemented the three confirmed findings F1–F3 and the review's bounded dossier/discovery presentation improvements.** The supplied review, fix prompt, verification record, source manifest, diagnostic probes and captures were treated as technical evidence under the user's implementation request. The archive was not extracted over the application. This task added no corpus records or human judgments and performed no external venture research, push or deployment.

## Recheck and preservation

All **153 reviewed source files** matched the current repository; every supplied archive checksum passed. Snapshotted **172 existing files** before changes, including the live SQLite file and existing reports/builds. No local Git metadata exists. Work and tests ran in an isolated source copy, using disposable databases. Reused installed Python/frontend dependencies and previously installed bundled Chromium; **fresh installs were not repeated for this fix task**. Prior clean-install records remain attributed history.

Applied verified source changes only, with backups of every replaced file and a consistent SQLite snapshot. **The live database is byte-for-byte unchanged** (SHA-256 `09775f184b8d18a535f318c390a83e6d4cabd038b6627d1c1947d47802370431`). Full-row equality holds across all **30 original tables**, including the six-entry migration ledger. **No migration was added or rewritten.** Existing evidence, raw packet bytes, review history and pending identity mappings remain intact. The live database still has zero saved drafts/revisions and zero mapping decision documents; test assertions/actors never entered it. All original files were checked immediately before copy-back to refuse concurrent user edits. Eighteen B0 query/mode/policy comparisons retain identical result/evidence signatures and run records, including accepted-only abstention and corpus digests.

The prior completion report is preserved as this chat's `outputs/current-review-fixes/previous_engineering_completion.md`. Existing research/review documents and historical manifests remain unchanged. `REVIEW_FIX_SHA256SUMS.txt` describes this corrected source; older manifest mismatches after these edits are expected provenance, not rewritten history.

## F1 — save/editor association

Pending saves disable draft switching, starting another draft and form edits. Save/comparison success, errors and busy transitions are bound to the mounted editor identity/request generation; unmount invalidates old completions. A late response cannot attach draft A's pointer to draft B's form. Save routes and payloads come from one captured editor session. Current/latest metadata is reconciled without replacing local form edits.

Correct-behavior browser regressions failed against the unchanged baseline, reproducing both race/reload defects. They now verify delayed save → attempted switch → subsequent edits to B, with both IDs retaining their own names/content/revision histories. Another test leaves/remounts the intake tab while a save response is delayed, then acknowledges the retained request without appending another revision.

## F2 — recovery, conflicts and uncertain saves

Added `frontend/src/intake-session.ts` and the versioned local recovery key `vee:intake-editor:2`. It persists form values, stable editor ID, saved draft ID/base revision and the exact pending route/body/request ID **before a write is sent**. This is a browser recovery container; research interchange stays 0.2.1, application inputs stay 1/2 and local draft interchange stays `venture-intake:1`.

Reload/tab return re-fetches the saved record while preserving unsaved edits and identity. A different server revision blocks saving and displays the conflict. **Use latest revision as base, keeping my edits** is an explicit user choice; no automatic rebase, duplicate create or field replacement occurs. A failed reconciliation retains identity and edits and offers retry. **Start another draft** explicitly clears the active identity/form. Old identity-less local-storage forms remain intact and require selecting an existing draft or explicitly treating the recovered input as new.

Network/5xx uncertainty retains the exact request and locks edits/switching until **Retry uncertain save** acknowledges it. Lost create/revision responses survive reload with the same retry key, route and payload. The backend now returns the original immutable revision for that request even if a newer revision exists; ordinary GET still returns latest. The UI checks current server state and exposes a conflict rather than silently replacing local edits. If the new request journal cannot be persisted, saving is refused before any write and typed input remains in memory.

Browser recovery is origin/browser specific. Clearing site storage, changing origin/browser or an unavailable browser store cannot provide durable recovery beyond retained memory/server records. No source assertion becomes accepted publisher evidence, legal identity or corpus evidence through these editor fixes.

## F3 — consistent identity-mapping chronology

Mapping evidence follows explicit provenance chains: observation → source; report → source/observations; event → state-basis reports; conclusion → basis observations/sources; requirement/readiness → supporting records; unknown → inspected sources; annotation → basis observations; case → events/observations. Nested requirements/conclusions inherit their enclosing readiness cutoff/review date. Referenced acceptance-event review dates are followed with cycle protection through targets.

A mapping decision cannot predate any applicable exact source inspection, assessment or review day. Each cited item must reach an actually read textual source. Source-less subject/party assertions and failed-access records do not independently support a resolution/rejection; actual source-backed evidence is required. Subject coverage of shared requirements is checked. This enforces provenance/chronology, not the truth or adequacy of a human's rationale, and cannot authenticate an actor.

Publication/event intervals, target years and unknown occurrence times are **not** converted to inspection dates or forced exact-day deadlines. Raw partial-date bytes remain unchanged. Valid same-day/later synthetic decisions and exact repeat imports pass; legal identity stays unresolved. Invalid decisions/batches leave mapping documents, decisions and research import rows unchanged. No applied migration needed modification.

The pre-fix chronology regression had **8 failures / 1 passing direct-source control**. New tests cover direct/indirect source/report/event/conclusion/requirement/readiness/unknown/annotation paths, source-less refusal, later decisions, parent assessment dates, acceptance-review cycles, failed access and rejection of a batch containing an earlier valid decision. Synthetic actors/decisions exist only in disposable/unit fixtures; none were written to the live database.

## Dossier and discovery presentation

Dossiers lead with supplied attributed solution, user and customer descriptions with source links, followed by a compact evidence timeline. Payer/procurement uncertainty, source-check versus acceptance and brand/project versus legal identity remain explicit. The timeline orders source publication where known; it does not claim verified occurrence order. Prospective targets and year/month/day/unknown precision remain visible, financing duplicates are flagged and totals/distinct rounds remain withheld. Full identity/mapping audit is available in a disclosure, with all original evidence/exports retained.

Discovery uses readable status/gap/filter labels, concise gap disclosures and inspectable stable IDs instead of repeated implementation keys. API/filter values and raw CSV IDs/provenance are unchanged. The zero-result pager now displays 0–0. Drawer/source details and complete records remain inspectable. Desktop/mobile captures were inspected; this is bounded presentation verification, not a formal usability or accessibility study.

## Executed checks

| Check | Newly executed result |
|---|---|
| Baseline backend, Python 3.10.10 | **113 passed, 2 skipped**, 11.48 s. |
| New pre-fix backend controls | Direct source rejected; **8 indirect/assessment regression expectations failed** against the old implementation, confirming the uncovered defects. |
| New pre-fix browser controls | Both correct-behavior race/reload regressions failed against the original built app and disposable service. |
| Final Python 3.12.15 backend | **133 passed**, 14.66 s; no version skips. |
| Final applied Python 3.10.10 backend | **131 passed, 2 skipped**, 17.71 s; skips are Python 3.12-only transaction paths. |
| Final browser suite | **32 passed**, 31.8 s; Node 22.23.5, bundled Chromium 145.0.7632.6 / revision 1208, disposable DB. |
| Frontend | TypeScript/Vite build passed; 33 modules. |
| API/generated types | Drift check passed in isolated and applied repositories; API shapes unchanged. |
| Integrity/repeat/rollback | Ordinary and research preservation verifiers passed; migration failure/retry/caller-transaction checks passed in all three Python 3.12 transaction modes. |
| Actual data preservation | All 30 original tables and six migration checksums unchanged; entire live DB byte hash unchanged. |
| B0 preservation | 18 before/after query × mode × policy checks have identical result/evidence/run records. Existing golden tests pass. |
| Live local UI | Read-only intake/dossier/discovery smoke passed with no page errors or DB writes; screenshots captured. |

Added **18 backend regression cases** and **12 browser cases** beyond the old suites. Backend tests cover direct/indirect chronology, source-less refusal, valid same-day/later decisions, raw year/unknown date preservation, rejected-batch atomicity, acceptance-event reference cycles and exact retry revision after a later edit. Browser cases cover delayed-save switching, unmount/remount, reload/tab return, concurrent revision reconciliation, lost create/revision responses with identical retry requests, legacy identity selection, unavailable recovery storage and evidence-presentation semantics.

The task's own local service was restarted at **http://127.0.0.1:8170** with the corrected code. No other service was stopped. Live captures created no drafts or decisions. Linux, Python 3.13 and remote CI were not run in this task; prior fresh-install results remain attributed historical records.

Every recorded check has the exact command, working directory, exit code, elapsed time and full log in this chat's `outputs/current-review-fixes/checks/`. `executed-commands.md` indexes them. Before-fix expected failures are preserved as evidence; they are not counted as correctness passes. An early build/probe command used the wrong working directory, and an intermediate build caught duplicated hook declarations; both were corrected before final checks. Existing Starlette/AnyIO deprecation and terminal-color warnings are upstream/runtime warnings.

Typical verification commands (repository root, browser/build commands from `frontend/`):

```sh
.venv/bin/python -m pytest -q -p no:cacheprovider
.venv/bin/python scripts/export_contract.py --check
.venv/bin/python scripts/verify.py
.venv/bin/python scripts/verify_research.py
.venv/bin/python scripts/check_migrations.py
npm run build
PLAYWRIGHT_BROWSERS_PATH=/absolute/bundled-browser-directory VEE_PYTHON=/absolute/python VEE_TEST_PORT=8189 node node_modules/playwright/cli.js test
```

Actual commands used the existing original Python 3.10 environment and previously installed disposable Python 3.12.15 environment, plus Node 22.23.5 / bundled Chromium 145.0.7632.6 (revision 1208). Build also passed on Node 26.12.1. Browser harness imports only into its temporary database. Local copy-back refuses overlapping source edits, preserves replaced files and makes a consistent SQLite backup. Recovery: use the saved source/database together in a separate directory and unused loopback port; retain any later current records and never overwrite a live database blindly.

Final applied checks: 131 backend passes and 2 Python-version skips; API/type drift passed. All 18 before/after B0 policy/mode checks and complete run records match. Read-only live UI smoke and captures passed at http://127.0.0.1:8170 with zero page errors and unchanged database bytes.

## Remaining boundaries

Core A–F, pilot dossiers, local intake, discovery staging and frozen evaluation remain implemented. The retrieval corpus is still **10 ventures / 20 observations**; discovery is **274 staged leads / zero promotions**, not a national population. Two pilot mappings stay proposed; legal/payer/procurement and financing reconciliation remain unresolved. No real human relevance/factual judgments, independent held-out research, time/usefulness observations or new acceptance records were supplied. Their metrics remain null; no reviewer identities or decisions were invented.

Academic E1/E3 remain scaffolded, E2 remains synthetic-only, and E4/sequential work remains deferred. A richer reviewed historical corpus, new retrieval methods, broader visual analysis and human research remain separate. Python 3.13, Linux/remote CI and new fresh-install checks were not executed for this task; earlier release verification is preserved as history. No push/deployment or external service was used.

## Remaining scope and academic status

The three confirmed defects are fixed. Browser recovery remains local to its origin/browser; lost storage cannot identify an unacknowledged create in another browser. Pending requests must be retried before further editing/switching. The software validates represented provenance/chronology, not actor authenticity or the adequacy of a human identity judgment. Source-less identity decisions need an explicit source-backed basis.

The comparison corpus remains ten original ventures; 274 discovery leads remain staging only, with zero promotions. Genuine identity/legal/event reconciliation, source acceptance, human relevance/factual grades, independent held-out research and analyst usefulness/time observations are still pending. Metrics and judgments remain unfilled where unsupported. The timeline is an implemented view of supplied source dates/targets, not newly researched or verified venture history. Broader visual comparison, national historical curation and a writable review interface remain separate work.

Academic classification is unchanged: E1/E3 scaffolded; E2 implemented as a synthetic-only demonstration; E4/sequential work deferred. No empirical relevance, investment-quality, generalisation or time-saving result is inferred from software tests.
