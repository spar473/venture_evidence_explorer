# Venture Evidence Explorer comparison framework v0.2.1

Prepared 18 November 2026, Pacific/Auckland. Research draft for implementation review; not an accepted analytical feature set.

The purpose is to find venture precedents worth investigating, identify which conclusions the evidence supports, and expose differences and gaps. Investment attractiveness, success prediction and founder-quality assessment remain outside scope.

This revision builds on `Comparison_Framework_and_Five_Dossiers_v0.1.md`. It replaces the combined buyer field, separates claim metadata into independent dimensions, makes observations atomic, separates event candidates from reports, and demonstrates explainable readiness on two dossiers. This research work did not edit the original application/database, previous research packs or 274-entry inventory. External application changes were observed during the earlier v0.2 work. This revision verifies an isolated code copy; see the current preservation record for snapshot drift.

## 1. Six different customer and user relationships

| Field | Definition | What it must not imply |
|---|---|---|
| `target_customer_segment` | Segment the venture explicitly intends to serve or sells its advertised offering to | A named contract, payment or budget owner |
| `intended_beneficiary` | Person/group/animal intended to benefit | User or buyer identity, or demonstrated benefit |
| `intended_user` | Role expected to operate/use/interpret the proposed or advertised product | Actual adoption, payment or purchasing authority |
| `documented_user` | A source reports actual use/adoption by a role or named unit | Independently verified deployment, payment or integration completion |
| `named_customer_organisation` | An explicitly named organisation/unit described as a customer/adopter; preserve the exact relationship asserted | Legal contracting party or reported payer |
| `reported_paying_organisation` | An organisation explicitly reported to have paid for a specified product/transaction | Procurement authority, amount or recurring revenue unless separately stated |
| `procurement_budget_authority` | Role/organisation explicitly identified as authorising a particular purchase or controlling its budget | Inferred authority from job title, testimonial or clinical seniority |

Intended and documented user are alternatives within one relationship family, so the table has seven fields for the six requested distinctions. Store multiple observations if a venture has different users, markets or channels. A unit such as a hospital department can be named without inventing a registered entity or contracting authority.

## 2. Other descriptive dimensions

| Dimension | Research fields / boundary |
|---|---|
| Identity and NZ connection | Stable research subject, product/brand/project scope, proposed existing-app link, legal-entity uncertainty, dated NZ-origin/activity evidence. Alias or same-name matching is not acceptance. |
| Problem, solution and alternative | Source-attributed need, product/proposed intervention and explicitly described alternative. Preserve intended versus demonstrated function. The example does not attempt an exhaustive competitor taxonomy. |
| Technology and origin | Technical mechanism/modality and research-origin relationship. Education, research origin, licensing, incubation and investment remain distinct. |
| Business model and price | Proposed or advertised charging arrangement versus executed contract. Amount, raw currency status, unit, interval and plan/product scope stay together as one offer when they share source/time/status. |
| Commercialisation pathway | Separately sourced validation, regulation, manufacturing, integration, distribution and geography. Analyst expectations are proposed questions, not automatic sector requirements. |
| Development and commercial history | Prototype, test, study, pilot, adoption, integration, customer agreement, paid sale and renewal are distinct event kinds/states. |
| Financing | Round total, investor cheque, instrument/round label, participant role and reported vehicle label are separate observations when their meaning differs. Fund labels do not establish legal vehicle identity. |
| University/community | Awards, participation, incubation and research connections. An invitation, eligibility or future place is not completed participation. |
| Outcomes | Share acquisition, asset acquisition, listing or closure with event/source semantics. No update is not failure. |

The machine-readable example is deliberately narrower than the full research domain. The accompanying contract documents which fields this schema accepts; additional concepts must receive defined fields and a versioned schema change rather than being silently squeezed into an unrelated field.

## 3. Independent claim dimensions

| Dimension | Values in the research contract | Interpretation |
|---|---|---|
| Assertion nature | `proposal`, `intention_target`, `advertised_offering`, `reported_occurrence` | What kind of assertion is made; not how authoritative it is |
| Source relationship | `entrant`, `company`, `university`, `customer`, `regulator`, `investor`, `project_team`, `other_identified` | Who is responsible for that passage/claim; `speaker_context` explains quoted or embedded material |
| Review state | `extracted`, `source_checked`, `accepted`, `disputed` | Processing/review disposition, with actor and rationale; source check is not independent acceptance |
| Event state | `announced`, `started`, `completed`, `cancelled`, `unknown` | State asserted for the event candidate, supported by linked report(s); not a universal maturity label |

Publisher role is also recorded on the source. It can differ from the claim's source relationship. In QuickMas's university article, team plans are attributed to the project team while the award report is attributed to the university. Likewise, in a regulator-hosted PDF, the official determination belongs to the regulator and applicant-authored technical statements belong to the company. Hosting alone does not confer regulator authority on every passage.

There are no automatic authority weights, confidence percentages or scores. Corroboration requires inspecting whether reports actually have independent origins. This packet has zero accepted records and no human review events. Proposed annotations are neither accepted facts nor independent relevance judgments.

## 4. Atomic observations and explicit unknowns

One observation represents one proposition with consistent subject, source, time basis, scope, nature and attribution. Split propositions when any of these differ. RosterLab's round total and Movac's own cheque are separate; SSO, API access and integrations are separate offerings. Intended customers, named adopters and payers never share one overloaded field.

Each observation retains:

- Stable observation/subject IDs, field and original paraphrase.
- Source ID and passage locator, with issuer/publisher context and source relationship.
- Effective, source-context and target times separately, including precision and basis.
- Product/geographical scope, related named party where applicable, optional typed money, conflicts and limitations.
- Review state, actor, date and an acceptance reference only if a real acceptance event exists.

Publication/update/retrieval dates live on source records. Source-context date means the publication context or date the live offer was inspected; it is not an event date or proof of historical availability. Source versions were not archived.

Unknown business facts live in explicit `unknowns` records with null value, reason, scope, inspected sources and access gaps. Null identity/date/currency cells likewise retain a reason. Empty geography arrays mean unspecified geography, with a reason—not worldwide scope. Missing reasons distinguish not stated in inspected sources, not researched, unavailable source, conflict, identity uncertainty, non-applicability and occurrence not established. None means zero or false. A bounded source check cannot establish that no public evidence exists anywhere.

## 5. Real-world event candidates and reports

`events` identifies a putative real-world occurrence or target. `event_reports` records a particular source's report of that event, linking its atomic observations. One event can have many reports; one document can report several events. Event state/date is a source-based research projection with its basis reports, not independently verified truth.

Do not merge event candidates automatically on name, date, amount or round label. The example leaves the UoA and Movac financing reports as two possible representations of one round, linked by an open reconciliation case. They are not two established rounds and must not be summed. Following actual reconciliation, preserve both reports, an auditable identity decision and the original candidate history.

Keep targets prospective. QuickMas's 2025 launch target has year precision, an unknown occurrence time and an announced-intention state. The year passing does not establish launch, failure or cancellation. A later occurrence source should create a separately evidenced event/report and an explicit relationship/reconciliation decision. Never overwrite the historical plan to make a timeline look complete.

Prototype testing reported as underway supports a reported `started` state, but not its start day, test setting, accuracy or field-trial completion. An adoption report supports neither an executed purchase nor a completed IT integration unless those claims have their own evidence.

## 6. Question-specific readiness

Each readiness record identifies a question, mode, subject set and evidence cutoff, and records:

1. Required evidence and its supported, partial, missing or unresolved/disputed disposition.
2. Supporting observation IDs, explicit unknowns and open cases.
3. Supported conclusions, each with observation and source lineage.
4. Conclusions that must be withheld.
5. Review state and the assessment rationale.

The examples use a **research-as-of cutoff**, not a historical backtest. A report published in 2024 but inspected now is not automatically known to have been available unchanged in 2024. Historical comparison requires a separate availability/capture policy.

| Task | What can remain useful despite gaps | Reason to withhold a stronger conclusion |
|---|---|---|
| Describe different proposed/offered solutions | Attributed solution/user contrasts | No evidence of relative effectiveness or investment value |
| Describe advertised charging units | State an offering with plan/unit/interval and currency gaps | Missing counterpart offer, currency, tax/scope or executed terms prevents cost comparison |
| Investigate a regulatory precedent | A specific product/jurisdiction/decision/date record | No generic requirement or approval inferred from sector |
| Compare actual purchasing/implementation journeys | Named reports can identify further candidates | Actual payer, authority, contract and completed interfaces may still be unknown |
| Measure financing-to-paid-sale elapsed time | Identify required dates and unresolved event identities | No elapsed-time calculation with missing dates or first-sale evidence |

A question can have limited supported conclusions while its main purchasing or causal conclusion remains withheld. `limited_conclusions_supported` is not a readiness score or approval badge. Questions and analyst interpretations remain proposals; they do not become ground-truth relevance labels.

## 7. What the two examples show

The JSON contains two subject identities with proposed links to `v_rosterlab` and `v_quickmas`; 34 atomic observations; six event candidates and six reports; 21 explicit unknowns; two proposed annotations; six readiness records; three open reconciliation/identity cases; and two access gaps. Six source records include one blocked institution page; no observation cites it as read evidence.

During the earlier v0.2 source-reading pass, RosterLab's live pricing and integration claims were reopened. University and investor financing reports were separately read. A vendor report names departmental adoption; the linked Health NZ page returned 403, and the linked Unitec page was a general homepage rather than the underlying study. These limits remain visible.

During that v0.2 pass, QuickMas's university story was reopened. Prototype testing, recognition and a launch target are separate records. No new occurrence, current legal identity, currency, payer, contract or human acceptance was invented.

## 8. Delivery and review boundary

This is a **research interchange package**, not a compatible application import. The app's importer changed during this task and was re-inspected: it now accepts integer input versions 1 and 2, including additive historical dates and typed observation values. Neither is this research format `0.2.1`. Its strict structure and assertion convention still differ, and it has no separate general event/report identity, payer/procurement or question-readiness tables. A guarded validation-only probe rejected this packet. See `Implementation_Note.md` for the inspected contract, overlap and gaps.

Use `Research_Interchange_Contract.md`, `Research_Interchange_v0.2.1.schema.json`, `Two_Dossier_Research_Example.json` and `validate_research_example.py` together. `Validation_Record.json` distinguishes structural/semantic checks from manual source reading and records the concurrent drift. No research record imports, original-app writes, contacts or publication were performed. Tests used disposable application copies/databases.

The package is ready for **the bounded integration pilot** in `Implementation_TODOs.md`. It is not ready for direct ingestion or claims of independently validated comparison quality. Decisions still needed include identity acceptance, event reconciliation, review authority, field expansion, source version capture and how accepted research projects into the app's existing retrieval fields.

## 9. Final review amendments in 0.2.1

The reviewer probes were reproduced against 0.2; they exposed validator gaps, not established errors in the baseline evidence. This revision enforces event → report → observation date/precision lineage, exact review target types, raw chronology and an external validation date, and explicit `required_subject_ids` coverage. A limited RosterLab-only conclusion remains valid in a two-subject question. Version 0.2 is preserved unchanged; strict consumers must adapt the requirement field rename.

The local code and engineering completion report are now available. Bootstrap/integrity, backend/build/browser and targeted migration checks were rerun on an isolated copy; see `Local_Code_Review_Record.md`. The four validator fixes are complete. Identity acceptance, transactional research import, dossier presentation, real relevance evaluation and fresh-install CI remain pending, with acceptance criteria in `Implementation_TODOs.md`. New source research was not undertaken in this patch.
