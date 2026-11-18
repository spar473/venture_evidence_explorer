# Venture Evidence Explorer — Prompts 2–5 completion

18 November 2026, Pacific/Auckland. The saved-intake, discovery-staging and honest-evaluation milestones are implemented. Fresh locked installation and local release checks were executed; exact environment coverage and any browser installation limitations appear below. This report supersedes the root Prompt 1 status without replacing its history. The prior report is retained under this chat's `outputs/remaining/previous_prompt1_engineering_completion.md`; the original research-package reports/manifests remain unchanged historical references.

## Revision, preservation and scope

Repository: `/Users/kevinnn.park/Documents/venture_evidence_explorer`. There is no local Git metadata/HEAD. Rechecked all **136 current source files** against the completed pilot before editing; no drift from the pilot source manifest. Work was isolated in this chat's `work/remaining/repository`. The clean installation source was `work/remaining/fresh-source`; it contained no virtual environment, node_modules, built frontend or database before checks. Source hashes were checked again before application. Original application input versions 1/2, research interchange 0.2.1, seed/evidence, review history, research reference files and applied migrations 001–004 were retained. No push, remote CI trigger, deployment, external AI call or paid service was used.

Applied additive migrations 005/006 after a consistent SQLite backup. Every row of all **21 original data/review/metadata tables** remains unchanged, including the two-dossier graph and proposed mappings. All four original migration ledger entries/checksums remain identical; the ledger now contains six migrations. Repeating the actual discovery import produced full-row equality across all tables. FK/integrity and B0 result/selected-evidence checks passed. The real database has **730 discovery records, 2,218 discovery links, 274 staged candidate leads, zero promotions, zero new human reviews and zero draft assertions**. Accepted NZ population remains null. Backups and exact hashes/row counts are in `outputs/remaining/backups/` and `preservation-and-apply.json` under this chat workspace.

Existing B0 scores/order/selected evidence and accepted-only safeguards remain unchanged. Its conservative digest includes all user tables; adding migrations/staging invalidates old run digests even when rankings are identical. Retain the pre-change code/database snapshot to replay old records. The explicit intake wrapper has its own `intake-b0-query-1.0` version and does not silently change B0 query interpretation.

## Prompt 2 — saved intake and comparison

Implemented `venture-intake:1` models/API, additive migration 005, append-only drafts/revisions, request retry keys, optimistic revision conflicts, rollback and immutable history. **Add venture** saves/reopens local name, aliases, description and optional source attributions. Publication day/month/year/unknown precision, retrieval dates, source URL/title/publisher/locator/responsibility and explicit unknowns are retained. User assertions remain `local_user_assertion`; supplied URL claims remain `user_supplied_source_attribution_unreviewed`. No owner acceptance, legal identity or publisher authentication is inferred.

Duplicate previews inspect aliases/names across app/research/drafts and never merge automatically. Pending research mappings are visible and do not block intake. A selected research subject supplies query context; only a genuinely resolved stored research-to-app mapping excludes that app subject. No supplied real mapping was resolved by this work.

The saved draft provides a deterministic literal comparison query; descriptions/attributed text are query inputs, never corpus evidence. Its comparison table includes the draft's missingness/status and up to three sourced candidates with contributing terms/evidence and withheld results. Exploration versus accepted policy remains explicit; no accepted evidence yields abstention. Unsaved input is retained locally, failures keep typed fields and saved input survives reload. Current draft list is bounded to the latest 100 with a total count. Occurrence dates can be supplied via the strict API; the optional-source form leaves them unknown.

Stage gate: **98 backend passed, 2 skipped; 19 browser passed; build and OpenAPI/type drift passed**. Regression cases cover revisions/retry, duplicate aliases, invalid source/date inputs, failed persistence without partial records, reload/reopen, synthetic resolved-subject exclusion, corpus isolation and accepted-only withholding. Synthetic fixtures were used only in disposable test databases. No demonstration draft was inserted into the real database. See `docs/intake.md` and `stage_records/prompt2.json`.

## Prompt 3 — historical discovery staging

Inspected and preserved the actual `expanded-discovery-0.1` packet and accompanying list/validation report. The explicit `Discovery_staging_v1.schema.json` is a staging-adapter boundary, separate from research 0.2.1. Migration 006 stores exact raw bytes/hash, stable IDs, full JSON rows, memberships, relationships, decision documents and append-only scoped reviews. Records without supplied IDs use content-derived stable IDs. Unknown/unsupported properties are refused rather than discarded. The whole staging import commits or rolls back; exact repeats preserve every row.

**274 discovery leads, 27 source families, 42 sources, 365 overlapping listings, 4 dated outcome reports, 2 explicit name links and 16 unresolved cases** are retained. These counts are editorial/staging grains, not a population or verified unique NZ ventures. Current portfolio listings do not establish historic membership, dates, cheques, fund vehicles or operating status. All absent dates/status/funding fields stay null. Name links and Kura/KuraDynamics-like duplicates remain review candidates, separate from legal continuity.

**Discovery queue** provides search, family/status/gap filters, reported-outcome year and unknown-period filters, paging, a source/evidence drawer, aliases/cases/outcomes, keyboard focus/Escape and lossless CSV exports. Period filters describe supplied outcome reports, not company founding/investment dates or complete historical coverage. The promotion dry run checks real scoped identity, NZ and period decisions and passes an explicitly supplied research packet through the research adapter. Source-checked evidence alone fails acceptance requirements. It performs no writes and there is no automatic promotion endpoint. Reviews can be supplied by an explicit strict sidecar; no genuine decision document was available or invented.

Stage gate: **104 backend passed, 2 skipped; 20 browser passed; build/type drift passed**. Verified exact packet bytes, totals, repeat equality, original-table preservation, rollback after earlier sources, immutable conflicts, reference/schema refusal, overlapping relationships, alias preview, null precision/date semantics, promotion refusal and CSV roundtrip. **274 staged / 0 promoted; accepted NZ population remains unknown**. See `docs/discovery.md`, `stage_records/prompt3.json` and `scripts/import_discovery.py`.

## Prompt 4 — frozen, label-gated evaluation

Implemented `evaluation-workbench:1`, strict task/reviewer protocols, frozen SQLite/canonical corpus/tasks manifest with data/code/method hashes, source/review chronology checks and drift refusal. Original six development tasks, blank `evaluation/judgments.csv` and B0 golden expectations are unchanged. New `evaluation/protocol-v1/` files are separate; no reviewer identities, grades, consent, timestamps, factual assessments or task-time observations were fabricated.

Query-specific inclusion criteria, suggested closer alternatives/distractors beyond the two pilot dossiers, stable candidate IDs and evidence gaps are exported. Suggestions are inspection hypotheses, not labels. All related seed tasks/identities form one development cohort. A separate held-out ID/group is explicitly `awaiting_evidence`; no new query, independent sourced cohort or held-out result is invented. Two contrasting dossiers do not constitute a benchmark.

Exported **60 blank task/candidate review rows** plus blank reviewer, factual-audit, adjudication and analyst time/usefulness materials. Actual human declarations record role/independence, grade 0–3, rationale, selected subject-correct observation IDs and valid chronology. The tool validates supplied lineage but cannot authenticate people. Disagreements retain separate reviewer records without synthesizing consensus. Blank labels never become zeros.

Metrics are reviewer-specific: precision uses returned-result denominator; nDCG@3 requires complete eligible-corpus labels, explicit zero-ideal/abstention handling. No recall from partial labels. Aggregate/adjudicated metrics and uncertainty remain null when unsupported. Method comparison requires identical frozen inputs/eligible identities/tasks/policy/labels and recomputes metrics. Only B0 is currently runnable; the blank self-comparison is a refusal check, not a second-method experiment. A seeded paired-cluster bootstrap helper is tested with synthetic numbers and requires eight declared independent groups; the actual one-group unlabeled corpus cannot support intervals.

Executed frozen development run: **6 tasks run, 2 return results, 4 abstain** (operational coverage 1/3, not relevance). Human relevance status is **not_evaluated / judgments_missing**; factual audit, usefulness and time-saving evidence remain absent. Held-out run executes **0 tasks**, with the explicit pending data reason. SQL SELECT counts and warm comparison-plus-serialization latency are measured separately, with digest cost/environment/corpus size disclosed in each run. Structural source/subject reference checks are not entailment judgments.

Stage gate: **112 backend passed, 2 skipped; OpenAPI/type drift passed**. Eight added protocol tests exercise leakage, frozen-input drift/reproducibility, malformed/incomplete grades, evidence/date/reviewer gates, disagreement/audit retention and refusal of invented numerical metrics. Metric/bootstrap fixtures are synthetic-only. Review/freeze outputs refuse overwriting nonempty directories. See `docs/evaluation_workbench.md`, `stage_records/prompt4.json`, this chat's `outputs/remaining/evaluation-frozen/`, `human-review/`, `development-run.json` and `held-out-status.json`.

## Prompt 5 — actual installation and release verification

Three new virtual environments successfully installed the unchanged `requirements.lock.txt` through pip. The 3.10 installation used cached wheels; 3.11/3.12 downloaded or reused wheels into absent environments. No installed site-packages were copied. `pip check` passed in all three. `npm ci` succeeded from the unchanged package lock in the clean frontend, including a repeat under the CI major Node 22. Both lock hashes match the original repository, and the original database bytes remained unchanged throughout clean verification.

| Local environment | Final backend | Other observed checks |
|---|---|---|
| Python 3.10.10 / SQLite 3.39.4 | **113 passed, 2 skipped**, 10.47 s | Bootstrap/integrity, two migration transaction modes, research semantic/regression validator, lossless research verification, research/discovery imports/repeat, frozen review/evaluation commands and type drift passed. |
| Python 3.11.5 / SQLite 3.41.2 | **113 passed, 2 skipped**, 9.49 s | Fresh pins, dependency check, type drift and two migration transaction modes passed. |
| Python 3.12.15 / SQLite 3.54.1 | **115 passed**, 9.86 s | Fresh pins, dependency check, type drift and three migration transaction modes including autocommit=True passed. |
| Node 26.12.1 / npm 11.20.0 | Locked `npm ci`, type/build passed | 20 browser tests passed with installed macOS Chrome 157.0.8103.79; this is a separate explicit browser fallback. |
| Disposable Node 22.23.5 / macOS arm64 | Locked `npm ci`, type/build passed | **20 browser tests passed, 29.4 s**, with freshly installed bundled Chromium/Headless Shell **145.0.7632.6, revision 1208**, Playwright 1.58.2; Python 3.12.15 disposable database. No CHROME_PATH override in this run. |

The Node 26 full Chromium installer downloaded the archive then stalled during extraction and timed out after **600.12 s** (exit 124). A separate headless-only attempt was stopped after **222.817 s** without further progress (SIGTERM). Both failures are retained. Retrying the same locked browser revision with disposable Node 22.23.5 succeeded in **22.194 s**; bundled-browser tests then passed. This is an observed host/runtime issue, not a proven general cause; no package pin was altered. The configured Node 22 build/browser path is now locally executed. The macOS result does not establish the Ubuntu/Linux CI result.

Fresh verification additionally ran the original blank B0 evaluation and existing academic synthetic demo. Human relevance metrics remain null. The initial malformed-URL regression failed as intended before the fix; final suites include its passing rejection-before-write test. No unexecuted check is described as passing.

The configured workflow now includes research/discovery imports and frozen blank-review evaluation. It was inspected and extended locally, **not remotely executed**. Python 3.13 and Linux/Ubuntu CI execution remain unexecuted on this macOS host; no Docker executable was found at the inspected standard locations. These are explicitly outside the observed local passes. Dependency pins/lockfiles were not changed to get green results. npm reported optional fsevents install scripts without allowScripts approval; no blanket script approval or dependency upgrade was performed. A malformed discovery URL regression first failed, then passed after strict URI/HTTPS/host/credential validation was added before any database write; failure and final suite logs are preserved. The older evaluation-plan threshold mismatch was documented explicitly without changing existing B0 metrics. Backend runs have one upstream Starlette/AnyIO deprecation warning.

Every fresh-install command, working directory, exit code and elapsed time is recorded in this chat's `outputs/remaining/fresh-install/*.json` with corresponding complete `.log` files. `environment.json` records exact lock hashes and installed Python versions; `tested-source.json` records the source checked for equality with staging. `release-verification.json` aggregates actual results, while `REMAINING_SHA256SUMS.txt` describes delivered source. Earlier manifests remain historical. Recovery/run instructions are in `docs/release_reproducibility.md`.

Final checks from the **applied repository** passed: **113 backend tests, 2 skipped** (10.65 s); OpenAPI/generated TypeScript drift; ordinary disposable integrity/rollback checks; and lossless research preservation/rollback verification. A read-only API smoke covered **59 route requests**, preserved both proposed pilot mappings, the original 10-venture directory, discovery filters/duplicates/promotion refusals, seven packet-row-equal discovery CSVs, all sixteen subject-filtered research CSVs for both dossiers, exact research packet bytes, B0 comparison and built frontend. The actual database byte hash was unchanged by this smoke.

The task's own prior loopback service was restarted with the new source on **http://127.0.0.1:8170**. Other user services were not stopped. The supplied discovery packet is staged only; no automatic import occurs on subsequent server startup. Exact copy-back commands/scripts are retained under `work/remaining/apply_remaining.py` and `finalize_remaining.py`; replaced-file backups permit inspection/recovery. Initial screenshot/probe invocations had selector/working-directory/assumed-discovery-ID errors; corrected captures and the final smoke passed. Those early probes are not counted as successful application checks.

## Exact operational commands

Repository-root commands below use the installed environment and explicit disposable paths where appropriate. Run schema preparation/import only after a SQLite backup on an existing database. Dry-run is the discovery default; startup never imports data or fabricates review decisions.

```sh
.venv/bin/python scripts/import_discovery.py --report outputs/discovery-dry-run.json
.venv/bin/python scripts/import_discovery.py --db outputs/venture_evidence.sqlite --apply --report outputs/discovery-import.json
.venv/bin/python scripts/import_discovery.py --db outputs/venture_evidence.sqlite --apply --report outputs/discovery-repeat.json
.venv/bin/python scripts/evaluation_workbench.py freeze --db outputs/venture_evidence.sqlite --output-dir outputs/frozen-evaluation --as-of 2026-11-18
.venv/bin/python scripts/evaluation_workbench.py review-materials --bundle outputs/frozen-evaluation --output-dir outputs/human-review
.venv/bin/python scripts/evaluation_workbench.py run --bundle outputs/frozen-evaluation --output outputs/frozen-development-run.json
.venv/bin/python scripts/evaluation_workbench.py run --bundle outputs/frozen-evaluation --split held_out --output outputs/held-out-status.json
.venv/bin/python scripts/evaluation_workbench.py compare --left outputs/method-a.json --right outputs/method-b.json --output outputs/paired-comparison.json
.venv/bin/python scripts/verify.py
.venv/bin/python scripts/verify_research.py
.venv/bin/python scripts/check_migrations.py
.venv/bin/python scripts/export_contract.py --check
.venv/bin/python -m pytest -q -p no:cacheprovider
.venv/bin/python scripts/serve.py --port 8170
```

The final fresh-install commands used absolute interpreter paths under this chat's `work/remaining/fresh-env`, `fresh-env311` and `fresh-env312`, not the original `.venv`; frontend checks ran in `work/remaining/fresh-source/frontend`. Exact executable invocations, configured port/browser overrides and times are in the named check records/logs. The command to compare two actual method reports is documented but no real two-method/real-label comparison was supplied or claimed. The executed blank self-comparison is saved as `blank-comparison-check.json` with null outcomes.

Demonstrate locally: choose **Add venture** for an empty user-assertion form (the real database contains no synthetic example drafts); **Discovery queue** → Kura or RosterLab for unresolved aliases, relationships, source lineage and withheld promotion; **Research dossiers** → RosterLab/QuickMas for the preserved evidence/unknowns. Saved screenshots are disposable-database captures. Screenshots/source link href checks do not establish publisher truth or research acceptance.

## Implemented, synthetic-only, scaffolded and deferred

| Status | Functionality / boundary |
|---|---|
| Implemented and verified | Core A–F and Prompt 1 pilot retained; Prompt 2 saved intake/comparison; Prompt 3 lossless staging/review preview/exports; Prompt 4 frozen evaluation, real-label validation and blank review workflow; Prompt 5 actual local clean installs/checks with platform limits stated above. |
| Synthetic-only verification | Test assertions/actors/decisions, numerical metric/bootstrap fixtures, scale fixtures and the existing E2 academic demonstration. They are not human relevance/research findings. |
| Scaffolded / evidence pending | Existing E1/E3 academic extensions; reviewer/adjudication/time/usefulness templates; independent held-out task ID; review sidecars requiring genuine decisions. A writable review UI, accepted-feature projection and additional runnable retrieval methods are not implemented. |
| Deferred | E4/sequential planning, broad national-history curation, automatic promotion/merging, external research collection/source archives, actual Power BI `.pbix`, PostgreSQL deployment and remote publication. |

Actual pending decisions remain: pilot brand/project mappings; legal identity and historic continuity; financing-candidate reconciliation; payer/procurement/integration facts; dated NZ/period inclusion for discovery; authorized factual acceptance; real reviewers/labels/adjudication; independent sourced held-out cohorts; and analyst time/usefulness observations. Blank human judgments remain blank. No new external research, coverage, relevance, generalisation, investment quality or time-saving result is claimed.
