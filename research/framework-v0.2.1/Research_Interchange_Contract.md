# Research interchange contract 0.2.1

Status: research draft, 18 November 2026. JSON Schema dialect: Draft 2020-12. Local schema ID: `urn:vee:research-interchange:0.2.1`; it does not designate a hosted service.

The authoritative structural definition is `Research_Interchange_v0.2.1.schema.json`. Cross-record rules are implemented by `validate_research_example.py`. Neither file is an application migration or importer. This packet is not compatible with the app's inspected integer schema-version-1/2 input contracts. Research version `0.2.1` is a separate namespace.

Metadata preservation flags refer to **this research task's actions on the user's original application**, as stated by `modification_scope`. `concurrent_application_changes_observed` retains the earlier v0.2 observation of external changes. This revision tests an isolated application copy; it does not write to the original app/database. Inventory and original-app preservation checks are recorded separately.

Version 0.2.1 supersedes 0.2 for integration planning. It deliberately renames requirement `subject_ids` to `required_subject_ids`; strict 0.2 consumers must adapt. Other subject sets keep `subject_ids`. This is a research contract revision, not an app schema version or a compatibility promise. Original 0.2 artifacts remain unchanged.

## Collections and grain

| Collection | Grain / key | Principal references |
|---|---|---|
| `subjects` | One research venture/project/brand, `subject_id` | Proposed app ID is an external unresolved link, not an accepted FK or instruction to merge |
| `parties` | One named organisation brand/unit, `party_id` | No invented legal entities or payer implications |
| `sources` | One inspected research source version/reference, `source_id` | Publisher role, access status and source dates; fresh captures need new version IDs rather than mutation |
| `observations` | One atomic source-attributed proposition, `observation_id` | Subject, source, optional named party and reconciliation cases |
| `events` | One event/target identity candidate, `event_id` | Subject and state-basis reports; identity may remain unresolved |
| `event_reports` | One source report concerning one event candidate, `report_id` | Event, subject, source and observations from that source/subject/attribution |
| `unknowns` | One bounded missing fact, `unknown_id` | Subject, inspected sources and optional access gaps; value is null |
| `proposed_annotations` | One analyst interpretation/question, `annotation_id` | Subjects and source observations; never accepted factual evidence |
| `readiness` | One question/mode/cutoff/subject-set assessment, `readiness_id` | Requirements, observations, unknowns, cases and supported conclusions |
| `reconciliation_cases` | One open identity/event/scope question, `case_id` | Subjects, event candidates and observations; aggregation prohibited while open |
| `access_gaps` | One failed/insufficient retrieval, `gap_id` | Subjects, URL, retrieval date, limitation and claims it cannot establish |
| `review_events` | One actual owner/independent-reviewer decision, `review_event_id` | Typed target, decision, reviewer role/date/rationale; empty in the example |

Keys are stable editorial identifiers, not array positions, display names or guessed registration numbers. IDs must be unique across the packet, including nested requirement and conclusion IDs. Existing earlier pack IDs are not silently reassigned. A later accepted identity decision should record a mapping/history rather than overwrite the original source subject.

The two dossiers are normalised graph views rooted at `subj_rosterlab` and `subj_quickmas`. Select records by `subject_id` or membership in `subject_ids`, then follow their references. Sources and cross-subject questions are shared instead of duplicated in nested dossier objects.

## Independent metadata dimensions

`assertion_nature`: proposal; intention/target; advertised offering; reported occurrence. `source_relationship`: entrant, company, university, customer, regulator, investor, project team, or another explicitly identified role. `review.state`: extracted, source-checked, accepted or disputed. `event_state`: announced, started, completed, cancelled or unknown.

These fields have independent meanings and no numerical authority/confidence weighting. A publisher's role belongs on its source; the responsibility for a quotation or embedded applicant statement belongs on the observation/report. `speaker_context` explains that distinction. Regulator hosting does not reattribute an applicant's technical claims to the regulator. A customer statement does not prove payment or budget authority.

An assistant's source check has actor role `assistant` and no acceptance reference. Acceptance requires an actual owner/independent-reviewer event for the same target, an identified reviewer and an acceptance-capable actor. Acceptance by the owner is not automatically independent review, factual truth or a relevance judgment. The example has no accepted records or review events.

`target_type` selects an exact collection: subject, observation, event, event_report, unknown, readiness or nested conclusion. An ID from another collection is invalid even if it exists globally. Accepted projections must link an acceptance event with the same target type, ID and reviewer role. Validation checks the supplied representation; it cannot authenticate a reviewer or prove a real human decision occurred.

## Field namespace

The schema accepts these research fields:

```text
problem, solution, alternative, technology, nz_connection, research_origin,
target_customer_segment, intended_beneficiary, intended_user, documented_user,
named_customer_organisation, reported_paying_organisation, procurement_budget_authority,
business_model, advertised_price, contract_terms, integration_offering,
completed_integration, prototype_testing, launch_target, commercial_launch, paid_sale,
financing_amount, financing_round_label, investor_cheque, investor_role,
investment_vehicle_label, award_recognition, programme_participation, incubation,
regulatory_record, validation_requirement, manufacturing_requirement,
distribution_channel, market_geography, outcome
```

Version 0.2.1's executable example contract intentionally supports only its defined field and event enums. Additional study/event kinds require definitions and a schema version change before a packet can use them. Unknown fact paths can be more specific than an observation field, e.g. `advertised_price.currency`.

Split claims when source, subject, time, scope, nature or speaker differ. A price's amount/unit/interval/currency status form one offer with one plan/time context; round total and investor cheque are different propositions and monetary scopes. Store only original concise paraphrases and locators, not full copyrighted pages.

## Time, money and missing data

Time objects have `value`, `precision`, `basis` and `unknown_reason`. Known precision is day (`YYYY-MM-DD`), month (`YYYY-MM`) or year (`YYYY`). Unknown time has null value, `unknown` precision and an explicit reason. Dates are calendar-validated by the semantic validator.

Sources distinguish publication, update and retrieval. Observations distinguish effective, source-context and target times. Event/report occurrence and target times are separate. Context can be a publication date or the date an undated offer was inspected; it is never automatically the occurrence date. Target times may be future or past. Neither passing a target year nor seeing a source today proves a launch happened or a page was available unchanged historically.

Known event target and occurrence values must match a linked report at the same precision. Known report target/occurrence values must in turn match a cited observation's target/effective time. Future targets are allowed when that represented chain agrees; the validator does not verify the passage itself.

Raw retrieval, review/check, unknown-assessment and readiness-cutoff dates cannot exceed `metadata.prepared_on`. Preparation cannot exceed the external validation-as-of date. Publication/update cannot be definitely after retrieval. Observation/report checks follow source retrieval; unknown assessments follow inspected sources and access attempts. Readiness evidence and unknown assessments must fall within its cutoff. Partial dates use earliest compatible bounds for chronology refusals, without promoting those bounds into actual event dates. Backdated false input remains a source-review problem.

Money objects carry numeric amount, currency as known or explicit null-with-reason, scope, unit, billing interval and qualifier. Unknown currency is not NZD/USD by default. The example has no conversions, monetary totals, individual-return calculations or investment scores. Keep advertised prices apart from contract prices; do not sum candidate financing events or add investor cheques to round totals.

Unknown fact values are null with a reason, explanation, scope and inspected-source references. Supported reason codes are `not_stated_in_inspected_sources`, `not_researched_this_pass`, `source_unavailable`, `conflicting`, `identity_unresolved`, `not_applicable_with_reason`, and `occurrence_not_established`. The validator enforces reason presence, not whether a search was exhaustive. Unspecified geography has an empty list and explicit reason; this is not global coverage. Structural null foreign keys mean no applicable relationship, not a business fact about payment.

## Events and reconciliation

Each event is labelled `source_reported_candidate`. `scenario` separates a target from a reported occurrence. The example's state/date projection is backed by report IDs and retains source uncertainty; `completed` can mean the publisher reported completion, not that legal completion was independently verified.

Target candidates cannot be marked completed or given an occurrence date. For this narrow version, their state is announced or unknown. Later completion/cancellation evidence should be a separately supported report/event and an explicit reconciliation/history decision, preserving the original target. The enum includes cancellation for reported occurrence records, but this example does not exercise cancellation history.

Reports must use observations from the same subject, source document, assertion nature and source relationship. A document containing different speakers must be split into appropriate observations/reports. An event can have multiple reports; the contract does not require one report per event. RosterLab's two financing candidates deliberately remain separate, with a possible-duplicate case; no automatic similarity-based merge is implemented.

## Readiness and traceability

Requirements record a description, explicit `required_subject_ids`, disposition and supporting/missing/unresolved IDs. Supported requirements need observations covering every required subject and no remaining unknown/case references. Partial requirements need evidence and an explicit gap/case. Missing requirements need explicit unknowns; disputed requirements need open cases. An unresolved identity case can make a requirement disputed without declaring a publisher's statement false. Coverage proves represented subject coverage, not that the observations satisfy the information need: that still requires human/source review. Use separate requirements per field and subject where needed.

Every supported conclusion has its own ID, subject set, original summary, source and observation IDs, inference type and review record. Source IDs must exactly equal the sources of its basis observations. A proposed annotation cannot be substituted for a sourced observation. Readiness unions must match their requirement references. Conclusions may concern only the assessed subjects and observations within the recorded research cutoff.

Conclusions need evidence for each declared subject. A question can span two ventures while an explicitly scoped requirement and conclusion cover only RosterLab. The charging-unit example retains this valid partial result and withholds a two-company cost comparison. Removing QuickMas evidence while retaining a supported requirement for both ventures is invalid.

`limited_conclusions_supported` allows useful bounded descriptions while stronger requested conclusions remain withheld. `abstain_on_requested_conclusion` means no supported business conclusion is supplied for that question. Neither is a universal venture readiness score. Review state and rationale are mandatory. The cutoff is research-as-of, not verified historical availability; independent relevance judgment is false in this contract.

## Validation and limits

Run:

```sh
python3 validate_research_example.py --as-of 2026-11-18
```

The validator loads adjacent schema/example files and `regression_cases.py`. It uses Python 3.10+ and `jsonschema` with Draft 2020-12 support; the recorded run used installed version 4.26.0. It opens no application database and performs no import or network request. Schema references are local. Without `--as-of`, it uses the local calendar date. An explicit date makes historical reproduction deliberate; it is not a second field controlled by the packet.

Checks cover strict keys/enums/types, unique IDs, references, subject lineage, read-source eligibility, time/currency/null semantics, target/occurrence separation and lineage, report attribution, open duplicate cases, proposal separation, typed acceptance, raw chronology, required subject coverage and conclusion provenance. The original 14 rejection cases plus 18 new rejection cases and four permitted counterexamples pass. Altered dates/acceptances are in-memory synthetic fixtures; none enter the delivered research data.

Structural validation cannot establish that a paraphrase follows from a passage, that claimed occurrences happened, that an assigned exact date was actually stated, that an unknown is unfindable, or that a comparison is useful. Those require source review and, separately, real independent/usefulness evaluation. The source-reading record and explicit unresolved cases remain necessary even after a schema pass.
