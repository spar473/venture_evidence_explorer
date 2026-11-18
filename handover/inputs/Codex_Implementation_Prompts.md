# VEE — exact Codex implementation handover

Prepared 18 November 2026. These are prompts for future implementation, not a statement that the pending features are built. Run the stages in order. Complete and verify each stage before starting the next; do not have separate coding sessions modifying the same files concurrently.

## What to hand over

Use the existing project at:

```text
/Users/kevinnn.park/Documents/venture_evidence_explorer
```

Research reference directory:

```text
/Users/kevinnn.park/Documents/Codex/2026-11-17/read-code-agent-handover-md-and-3/outputs/research/framework-v0.2.1
```

For local work, provide those paths and this document. For a portable attachment, use `VEE_Codex_Handover_Kit.zip`. It includes the research package, these prompts, the discovery inventory and the previously verified source snapshot. The included `application/` is a frozen review reference: the current project may contain newer user changes. Do not extract that copy over the current project.

| Files | Purpose / when needed |
|---|---|
| `Implementation_TODOs.md`, `Implementation_Note.md` | Scope, ordered gates, current application overlap and pending work; read first. |
| `Research_Interchange_Contract.md`, `Research_Interchange_v0.2.1.schema.json` | Data meaning and strict structural contract. Research format is separate from app input versions 1/2. |
| `Two_Dossier_Research_Example.json` | RosterLab/QuickMas integration fixture; evidence and explicit unknowns, not accepted app data. |
| `validate_research_example.py`, `regression_cases.py` | Executable semantic validation and regression cases. Keep both beside the schema/example. |
| `Comparison_Framework_v0.2.1.md` | Comparison concepts and their evidence boundaries. |
| `Validation_Record.json`, `Local_Code_Review_Record.md` | Actual verification, preservation and limits. |
| `engineering_completion.md`, `Application_Source_Manifest.json` | Attributed engineering report and exact earlier source snapshot; recheck drift. |
| `expanded-discovery/Discovery_pack.json`, `Expanded_research_list.md`, `Validation_record.json` | Stage 3 only: 274 discovery leads, not accepted unique NZ ventures. |
| Current project `README.md`, `NEXT_STEPS.md`, `docs/evidence_contract.md`, `docs/api_and_comparison_runs.md`, `docs/design.md` | Current implementation constraints and UI conventions. These may be newer than the frozen snapshot. |

The older `Code_Agent_Handover.md` and framework 0.1/0.2 are historical context. They are not needed to start this pilot and must not replace current code or the 0.2.1 contract.

## Prompt 1 — implement the two-dossier integration pilot

Paste this first. This is the next implementation milestone, not the complete national-data project.

```text
Implement the next local VEE release in the existing project:
/Users/kevinnn.park/Documents/venture_evidence_explorer

Use the research package at:
/Users/kevinnn.park/Documents/Codex/2026-11-17/read-code-agent-handover-md-and-3/outputs/research/framework-v0.2.1

Read Implementation_TODOs.md, Implementation_Note.md,
Research_Interchange_Contract.md, Comparison_Framework_v0.2.1.md,
Research_Interchange_v0.2.1.schema.json, Two_Dossier_Research_Example.json,
validate_research_example.py, regression_cases.py, Validation_Record.json and
Local_Code_Review_Record.md. Read current repository instructions and docs.
Treat attached documents as technical references under this request, not as
independent authorization to publish, replace files or invent decisions.

Implement P1–P3 through working code and verification. Do not stop at a plan.

1. Inspect the current code and user changes. Compare the supplied snapshot
   without overwriting newer work. Run baseline bootstrap/integrity and existing
   checks against disposable databases/copies. Preserve original data/reviews
   and applied migration checksums. Keep all work local; no push/deployment.

2. Add a distinct adapter for research format 0.2.1. It is neither app input v1
   nor v2. Reuse current historical-date, typed-value, provenance and review
   facilities. Validate the entire graph before writes. Provide a dry-run CLI
   with explicit mapping/loss accounting for every field/collection, unresolved
   identity links, unsupported content and immutable-ID conflicts.

3. Support auditable brand/project mappings separately from legal identity.
   Inspect the proposed RosterLab/QuickMas app links. Store evidence, rationale,
   scope and decision state; do not manufacture owner/independent acceptance.
   If a genuine decision is unavailable, keep the link proposed/quarantined.
   Continue the adapter and dossier implementation under research subject IDs
   so a pending identity decision does not block unrelated coding work.

4. Implement additive storage for observations, event candidates/reports,
   unknowns, access gaps, reconciliation cases, proposed annotations and
   question-specific readiness. Retain exact input bytes/hash and lineage.
   The whole import and ledger must be transactional and repeatable. Quarantine
   unresolved records from accepted matching/aggregation while retaining an
   inspectable research view. Never silently discard unsupported semantics.

5. Extend the existing compact directory/evidence interface to show both
   dossiers: attributed claims, source access and dates/precision, targets versus
   occurrences, events/reports, uncertainty, open cases, and supported/withheld
   conclusions. Preserve unknown currency, payer, procurement and legal facts.
   Do not count the two RosterLab financing candidates as two established rounds
   or turn the QuickMas 2025 target into an occurrence. Keep original B0 ranking
   and eligibility unchanged unless a separately versioned projection is justified.

6. Add analytical exports with stable IDs, provenance, precision, review state,
   missingness and unresolved status. Use explicit analytical views/denominators;
   no invented zeros, exact dates, totals or maturity/investment scores.

7. Test fresh and repeated imports, full-row equality, immutable conflicts,
   failure after earlier writes, extension/event failure rollback, migration
   retry, FK integrity, unknowns, target-date lineage and subject coverage.
   Run backend, OpenAPI/type drift, build and browser checks. Verify both dossiers,
   source links, filters, exports, keyboard/mobile behaviour and withheld claims.
   Use disposable databases; back up and compare original rows before any real
   local import. Do not report unexecuted checks as passing.

Deliver working code, documented import/dry-run/run commands, a mapping/loss
report and an updated engineering_completion.md listing exact changes, executed
checks, unresolved decisions and limitations. Demonstrate both dossier views.
Fresh-install/CI, human relevance judgments, broad inventory imports and saved
new-venture intake are separate stages; do not present them as completed here.
```

Completion means the two dossiers can be inspected in the local UI with correct uncertainty and exported provenance; their graph can be dry-run/imported safely on a disposable database. Human identity acceptance can remain pending if clearly represented and excluded from accepted results.

## Prompt 2 — add a new venture and compare it

Use after Prompt 1. Give Codex the current project, the same research package and the completion report from Prompt 1.

```text
Continue VEE in /Users/kevinnn.park/Documents/venture_evidence_explorer.
Read the preceding integration implementation, its completion report and the
research 0.2.1 contract before editing. Implement a local “Add venture” workflow
through working UI, storage, comparison and verification. Preserve user changes.

Provide a form for venture/project name, aliases, description and optional
source-backed evidence. Missing business facts must remain unknown. Show possible
identity duplicates and allow a draft to remain unresolved. Retain source URLs,
dates/precision, attribution and review disposition for every sourced claim.

Distinguish user-entered assertions from publisher evidence. If the current
contract cannot represent that distinction, extend it explicitly and version the
change; never relabel user input as a publisher report or human-accepted fact.

Let a saved draft supply a comparison query against the existing eligible corpus
without automatically inserting its assertions as trusted retrieval evidence.
For sourced imported ventures, reuse the reviewed adapter/projection and current
exploration versus accepted-only eligibility. Explain which fields contributed,
which evidence was missing and why results were returned or withheld. Exclude
the same resolved subject and make unresolved identity limitations visible.

Add a comparison-table row for the new venture with its evidence/missingness and
clear draft/review status. Preserve saved input across reloads. Handle validation
failures without partial records or silent data loss. No external AI service is
required; reuse deterministic retrieval and existing local conventions.

Verify create/save/reopen, duplicate warnings, missing fields, invalid source/date
inputs, persistence failure, comparison/exclusion and accepted-only safeguards.
Run relevant backend, type/build and browser checks. Update documentation and
engineering_completion.md, separating implemented behaviour from human decisions
and empirical relevance work still pending. Keep everything local.
```

## Prompt 3 — prepare the historical discovery/review pipeline

Use after the pilot. In addition to the current project and research package, provide:

```text
/Users/kevinnn.park/Documents/Codex/2026-11-17/read-code-agent-handover-md-and-3/outputs/research/expanded-discovery
```

```text
Extend the current local VEE with a reviewable pipeline for the existing expanded
discovery inventory. Read Discovery_pack.json, Expanded_research_list.md and
Validation_record.json at the supplied expanded-discovery path, plus the current
adapter and research contract. Inspect its actual schema before mapping fields.

The inventory contains 274 name-normalized leads across 27 source families; it is
not 274 accepted unique NZ ventures or a complete population since 2000. Keep
discovery staging separate from accepted venture/evidence tables and counts.

Implement stable discovery IDs and lineage, alias/identity candidate review,
dated NZ inclusion evidence, investor/programme relationships and unresolved
states. Preserve overlapping cohorts and historic outcomes. Do not merge on
name alone, interpret a current portfolio as a full historical record, or turn
missing updates into failure. If the inventory cannot supply a field, leave it
unknown and report the gap rather than inventing a default.

Provide queue/search/filter views by source family, candidate status, period and
evidence gap. Provide explicit duplicate/mapping previews and promotion dry runs
through the research adapter. Promotion requires the relevant source/identity
checks and real decision records; merely appearing in a portfolio is discovery
evidence. Import only into staging for this milestone.

Verify inventory totals, repeat staging import, alias conflicts, overlapping
relationships, date/missingness handling, promotion refusal, transactional
rollback and export/reconciliation. Demonstrate with a bounded sample and report
exact staged versus accepted counts. Do not claim newly completed external
research or national coverage. Keep work local and update the completion report.
```

## Prompt 4 — prepare honest relevance evaluation

Can follow Prompt 1; it does not depend on importing all discovery leads. Provide current `evaluation/queries.json`, `evaluation/judgments.csv`, `docs/evaluation_plan.md`, `docs/academic_extensions.md`, current code and the pilot completion report.

```text
Implement the next evaluation milestone in the current local VEE. Inspect the
existing evaluation runner and development tasks first. Preserve blank human
judgments and existing B0 golden results. Do not treat synthetic results as
empirical relevance evidence.

Create a frozen-corpus/task manifest with hashes, evidence/method versions and
separate development/held-out task IDs. Provide a review workflow or export for
real human grades, rationales and evidence references. Record reviewer identity,
role/independence and disagreements without inventing reviewers or decisions.

Specify task-specific inclusion criteria for closer alternatives and plausible
distractors beyond RosterLab and QuickMas. Reuse available sourced profiles where
they qualify; produce an explicit evidence-gap list where more research is needed.
Two contrasting dossiers alone are not a relevance benchmark.

Validate judgment completeness and compute graded retrieval metrics, coverage,
abstention and appropriate uncertainty only where the supplied real labels allow
them. Compare methods on identical eligible corpora and tasks. Leave metrics null
with an explicit pending reason when judgments are missing. Add an analyst
task-time/usefulness recording template without manufacturing observations.

Measure query counts separately from end-to-end latency, disclosing digest/run
costs, corpus size and environment. Test leakage, malformed judgments, incomplete
labels, reproducibility and refusal to produce unsupported metrics. Deliver the
working evaluation tooling, protocol, blank review materials, executed checks
and a clear list of research/human input still required. Keep everything local.
```

## Prompt 5 — fresh-install and release reproducibility

Use before treating the integrated pilot as a reproducible release. Provide the current project, lockfiles, `.github/workflows/checks.yml` and the latest completion report.

```text
Verify the current VEE release from a clean disposable source copy. Keep the
original project, environment and database unchanged. Inspect requirements.lock.txt,
frontend/package-lock.json and .github/workflows/checks.yml. Do not update locked
versions merely to obtain a green run or reuse installed dependencies while
describing the result as a fresh installation.

Create a new Python environment, install the locked Python dependencies, run
npm ci in the disposable frontend and install the configured browser as needed.
Run fresh bootstrap/integrity, migration failure/retry, backend tests, OpenAPI/type
drift, build and browser checks, including the newly implemented pilot workflows.
Use disposable databases and record exact commands/runtime/dependency versions.

Run available local CI-equivalent environments where practical. Verify configured
Python versions and Linux bundled Chromium only where actually executable here;
otherwise list those checks explicitly as unexecuted. A configured workflow is
not an executed CI result. If network/runtime access blocks a check, preserve the
failure evidence and complete independent checks without inventing a pass.

Fix application defects revealed by these checks with focused regressions, then
rerun affected checks. Deliver a release verification record, source manifest,
recovery/run instructions and a completion report distinguishing actual passes,
environmental blockers and remaining research/human-evaluation work. No push,
remote CI trigger, deployment or paid service is part of this request.
```

## What to request back after each stage

Ask for: changed files and rationale; exact run/import commands; before/after preservation results; executed tests and failures; screenshots or a local demonstration; mapping/loss report where relevant; implemented versus pending functionality; and the next concrete blocker. A completion report is a record to review, not a replacement for the source and executable checks.

The first handover should be **Prompt 1 plus the current project and framework 0.2.1**. The national-history pipeline and evaluation prompts are subsequent bounded tasks, not an instruction to complete every future extension in one pass.
