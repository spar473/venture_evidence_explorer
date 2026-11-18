# VEE implementation TODOs after final research review

Updated 18 November 2026, Pacific/Auckland. Supplements the app's broad `NEXT_STEPS.md` with a bounded first integration milestone. Keep the existing local application and user edits; do not rebuild from the starter or import the inventory wholesale. No push/deployment is requested.

## Completion ledger

| Work | State / evidence |
|---|---|
| Directory, evidence inspection, programme filters, explainable B0 comparison, analytical exports | Existing local functionality. Isolated-code verification is in `Local_Code_Review_Record.md`. |
| Engineering contracts, historical values, run provenance, evaluation scaffolds | Existing code; relevant tests rerun. The supplied engineering report contains wider implementation claims and limits. |
| Atomic research evidence, separate users/buyers/payers, events/reports, missingness and question readiness | Delivered research contract and two dossiers; not yet app functionality. |
| Four reviewer validator findings | Fixed in 0.2.1: 32 rejection cases and four permitted counterexamples pass. Original 0.2 retained. |
| Independent factual acceptance | Pending; source checks are assistant extraction checks. Zero human acceptance events. |
| Identity mappings, research adapter, research dossier UI | Pending pilot gates below. |
| Relevance/usefulness, clean-install CI, realistic performance | Pending evidence; no empirical success claim from synthetic demonstrations or query counts. |

## Ordered pilot gates

- [x] **P0 — close validator findings.** Match event/report/observation target values and precision; type review targets; check raw chronology against preparation and an external date; enforce `required_subject_ids` and conclusion coverage. Retain valid future targets and limited one-subject conclusions. Package tests with schema and examples.
- [ ] **P1 — record brand/project mappings separately from legal identity.** Review `subj_rosterlab → v_rosterlab` and `subj_quickmas → v_quickmas` against source/seed context, aliases, scope and conflicting matches. Record actual decision actor/date/evidence/rationale/scope. Do not infer registration numbers, legal continuity or contracting parties. A brand/project mapping may be resolved while legal identity stays unknown. Leave unresolved mappings quarantined; owner acceptance must be a genuine decision.
- [ ] **P2 — transactional adapter with dry run.** Use a distinct research-version discriminator and additive migrations; preserve applied checksums. Validate the graph before writes. Account for every collection/field as mapped, preserved research-only, quarantined or unsupported. Reject silent loss and immutable-ID conflicts. Retain original bytes/hash, namespaces, provenance and review lineage; reuse existing historical date/value structures. Keep unresolved events inspectable but excluded from aggregates and accepted-only features. Atomicity covers the entire graph and import ledger.
- [ ] **P2 verification — preservation and failure cases.** Test fresh disposable DB, repeat import/full-row equality, changed-byte/semantic conflicts, failure after a source insert, failure during extension/event writes, migration rollback/retry and caller-transaction refusal. Verify foreign keys and no partial writes. Before an actual authorized import, back up SQLite and compare every original data/review row afterwards. Repeat imports must add no duplicate evidence, reports or acceptances. Unsupported payloads must fail without writes.
- [ ] **P3 — display both dossiers and analytical views.** Show atomic claims, speaker/source responsibility, access/version, date precision, targets versus occurrences, reported events and unresolved cases. Display supported and withheld conclusions per question. Keep currency/payer/procurement/integration/legal gaps visible. Financing candidates must not inflate totals. Export stable IDs, provenance, precision, review disposition and missingness without invented zeros/dates. Verify links, filters, CSV contents, keyboard/mobile behaviour and withheld conclusions in browser tests.
- [ ] **P4 — real-task evaluation.** Add sourced closer alternatives and plausible distractors; RosterLab and QuickMas alone test schema contrasts, not retrieval relevance. Separate development and held-out questions; freeze corpus, evidence policy and method. Collect real task-specific human grades/rationales/evidence IDs, disclose independence and report disagreements. Keep missing judgments null. Compare B0 and any proposed projection on identical eligibility/corpus. Report abstention, coverage, graded retrieval metrics and uncertainty only when labels support them. Measure source-finding time/usefulness in an analyst case study before claiming gains.
- [ ] **P5 — reproducible release checks.** Execute fresh lockfile installation, backend CI matrix, migration checks, OpenAPI drift, build and bundled Linux Chromium tests. The workflow exists; local tests with installed macOS dependencies do not establish CI success. Preserve logs and snapshot hashes. Remain local unless the user separately changes that constraint.

P1/P2 unblock a reviewed data pilot; P3 completes the inspectable demonstration. P4/P5 gate claims about usefulness and portable reproducibility. Do not expand the dataset merely to improve an unmeasured headline count.

## Performance and verification

Record SELECT counts **and** end-to-end median/p95 latency, corpus size, hardware/runtime, warm/cold state and inclusion of digest/run construction. The engineering report shows tiny-corpus comparison latency increased despite fewer SELECTs. Do not advertise speed gains from query counts. Profile realistic larger corpora before digest caching or retrieval changes; preserve snapshot consistency and replay guarantees.

Classify claims as implemented, verified here, reported elsewhere, scaffolded or deferred. Synthetic E1/E2/E3 work does not demonstrate empirical gains. Blank relevance judgments remain blank.

## Extensions after the bounded pilot

- **New-venture intake:** validate a new subject and evidence, show identity conflicts and unsupported fields in dry run, retain provenance/genuine reviews, then expose its accepted projection to comparison. Free-text comparison already works; saved new-venture intake remains unimplemented.
- **NZ history since 2000:** use the 27-family discovery inventory beyond the initially named investors. Deduplicate aliases, define dated NZ inclusion criteria, follow historic/outcome sources and retain stale/inaccessible records. Current portfolios cannot reconstruct historic populations or failed ventures. Preserve overlapping university/investor/programme cohorts.
- **Venture visualisations:** evidence timelines with precision/target styling and visible coverage, plus comparable tables with clear denominators. No universal maturity/investment score from sparse evidence.
- Archive/availability witnesses, review UI, evaluated structured similarity, Power BI and PostgreSQL remain separately scoped. Deep-tech diligence, MCDA and sequential decisions remain deferred until a defensible case and contract exist.

## Next coding-session instruction

Read this file, `Implementation_Note.md`, `Research_Interchange_Contract.md`, `Validation_Record.json` and current app docs. Check snapshot drift; run bootstrap/integrity on a disposable copy. Begin with P1 and the P2 dry-run adapter, carrying work through P3 verification. Do not treat research JSON as app input version 2, invent acceptance, overwrite user changes or silently change B0. Record unresolved decisions and unsupported fields explicitly.
