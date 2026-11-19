# Research interchange 0.2.1 integration pilot

The bundled `research/framework-v0.2.1/` files are exact supplied references, not newly researched facts. Their historical statements about pending app work describe the research author's snapshot. This document describes the implemented adapter. The frozen `application/` copy from the kit was compared with the current source, never extracted over it. All 87 snapshot files matched before work; no local Git metadata exists.

## Distinct import boundary

Research `metadata.format_version: "0.2.1"` is a separate namespace (`research:0.2.1`), not application integer input version 1 or 2. Use `scripts/import_research.py`, not bootstrap, for research packets. The adapter invokes the unchanged supplied JSON Schema and semantic validator, with an external validation-as-of day. It validates the complete graph before data writes. Duplicate JSON keys, non-finite numbers, unknown fields/enums, wrong review target types, orphan/mis-scoped references, chronology and target/report/observation precision mismatches are refused.

The additional locked dependency is JSON Schema validation plus its compatible dependencies. `rfc3986-validator` is explicit so URI `format` checks cannot silently disappear when jsonschema's optional URI checker is absent. The wrapper refuses to start if date or URI validation is unavailable. Existing Python dependencies are not blanket upgraded.

```sh
python scripts/import_research.py --input research/framework-v0.2.1/Two_Dossier_Research_Example.json --db outputs/venture_evidence.sqlite --as-of 2026-11-18 --report outputs/research-dry-run.json
# After taking a SQLite backup; this explicitly writes the local research graph:
python scripts/import_research.py --input research/framework-v0.2.1/Two_Dossier_Research_Example.json --db outputs/venture_evidence.sqlite --as-of 2026-11-18 --apply --report outputs/research-import.json
python scripts/verify_research.py --as-of 2026-11-18
python scripts/export_research.py --db outputs/venture_evidence.sqlite --output-dir outputs/research-exports
```

Without `--apply`, no database is created, migrated or changed. Dry run can inspect an existing app-only database before migration 004. Its report accounts for every leaf, including nulls and empty arrays, plus every collection. Categories are `mapped` (stable graph identity/reference), `preserved_research_only` (losslessly stored without legacy projection), `quarantined` (unresolved external identity or duplicate-event semantics), and `unsupported` (refused). The supplied packet has 2,430 leaf paths: 605 mapped, 1,767 research-only, 58 quarantined and zero unsupported. Those categories describe adapter destinations, not factual acceptance. The report also lists external candidate matches/shared source URLs, missing/conflicting links and immutable-ID conflicts.

## Storage and transaction ownership

Additive migration `004_research_pilot.sql` creates immutable research records/import documents, import membership, graph links, canonical time projections, identity mapping history and decision documents. Existing seed, tables and applied migration files are untouched. Whole raw packets are stored byte-for-byte with SHA-256 and a canonical semantic digest. All 92 top-level records and 17 nested requirements/conclusions are stored with stable editorial IDs and typed reference links. Namespacing prevents research IDs from being mistaken for app venture/source IDs.

Historical dates reuse the application's `HistoricalDate` interval validation. New namespaced time projections are necessary because the existing immutable `evidence_dates` owner contract only supports legacy source/observation/award IDs. Raw research time, precision, basis and missing reason remain intact. Calendar bounds are query bounds, not invented occurrence days. Money scope/currency/unit/interval and speaker/source responsibility are preserved exactly; no incompatible legacy financial or publisher-report assertion is manufactured.

Schema preparation is the explicit migration boundary. The entire research graph, raw packet, membership, links, time values, mapping proposals/decisions and research import ledger then share one `BEGIN IMMEDIATE` transaction. Failures roll back all of those writes. Migration failure rolls back that migration and its ledger entry; earlier applied migrations remain committed. An active caller transaction is refused, and caller connection configuration is restored. Explicit SQL COMMIT/ROLLBACK avoids Python autocommit-default assumptions.

Exact repeat imports produce full-row equality. If only whitespace/order formatting changes, a new raw-byte document and membership are retained, while semantic records, links, time values and mappings remain unchanged. Reusing an editorial ID with changed semantic content is refused; supply genuinely new version IDs and explicit history instead. Original raw import bytes/hashes are never replaced. Success reporting uses the already validated bytes and actual connection, not a second read of a file that might change during import.

## Identity and review

The two app links remain proposed at brand/project scope. Same name and shared source URLs are candidate evidence, not owner acceptance, legal identity or contracting-party identity. Missing external targets remain quarantined without inventing an app venture or blocking the independent research subject. Dossiers work under `subj_rosterlab` and `subj_quickmas`.

An optional `--mapping-decisions FILE` accepts a distinct strict `identity-mappings:1` sidecar. A genuine decision needs `mapping_id`, `subject_id`, `venture_id`, state (`resolved` or `rejected`), `scope: brand_project_only`, an owner/independent-reviewer role and actual actor ID, decision date, subject-correct evidence IDs, rationale and `supersedes_mapping_id`. The raw decision document/hash and predecessor remain stored. Missing actors, assistant resolutions, legal scopes, future/predecessor-inconsistent dates and unrelated evidence are refused. The software checks representation and lineage; it cannot authenticate a human.

No real resolution was supplied, so this pilot creates only two proposed mapping records with null decision actors/dates. Resolution tests use explicitly synthetic actors in disposable databases only. A resolved brand/project mapping never changes legal identity, original proposals/cases, source review or factual acceptance. Current mapping state and source-proposal state are displayed separately. No accepted feature projection is enabled in this pilot.

## Evidence and comparison boundary

The original app corpus still has ten ventures and twenty observations. No research row becomes a B0 `product_description`, UoA connection, award or accepted feature. Golden scores, result ordering and selected baseline observation eligibility remain unchanged. The existing comparison-run digest conservatively hashes all user tables: migration 004 and research imports therefore invalidate earlier run digests even when B0 scores remain identical. Retain the pre-import database backup and matching code to replay those earlier runs; no digest or method behavior was silently changed.

RosterLab's two financing candidates remain possibly duplicate and cannot establish two rounds or monetary totals. QuickMas's 2025 target retains year precision, unknown occurrence and an announced-intention state. Adoption does not establish payer, procurement authority, executed contract or completed integration. Source checks are assistant extraction checks, not factual acceptance or independent relevance judgments. Supported readiness conclusions remain scoped/attributed, and stronger conclusions remain withheld. Research-as-of is not historical web availability.

## Dossiers, exports and verification

Use **Research dossiers** in the existing local UI. Search/filter, open RosterLab or QuickMas, inspect atomic claims, source versions, targets/events, question-specific supported/withheld conclusions, explicit unknowns, cases and access gaps. Evidence links reveal counterpart context required by shared questions. Native dialogs retain Escape, focus return and narrow-screen behavior. No data is imported automatically at API startup.

CSV endpoints and `scripts/export_research.py` provide sixteen grains: the twelve collections plus requirements, conclusions, identity mappings and time projections. Stable IDs, source/packet lineage, assertion/speaker roles, review disposition, precise/unknown dates and missingness reasons are retained. `record_json` preserves each unflattened record. Source packet JSON download returns exact original bytes; subject reference views are explicitly not standalone import packets. There are no synthesized zeros, financial totals, distinct-round counts or maturity/investment scores. CSVs are generated outputs, never a second editable master.

`tests/test_research_import.py`, `tests/test_research_api.py`, `scripts/verify_research.py` and `frontend/e2e/research.spec.ts` verify the pilot. Synthetic source mutations, failures and actor decisions are confined to temporary fixtures. Existing backend/B0/UI tests remain active. See the current root `engineering_completion.md` for actual executed counts/commands, preservation records and limits. Configured CI, fresh installations, real relevance evaluation, discovery ingestion and saved new-venture intake remain subsequent milestones, not claimed complete here.

## Mapping chronology correction · 18 November 2026

A decision must not predate any cited source inspection or relevant evidence assessment/review. This applies to indirect citations as well as direct sources. The adapter follows observations → sources, reports → sources/observations, events → state-basis reports, conclusions → basis observations/sources, requirements/readiness → supporting records, unknowns → inspected sources, proposed annotations → basis observations, and reconciliation cases → reports/events/observations. Nested requirements/conclusions inherit their enclosing readiness cutoff/review day. Actual referenced acceptance events contribute their review day, with cycle protection through target links.

Every cited item must resolve to an inspected source. A source-less subject name, party assertion or failed-access record cannot alone support either a resolution or rejection; cite the actual source-backed basis. Subject/scope checks still apply. These are necessary chronology/provenance checks, not authentication of the actor or proof that the evidence warrants the decision. Shared requirement subject coverage is recognized explicitly. Brand/project scope remains separate from legal identity.

Only exact inspection/assessment/review dates constrain the decision day. Publication/event intervals, unknown occurrence dates and future target years are not promoted to invented inspection dates or upper-bound deadlines. All original raw partial dates remain intact. Invalid decisions/batches are rejected before graph/mapping writes; a rejected sidecar leaves mapping documents, decisions and research import rows unchanged. Applied migration files and existing decisions are not rewritten.

## Healthtech packets · 19 November 2026

`research/healthtech-pilot/packet.json`, `extension.json` and `clinical-studies.json` use the unchanged research 0.2.1 contract and adapter. Each is independently valid. Reused Formus reference records keep identical stable IDs and semantic content across packets; membership/raw bytes preserve both inputs, while graph rows remain unique. New external application IDs are proposals only and missing targets stay quarantined. Existing Formus and IVF base IDs are proposed correspondences, never automatically resolved identities.

```sh
python scripts/import_research.py --input research/healthtech-pilot/packet.json --db /tmp/healthtech-demo.sqlite --as-of 2026-11-19 --report /tmp/healthtech-dry-run.json
python scripts/import_research.py --input research/healthtech-pilot/packet.json --db /tmp/healthtech-demo.sqlite --as-of 2026-11-19 --apply --report /tmp/healthtech-import.json
# Repeat with extension.json for the remaining projects and Toku.
# Repeat with clinical-studies.json for Wellumio and Alimetry.
```

Use a disposable bootstrapped database; `python scripts/healthtech_demo.py` prepares and verifies one without touching any existing database. See the [pilot guide](healthtech-pilot/README.md). The editorial comparison manifest is not an import packet or a new evidence namespace. It selects existing question-readiness records for display without projecting features into B0. Historical availability remains unrepresentable under 0.2.1, so these comparisons explicitly abstain in historical mode. Adding archive support requires a separately versioned, validated contract; no boolean or publication date is treated as an archive witness.
