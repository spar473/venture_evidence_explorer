# Implementation note — research interchange 0.2.1

18 November 2026, Pacific/Auckland. Ready to begin the bounded integration pilot in `Implementation_TODOs.md`. **Not a compatible application import and not an implemented research adapter.**

The pasted reviewer feedback was assessed as review material. Its request to push code does not override the user's local-only constraint. Delivery stays local, including a source-review ZIP. No original application/data files were edited. Existing implementation changes belong to the separate engineering work and are preserved.

## Completed in this revision

The four reported validator gaps were reproduced against 0.2, then fixed in 0.2.1: target-date lineage/precision, typed review targets, raw chronology with an external validation date, and explicit required subject coverage. The source dossiers retain their evidence, unknowns, unresolved identity links and zero accepted records. No new venture/source research was performed in this revision; source-reading statements carried forward from 0.2 refer to that earlier pass.

The local app and engineering completion report were found and inspected. An isolated source copy passed bootstrap/integrity, 59 backend tests (two version-specific skips), migration rollback/retry, API-type drift, frontend build and 13 browser tests. Exact scope and limits are in `Local_Code_Review_Record.md`. The engineering report is supplied separately as an attributed report; its every claim was not rerun.

## Current contract and overlap

| Inspected app facility | Integration consequence |
|---|---|
| Strict integer input versions 1 and 2; immutable full-row equality | Research `format_version: "0.2.1"` needs its own adapter. Validation-only app probe rejects it as expected. Never feed it directly to bootstrap. |
| Six seed arrays: sources, ventures, observations, awards, connections, annotations | Explicit mappings needed for subjects/parties/events/reports/unknowns/readiness/cases. Preserve unsupported fields in a loss report and original packet. |
| Version-2 historical dates, typed financial/event values; `evidence_dates`, `observation_values`, `source_availability`, `observation_relations`, `import_documents` | Reuse where semantically compatible. Convert precision to calendar intervals, never guessed days. Avoid competing date stores. |
| Publisher-report observations, review history and shared evidence policies | Preserve claim nature, speaker relationship, source version and review lineage. Source-checking does not satisfy accepted-only retrieval. |
| Awards plus per-observation event values | These do not supply a general event-identity/report graph. Keep unresolved financing candidates out of totals/distinct-round counts. |
| Same-subject UoA connections and annotation evidence | Buyer/payer/procurement relations must not become UoA connections. Cross-subject proposals need a bridge or explicitly limited projection. |
| Existing review events target observations/annotations | Research identity/event/report/readiness acceptance needs deliberate audit mapping. No human decisions may be fabricated. |
| B0 uses sourced `product_description` and `uoa_connection` | New fields are not automatically ranking features. Preserve golden results and policy/corpus versions until evaluated. |
| Summary directory, full profiles, run provenance/replay, CSV exports and modular UI | Extend existing surfaces. Research dossier UI and saved new-venture intake remain planned work. |

Inspection covered ingestion/database/contracts/evidence-policy/retrieval/run code, migrations, tests, scripts, frontend and CI workflow. `Application_Source_Manifest.json` anchors the exact reviewed snapshot. No local `.git` metadata was found, so use source hashes, not an assumed Git HEAD. No fresh GitHub-state claim is made.

## Boundaries

RosterLab and QuickMas links remain proposed at the brand/project level; legal identity remains separately unknown. Existing IDs with matching labels are candidates, not accepted mappings. A named adopter or advertised integration does not establish payment, procurement authority or completed integration. The 2025 launch target remains a target; financing reports remain possibly duplicate.

The 274-entry discovery inventory remains unchanged and unimported: name-normalized leads, not a verified NZ venture population since 2000. This revision establishes neither relevance/time savings nor programme/investment outcomes. See the ordered acceptance gates and deferred extensions in `Implementation_TODOs.md`.
