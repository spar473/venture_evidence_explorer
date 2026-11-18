# Comparison research framework and five first-pass dossiers

Prepared 18 November 2026, Pacific/Auckland. Draft v0.1, following the supplied brainstorm feedback.

**Review conclusion:** the feedback is substantially right. The 274-entry inventory supports discovery, but most entries cannot yet support substantive comparisons. The next research milestone should deepen a small, varied cohort using explicit field definitions and real investigation questions. Broad inventory research remains useful as a queue; it should not be mistaken for completed profiles.

This document tests that approach on AgriPhage, QuickMas, Alimetry, RosterLab and Tracksuit. These are **completed first research passes with explicit gaps**, not complete company profiles or independently accepted comparison records. Application code/data and earlier research packs have not been changed. No MCDA assessments or relevance judgments have been created.

## 1. What to retain and refine from the feedback

| Recommendation | Review and refinement |
|---|---|
| Descriptive evidence before scoring | Retain. Separate what is reported about a venture from whether it performs well against an objective. Similarity must not become investment attractiveness. |
| Problem, solution, users, technology and business model | Retain, but split user, beneficiary, paying organisation, procurement authority and channel. A doctor using a product is not proof that doctor controls its budget. |
| Commercialisation pathway | Retain as the distinctive research direction. Collect actual requirements and events; do not assign a universal pathway or maturity score from sector labels. |
| Five diverse cases, then about 20 | Retain as a practical sequence, not proof of generalisation or a fixed sample-size requirement. This pilot covers two early university projects, a clinical device, workforce software and marketing software. It is still a purposive, non-representative selection. |
| Research infrastructure is ready | Qualify. A queue and inspection tools have a useful purpose now; a production schema/import still needs definitions, identity reconciliation and validation against the app contract. The research JSON is not directly importable. |
| Five completed dossiers | Define completion as a documented research pass, including unknowns, source limits and next actions. It does not mean every field is known, every publisher claim is true, or a reviewer accepted the dossier. |
| Structured comparisons | Require evidence for the specific question. A venture can support a product comparison while lacking the buyer or deployment evidence needed for a pathway comparison. |

The source document is feedback to assess, not a new set of commands automatically overriding the user's research-first, local-only scope.

## 2. Field dictionary for the next research pass

Definitions below are proposed research conventions. Store multiple dated observations rather than flattening changing descriptions into one timeless company row.

| Dimension / field | Meaning | Minimum acceptable basis / common mistake |
|---|---|---|
| `identity.subject` | The particular venture/project, product, brand or legal entity being described | Subject-linked source and stable research ID. Preserve entity uncertainty and explicit former names. |
| `identity.nz_connection` | Documented NZ research origin, founding or substantive historical activity | Specific dated evidence. An NZ investor's global portfolio membership alone is insufficient. |
| `problem` | The task, unmet need or cost the source says is addressed | Attribute the statement. A pitch's problem estimate is not a validated market-size result. |
| `solution` | What the product or proposed intervention does | Preserve intended versus offered versus demonstrated wording. |
| `alternative` | The existing process/product the source explicitly compares with | Record source and time; do not call it the only or current alternative. |
| `beneficiary` | Who/what is intended to benefit | Separate from user and buyer; a patient or animal may benefit without purchasing. |
| `user_role` | Who directly operates, interprets or uses the product | Explicit role evidence; distinguish intended users from documented users. |
| `paying_organisation` | Organisation reported to pay, or the explicitly targeted customer segment | Record whether targeted or contracted. Targeted hospitals are not a verified paying customer list. |
| `procurement_authority` | Role/team documented as authorising the purchase | Do not infer from a testimonial, title, user role or industry. |
| `market_geography` | Geography of a target market, reported use, sale or regulatory permission | Keep relationship type and date. Permission to market is not evidence of a sale. |
| `technology` | Source-supported technical mechanism/modality | Describe function without promoting marketing superiority claims to technical validation. |
| `research_origin` | Documented research institution and translation relationship | Keep research origin, founders' education, licensing and investment distinct. |
| `business_model` | Publicly described offering and charging arrangement | Distinguish proposed model, advertised offer and actual paid contract. Device architecture alone does not establish a hardware-plus-consumables revenue model. |
| `price_basis` | Unit, billing interval, scope, geography, currency and date | Preserve unspecified currency; an advertised price is not realised revenue or contract value. |
| `validation_requirement` | A requirement explicitly documented by an authoritative or project-specific source | General analyst expectations remain hypotheses until sourced; no sector-based automatic compliance labels. |
| `regulatory_record` | Specific product, jurisdiction, identifier, decision and date | Record clearance/approval/registration precisely; do not extend scope across versions or jurisdictions. |
| `manufacturing_requirement` | Documented materials, production, quality or scale-up requirement | Unknown unless supported; hardware does not prove a particular supply-chain constraint. |
| `integration_requirement` | Documented workflow, IT, physical or organisational integration | Separate advertised API availability from evidence of a completed integration. |
| `distribution_channel` | Documented sales, reseller, referral or deployment route | A partnership announcement does not establish sales volume or exclusive rights. |
| `development_event` | A dated prototype, test, study, pilot, deployment or other development occurrence | Capture event type, subject, setting and what occurred. Prototype testing does not establish field trial or commercial launch. |
| `commercial_event` | Customer agreement, deployment, paid sale, revenue or renewal report | Keep each distinct; paid status and amount stay unknown unless explicit. |
| `financing_event` | Financing report with event date precision, scope, instrument/round and named parties | Keep raw amount/currency, qualifiers and investor roles. Awards and research grants are not venture financing rounds. |
| `community_relationship` | Award, participation, incubation, research connection or support relationship | Record the relationship actually supported; being encouraged to join a programme is not participation. |
| `outcome` | Specific sourced acquisition, asset sale, listing, closure or other outcome | Distinguish event date from publication and legal completion; absence from a portfolio is not closure. |

### Required metadata on each sourced observation

Use: research subject ID; field; original paraphrase; source ID/URL; issuer and publisher; passage/page locator; publication/update/retrieval dates separately; event or effective time and precision; geography/product scope where relevant; claim nature; extraction/review state; and conflicts or limits.

Suggested **claim nature** values are `entrant_proposal`, `intention_or_target`, `advertised_offering`, `publisher_reported_occurrence` and `official_record`. These are nominal descriptions, not a ladder of commercial maturity or confidence. An event's type and completion state need their own fields.

Keep extraction and acceptance separate. An assistant can record `source_read; acceptance_pending`; it cannot invent owner or independent reviewer acceptance. Retain reviewer decisions and rationale later as separate records. Repeated articles quoting the same release are not independent confirmations.

For missing data, use null plus a reason such as `not_stated_in_inspected_sources`, `not_researched_this_pass`, `source_unavailable`, `conflicting`, `identity_unresolved` or `not_applicable_with_reason`. A bounded search failing to find something does not prove it is not publicly available. Do not replace missing values with zero/false or a negative assessment.

Date rules: preserve year/month precision, distinguish occurrence from “known by publication,” keep future targets prospective, and do not infer historical availability from today's retrieval. Live undated pages describe what was observed now, not what the company offered in 2021.

## 3. Event distinctions that must survive extraction

Use separate types for prototype reported; laboratory study; field trial; clinical study; pilot announced; pilot started; pilot completed; customer agreement announced; deployment reported; paid sale reported; renewal reported; regulatory determination; financing announced; financing closed; and future target.

These types should not automatically imply one another. A laboratory study is not a field trial, a customer name is not proof of payment, and a regulatory determination is not a generic traction tick. Record counts for each type separately. Do not calculate a universal maturity score from them.

For a future milestone table, retain `actual_or_target`, `event_date`, `date_precision`, `date_basis`, `announcement_date`, `paid_status`, `subject/product`, `setting`, `source_id` and `review_state`. Future target dates can be after the research cutoff; completed-event dates cannot be silently drawn from those targets.

## 4. Five first-pass research dossiers

Source references S01–S12 below were opened/read for this pass on 18 November 2026. Full pages were not archived and cached/rewritten web text is possible. The prior funding pack is referenced separately where not freshly re-audited. All dossiers remain `source_read; acceptance_pending`; legal-entity matching remains unresolved.

### A. AgriPhage — Ideas Challenge proposal

Proposed app link: `v_agriphage`; no update or merge performed. Reason for selection: an early-stage proposal where limited detail must remain limited.

| Field | Research result |
|---|---|
| Problem / solution / technology | Entrant proposes a bacteriophage-based alternative to livestock antibiotics. Safety and effectiveness language is the entrant's claim, not established performance. [S01] |
| Users / buyers | Livestock application is stated; operator, paying organisation and procurement role are not specified. [S01] |
| Development / community | Listed among the 2025 Ideas Challenge winners; the article dates the ceremony to 22 May 2025. This establishes recognition, not a prototype, animal trial or sale. [S01] |
| Model / pathway / financing | Charging model, regulatory route, manufacturing, delivery channel and financing are not stated in the inspected entry. |
| Identity / current status | University programme subject is identifiable; legal entity, company domain and current operation are unverified. |

**Useful now:** investigate proposed livestock intervention and university recognition. **Insufficient for:** buyer, demonstrated animal outcomes, commercialisation readiness or investment comparisons.

**Next research action:** find subject-specific university/team research outputs or a clearly matched project/company source. Do not attach results from an identically named product merely because its name matches. The source labels these entries as entrant summary statements; that provenance needs to remain visible.

### B. QuickMas — $100K recipient and diagnostic prototype

Proposed app link: `v_quickmas`; no update or merge performed. Reason for selection: distinguish demonstrated development activity from planned launch.

| Field | Research result |
|---|---|
| Problem / solution | Mastitis-related decisions for dairy cattle; proposed on-farm milk testing using sample-processing equipment and cartridges. [S02] |
| Users / alternative | Dairy farmers are intended users. A founder contrasts the proposal with slower, connected testing. These are attributed claims, not an independent product benchmark. [S02] |
| Development event | UoA reports prototypes being tested as of publication, 17 October 2024. Exact start date, setting, sample size and performance results are not supplied. [S02] |
| Target, kept prospective | The team planned partnerships/investment and a 2025 market launch. This pass does not establish that launch occurred. [S02] |
| Community / origin | First place in the 2024 Velocity $100K Challenge; team spans Liggins, ABI and Engineering. [S02] |
| Unknowns | Paying organisation, procurement authority, revenue model, validated performance, regulatory path, manufacturing and current operation. |

**Useful now:** compare a diagnostic proposal with AgriPhage's therapeutic proposal, including what each source actually establishes. **Insufficient for:** comparative accuracy, treatment efficacy, completed field validation or current commercial stage.

**Next research action:** find dated prototype/test reports and subsequent project updates; preserve the 2025 launch as a target until a separate occurrence source is found. This pass checked the university story and bounded university-domain search, not every public source.

### C. Alimetry — clinical device and regulatory evidence

Proposed app link: `v_alimetry`; existing research ID `cand_alimetry`. Reason for selection: separate product architecture, clinical users, formal regulation and commercial assumptions.

| Field | Research result |
|---|---|
| Solution / technology | System combines a skin electrode array, reader, app and clinician reports for gastric electrical activity. The FDA-hosted summary identifies healthcare-facility use. [S04] |
| Users / workflow | Company addresses GI clinicians and practices; offers onboarding, in-service education and billing-team support. Procurement authority and contract payer are not established. [S03] |
| Regulatory event | FDA record K240946 names Gastric Alimetry and Alimetry Ltd.; decision is substantially equivalent, dated **3 July 2024**. Associated letter identifies a Class II device. This is a specific determination, not a blanket approval or proof of commercial success. [S04, S05] |
| Business model / manufacturing | Reusable/single-use components do not establish how contracts are priced. Commercial terms, manufacturing arrangements and unit economics remain unknown. |
| Clinical outcomes | A company evidence page lists studies, but this pass did not complete a paper-level methodological assessment. One attempted PMC paper was access-blocked. No efficacy score is assigned. |
| Financing / origin | Prior pilot contains UoA-origin evidence and conflicting 2024 financing presentations. Those claims are carried by reference, not resolved or freshly re-audited here. [P1] |

**Useful now:** investigate device/workflow and a dated regulatory precedent. **Insufficient for:** actual hospital procurement pathway, paid sales, economic outcomes or comparative clinical performance.

**Next research action:** inspect primary studies with outcomes, methods and conflicts of interest, and seek institution-side procurement/deployment evidence. Current company descriptions do not prove features or reimbursement arrangements existed at an earlier cutoff.

### D. RosterLab — healthcare workforce software

Proposed app link: `v_rosterlab`; discovery ID `discovery_rosterlab`. Reason for selection: a healthcare customer context with a different product, user workflow and evidence burden from a clinical diagnostic device.

| Field | Research result |
|---|---|
| Problem / solution | UoA describes software addressing complex hospital staffing and roster constraints. It reports departmental operation in NZ and Australia by November 2024. Deployment is reported; payment and exact start dates are unspecified. [S06] |
| Users / buyer | Advertised offer addresses scheduling administrators/managers and rostered employees; named contracting and budget-authorising roles are unknown. [S07] |
| Model / price basis | Free digital plan, paid AI rostering advertised at **$20 per rostered person/month**, and custom enterprise offering. Selected page does not explicitly give currency. This is an observed offer, not realised revenue. [S07] |
| Integration | Enterprise offer lists SSO, API access and integrations. That does not establish a specific completed hospital integration. [S07] |
| Origin / community | UoA links the concept to PhD research, Velocity and Venture Lab. [S06] |
| Financing report | UoA reports a recent $1.75m seed round led by Movac with Pacific Channel and UniServices. Currency and exact closing date are not explicit. [S06] |
| Unknowns | Procurement process, paid deployment terms, independently measured performance and current legal/operating status. |

**Useful now:** compare advertised B2B pricing units with Tracksuit and identify reported healthcare deployment. **Insufficient for:** claiming it faced the same purchasing, regulatory or integration challenges as Alimetry.

**Next research action:** obtain named institution-side implementation evidence and timeline, including which systems/interfaces were involved. Do not treat vendor ROI claims as demonstrated benefits for this project or for every customer.

### E. Tracksuit — marketing software and agency channel

Existing research ID `cand_tracksuit`; discovery ID `discovery_tracksuit`; no accepted app identity match. Reason for selection: test the dictionary beyond university/agricultural/clinical cases.

| Field | Research result |
|---|---|
| Problem / solution / technology | Company describes ongoing survey-based brand measurement delivered through a dashboard, addressing marketers' difficulty explaining brand investment. [S08] |
| Users / buying roles | Company addresses CMOs, brand managers and insights leads. These are target roles, not proof of contract-signing authority. [S08] |
| Model / channel | Agency hub advertises annual per-brand pricing and referral arrangements. Separate brand customers, agency users, referral partners and the party paying the contract. [S09] |
| Implementation | Agency FAQ describes category/competitor selection, surveys and dashboard setup. This is the advertised process, not a verified implementation for a particular customer. [S09] |
| Historical customers / financing | February 2024 company announcement names customers and an AUD20.5m Series A. This is a company report, not independently verified payment or investment-return evidence. [S10] |
| Prospective product change | A page says the next chapter will be revealed in January 2027. Planned features are not marked as already released at this November 2026 cutoff. [S11] |
| Unknowns | Customer-specific procurement, payment/renewal dates, realised pricing and independently validated customer outcomes. |

**Useful now:** compare advertised charging units and channels with RosterLab while keeping the different markets explicit. **Insufficient for:** judging investment attractiveness or attributing customer growth to use of the software.

**Next research action:** inspect methodology and customer-side implementation evidence; reconcile different regional/currency presentations before comparing money. Keep earlier pricing/features separate from the live offer observed today.

## 5. Test the fields against actual investigation questions

These are proposed development questions and analyst assessments, not independent relevance labels or measured retrieval results.

| Investigation | What this pass can support | Still missing / appropriate abstention |
|---|---|---|
| How do AgriPhage and QuickMas address livestock antibiotic-related problems differently? | Attributed intervention versus diagnostic descriptions and different types of development evidence. | Comparative safety, efficacy, cost and substitution claims. |
| Who faced similar hospital purchasing and integration challenges? | Alimetry and RosterLab are candidates for further investigation. | Actual purchasing processes, authority, integrations, dates and obstacles. Do not claim the similarity is established. |
| How do the publicly offered charging units differ between two B2B tools? | RosterLab per-rostered-person/month versus Tracksuit per-brand/year. | Currency/contract scope and realised pricing; no like-for-like cost or unit-economics comparison. |
| What was demonstrated by the time QuickMas received recognition? | Prototype testing reported in the award story. | A 2025 target is not evidence of launch, field trial completion or paid sale. |
| Which venture has regulatory evidence relevant to a clinical device pathway? | Alimetry's specific FDA record and product architecture. | Not a general ranking of all five ventures or advice that the same route applies to another product. |
| How long did each take from first financing to first paid customer? | The question identifies needed fields. | First paid-sale dates and comparable financing histories are absent; no elapsed-time chart is justified. |

**Pilot learning:** the proposed dimensions are useful, but even a named customer and advertised integration are insufficient to answer the hospital-purchasing example. The next 15 cases should be selected partly to fill that evidence gap, rather than chosen only for well-known names or large raises.

## 6. Readiness and next research sequence

Readiness should be a record for a question/mode and evidence cutoff, with supported fields, unresolved conflicts and a reason for withholding a conclusion. It should not be a universal green tick for a company.

Suggested stages are discovery; source-backed description; question-specific evidence assembled; and independently reviewed for that question. These describe research workflow, not venture maturity. None of these dossiers has been independently accepted or assigned investment/relevance scores.

Before expanding to approximately 20 dossiers:

1. Refine the draft dictionary using this pilot, especially buyer roles, event semantics and time-varying offers. Preserve open decisions rather than treating the brainstorm's recommendation as owner approval of every field.
2. Resolve subject/identity matches and seek the highest-impact missing primary evidence. Prioritise original test reports, institution-side implementations, contracts disclosed publicly, regulator records and dated company histories. Contacting people would require separate authorisation; no contact was made.
3. Add other sectors, non-UoA origins, older ventures and exited/closed cases. This small cohort does not solve the 2000–2010 coverage gap.
4. Define review tasks and several fresh comparison questions before choosing scoring rules. Analyst-authored dossiers and angles must not become both features and ground-truth evaluation labels.
5. Produce the local implementation contract after the fields have been exercised: identity links, typed observations/events, null reasons, review history, import refusal rules and query-specific evidence display.

Useful future visuals are source-linked timelines, side-by-side field tables and missing-evidence panels. A funding-versus-time chart needs reconciled currencies/scope; a maturity radar or success league table is unsupported by these records.

## 7. Source register and access record

All S sources were accessed 18 November 2026. Publication dates are listed only where observed. No historical page-availability proof or full-page archive was created. The FDA database and associated letter are related records, not two independent confirmations. The university award story and its entrant statement are also not independent sources.

| ID | Source, date and locator | Scope / limit |
|---|---|---|
| S01 | [UoA Ideas winners](https://www.auckland.ac.nz/en/news/2025/05/23/2025-velocity-ideas-challenge-winners.html), 23 May 2025; ceremony paragraph and AgriPhage entry under entrant summaries | Recognition and entrant proposal; no performance validation. |
| S02 | [UoA QuickMas story](https://www.auckland.ac.nz/en/news/2024/10/17/innovating-until-the-cows-come-home.html), 17 October 2024; QuickMas/prototype/launch paragraphs | Publisher report and founder statements; prototypes and targets kept distinct. |
| S03 | [Alimetry for clinicians](https://www.alimetry.com/for-clinicians); undated live page; clinician roles and Alimetry in Your Practice | Company descriptions and implementation offer; no independent outcome appraisal. |
| S04 | [FDA-hosted K240946 letter/summary](https://www.accessdata.fda.gov/cdrh_docs/pdf24/K240946.pdf); letter 3 July 2024; PDF pages 1, 5–6 | Letter plus applicant's technical summary; summary prepared 5 April is not decision date. |
| S05 | [FDA 510(k) record](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPMN/pmn.cfm?ID=K240946); decision field 07/03/2024 | Decision date confirmed by the July 3 letter. Page update is not the event date. |
| S06 | [UoA RosterLab story](https://www.auckland.ac.nz/en/news/2024/11/27/rosterlab-levels-support-healthcare-workers.html), 27 November 2024; opening, financing and research-origin paragraphs | Publisher/quoted-company reports, not customer-contract verification. |
| S07 | [RosterLab pricing](https://rosterlab.com/pricing); undated live page; plans and pricing FAQ | Advertised offer; currency not explicit. |
| S08 | [Tracksuit about](https://www.gotracksuit.com/uk/about); undated live UK presentation; problem, target roles and product | Company positioning; no claim of independent effectiveness. |
| S09 | [Tracksuit agency hub](https://www.gotracksuit.com/agencies/hub); undated live page; partner/pricing/setup FAQs | Channel and offering descriptions; no actual contract/payment verification. |
| S10 | [Tracksuit Series A report](https://www.gotracksuit.com/au/blog/posts/raise-announcement-series-a), 28 February 2024; financing, customer and NZ paragraphs | Company report; locale variants remain one possible event. |
| S11 | [Tracksuit next chapter](https://www.gotracksuit.com/whats-next); undated live page; January 2027 reveal and planned features | Prospective content as of research cutoff. |
| S12 | [RosterLab about](https://rosterlab.com/about); undated live page; research-origin section | Supplementary identity/origin context; timeline year placement is not used to infer exact dates. |
| P1 | Prior local `outputs/research/batch-01/Research_pack_01.json`, prepared 17 November 2026 | Previously researched origin/funding context; unresolved claims retained, not freshly re-audited in this pass. |

Access gap: the attempted [PMC study page](https://pmc.ncbi.nlm.nih.gov/articles/PMC11719321/) returned a browser/reCAPTCHA check. It was not admitted as a fully read clinical study or used to assign performance claims. No access control was bypassed.

The original 274-entry inventory and earlier counts are unchanged. Alimetry, RosterLab and Tracksuit already appear there; AgriPhage and QuickMas come from the original application sample and are absent from that inventory. This worksheet does not update the inventory or announce a reconciled union total. Identity reconciliation is still required before any union/count or import. The Markdown framework is a draft research worksheet, not an application import file.
