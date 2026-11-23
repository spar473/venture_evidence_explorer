# Time Machine: retrospective backtest preregistration

Registered 22 November 2026, before any Time Machine scoring, selection, ablation or sensitivity run. Baseline application: `0b7e5d839553768c479639adc7717cb6cbd91672`. The original brief is preserved separately in `docs/healthtech-pilot/TIME_MACHINE_PROMPT.md`; this specification resolves its timing and evaluation ambiguities.

This is a retrospective, known-outcome demonstration. Partly, Supie and Halter were chosen with their outcomes already known. Freezing this protocol prevents subsequent tuning on these cases; it does not make the sample blind, representative or an independent predictive validation. No rates, probabilities, calibration claim or investment recommendation will be displayed.

## 1. Frozen subjects and population

| Subject | Cohort ID | Entry interval | Role |
|---|---|---|---|
| Partly | `public_partly` | 2020-10-08 | Main case |
| Supie | `public_supie` | 2021-11-09 | Closure case |
| Halter | `discovery_halter` | 2016-12-01 through 2016-12-31 | Stretch; abstention is acceptable |

Use the accepted population under `nz-first-institutional-seed:1` from the checked-in cohort entry evidence. Freeze the baseline input digests in the Phase 1 coverage report. Do not add companies because of their outcomes. Report additions, identity corrections and anchor corrections separately, with sources and dated amendments.

The subject's historical cutoff is the **earliest** day of its entry interval. A peer is temporally eligible only if its **latest** possible entry day is strictly before that cutoff. Exclude the subject, aliases of the subject and unresolved identity links. Unknown peer outcomes do not exclude peers from feature coverage or similarity ranking. Report the full eligible denominator and every exclusion.

## 2. Evidence clocks and review

- **Strict, default:** each subject and peer feature must have a qualifying source-version witness, publication date when known and effective date when applicable on or before that venture's earliest possible entry day. Each peer feature must also be public by the subject cutoff. A peer's later development must not rewrite its entry snapshot.
- **Lenient, separately labelled:** only offering, buyer and market descriptors may fill a missing peer field within 90 calendar days of the peer's earliest entry day, capped at the subject cutoff. This does not admit later stage achievements, rounds, team milestones or funding context. Strict values take priority. The subject remains strict. Every admitted late feature records its delay. Lenient evidence cannot pass the Phase 1 strict gate.
- **Historical peer events:** default `as_of_anchor` applies the subject cutoff to event occurrence, publication and witness, and to the information used to select ceiling/typical/floor. Filtering a timeline after choosing roles using future outcomes is prohibited.
- **Hindsight:** `today` may expose subsequently verified peer events up to the frozen data cutoff, initially 2026-11-21. Flag every post-subject-cutoff addition and label the entire mode as hindsight. Do not use it as the primary validation result.
- **Reveal:** post-entry subject events belong only in the separate reveal block. They are absent from the snapshot, IDF corpus, peer ranking and role selection. The frontend must not render the reveal until requested.
- **Witness standard:** reuse `Witness.check_source`. A current company, portfolio or register page with an old event date cannot become a `publisher_dated` witness. A dated original news article or release must identify its dated version; a later revision moves the available date unless an earlier archived version is actually inspected. An archive requires a real capture URL, UTC timestamp and matching passage. Search snippets, URL dates and uninspected CDX listings do not establish a feature.
- **Extraction review:** AI may propose field/value/source/witness/passage/locator records. New proposals remain `proposed` until a human confirms them. Only confirmed, undisputed features count toward the gate or enter scoring. Record a named reviewer and review date; do not invent review actions. Existing accepted packets are not silently promoted into a new scope.

Missing means missing. Never infer a negative milestone, paid customer, full-time employment or priced round from silence, an award, a founder biography or an investor's presence.

## 3. Frozen general similarity profile

Version: `general-gower-b1:1`. Keep `witnessed-gower-b0:3`, its thresholds and its payloads unchanged.

| Dimension | Weight | Fields |
|---|---:|---|
| Product and customer | 0.35 | `description`, `product_type`, `buyer`, `business_model` |
| Market | 0.15 | `sector_normalised`, `market_focus` |
| Stage evidence | 0.30 | `prototype`, `paid_pilot_or_revenue`, `full_time_team` |
| Funding context | 0.20 | `round_size_band`, `lead_investor_type`, `months_since_founding` |

These are design choices, not fitted or validated weights. Within a dimension, average only fields observed on both sides. Overall similarity is the weighted mean over dimensions with a defined score. Weighted coverage is the sum of each dimension's weight times its jointly observed fraction, with no renormalisation. Empty descriptions have no score; missing or unknown values do not match each other.

Fixed admission bars: overall similarity **≥ 0.35**, weighted coverage **≥ 0.35**, Product and customer similarity **≥ 0.25**, and at least **five confirmed fields per venture**. Rank qualifying peers by descending similarity then stable cohort ID; retain **k = 12**. Fewer than **three** qualifying peers means abstention. A field is counted once, regardless of the number of citations.

### Vocabulary and normalisation

Use an explicit, versioned vocabulary; retain each raw source phrase and the mapping rationale. Case-fold, trim and collapse whitespace. Resolve only declared aliases and plurals; no blanket trailing-`s` stripping, fuzzy matching or inferred synonyms. Identical known nodes score 1.0. Direct parent/child nodes or siblings with a meaningful shared parent score 0.5. Other pairs score 0.0. A field's artificial root never grants partial credit. An unknown token is missing for vocabulary scoring and is reported for review.

Freeze these families and nodes before scoring:

- `product_type`: software {analytics, workflow, marketplace}; hardware {medical_device, industrial_equipment}; physical_goods {food_beverage, materials}; service {financial_service, professional_service}.
- `buyer`: business {small_business, enterprise}; consumer {individual, household}; public_sector {government, education}; clinician {radiologist, optometrist, general_practitioner, surgeon}. Intended users are not automatically buyers.
- `business_model`: subscription {saas, membership}; transaction {marketplace_commission, retail_margin}; sales {hardware_sale, licensing}; service_fee {professional_fee, pay_per_use}.
- `sector_normalised`: digital {enterprise_software, fintech, retail_ecommerce, media}; science {healthtech, biotech, agritech, cleantech, advanced_materials}; industrial {manufacturing, aerospace, energy}; consumer {food_beverage, consumer_products}. Map raw sector labels with editorial provenance; do not replace raw labels or count a mapping without historical source evidence.
- `market_focus`: geographic {new_zealand, australia_new_zealand, international}. No geography-based partial credit between distinct nodes; this is a flat categorical field, scored by equality.
- `lead_investor_type`: institutional {venture_capital, angel_network, corporate_venture}; other {public_fund, accelerator}. An investor name alone is insufficient evidence for a classification.
- Explicit aliases include radiologists → radiologist, clinicians → clinician, optometrists → optometrist, surgeons → surgeon, SMEs/SMBs → small_business, SaaS → saas, clean technology/cleantech → cleantech, healthtech software/health technology → healthtech. Other additions require a dated amendment and both-version results if scoring has started.

`description` uses the existing tokeniser and symmetric IDF-weighted overlap. Compute IDF over the subject and temporally eligible, sufficiently covered entry snapshots only, before score thresholding; never include reveal text, outcome text, present-day profiles or held-out labels. Record the exact corpus IDs and input digests.

`months_since_founding` uses `max(0, 1 - abs(a-b)/120)` for nonnegative integer months supported by source precision. Imprecise founding dates remain intervals and do not become invented point values. `round_size_band` uses NZD stated in the dated source: <0.5m, 0.5m–<2m, 2m–<5m, 5m–<10m, ≥10m, scoring `1 - abs(index_a-index_b)/4`. Do not use a present-day FX rate to manufacture a historical band. Milestones require explicit yes/no evidence and use equality.

Embeddings are an optional, precomputed local ablation only, replacing the description field score. Never change weights or admission bars for that run. Record model name/revision, model and vector digests, dimensions and cosine transformation `(1 + cosine)/2`. The default stays token overlap. No embedding method is selected or shipped on these known outcomes alone; absent evidence of better semantic matching, report it as not run and ship no runtime network dependency.

## 4. Data gate before implementation

Store the new entry evidence in a separate `research/healthtech-pilot/backtest-snapshots.json`, scope `backtest_entry`, so the existing application packets and b0:3 remain unchanged. Extend validation alongside the existing witness validator. Keep sources, witnesses, raw values, proposed normalisations, field locators and confirmation records inspectable.

**Phase 1 passes only when at least 15 Partly-eligible peers each have at least five confirmed strict entry fields.** Validate the full packet graph and anchor identity. Also report subject coverage, total peers eligible by date, fields per peer, unconfirmed proposals, lenient-only records and exclusions. Coverage is a data audit, not a backtest run.

If the gate is missed, stop before the general scorer, endpoint, backtest or Time Machine UI. Commit the evidence, coverage script and shortfall report. Do not lower the bar, widen the window, backfill values from later sources or claim the feature is implemented. A documented data shortfall is a valid result.

## 5. Roles, horizons and evaluation

Use the existing top-k ceiling/typical/floor selection semantics: highest resolved rank, lowest resolved rank with closure at the floor, and unused peer nearest the lower median, with similarity and ID tie breaks. A single resolved rank yields a representative, not an invented range; no resolved outcomes yields abstention. All role evidence must satisfy the selected historical clock. Peer ages may differ at the subject cutoff; show that age rather than implying equal follow-up.

The subject reveal uses the frozen cohort primary status within **36 calendar months of subject entry**, with existing interval and competing-event rules. Each peer's 36-month classification uses **its own** entry clock. Where a primary result is not yet knowable at the subject cutoff, retain censoring/unknown; do not treat it as no outcome. Show events on an aligned entry clock with their dated sources, plus the subject-date cutoff. A global reveal beyond 36 months must be separated from the scored horizon.

Prespecified report fields, per case and mode:

1. Eligible and covered peer IDs, admitted/ranked IDs, role selections or exact abstention, scores, coverage, timestamps and provenance digests.
2. **Span hit**, descriptive only: compare the subject's verified status rank by its 36-month horizon with the default historical ceiling/floor ranks. Use the existing status ladder (closure 0, quiet/lost 1, operating on seed 2, Series A 3, Series B+ 4, exit/IPO 5). No subject status rank, missing either role, representative-only output or unresolved competing-event order means **not evaluable**, not a hit or a miss. Quiet/lost is not a verified 36-month operating result. This ordinal span is not a calibrated interval.
3. **Typical-status hit:** equality of subject and typical peer's frozen 36-month **primary** status, only when both are resolved and the peer's full horizon was observable at the subject cutoff. Unknown, lost, incomplete follow-up or no typical role means not evaluable. Report the comparison's denominator explicitly.

Run strict/as-of-anchor first. Keep lenient and hindsight results separate. Leave-one-company-out uses every sufficiently covered cohort entry with a resolved 36-month primary status, while excluding that company and its linked identity from its own peer universe. Preserve temporal eligibility for every fold. Do not describe this small, incomplete, selected population as external validation.

## 6. Frozen robustness checks

- Ablations: exact categorical matching versus the declared vocabulary; token descriptions versus an explicitly recorded optional embedding model. Keep the corpus, source clocks, population, k and bars fixed. Report changed peer IDs and roles, including abstentions; do not select a winner by the known case outcomes.
- Sensitivity: for each of four dimensions, separately add or subtract **0.05**, then proportionally renormalise the other three weights to keep the sum at one. Run eight perturbations against the same baseline. Report each role's changed ID, representative/abstention transitions and the number of comparisons evaluable. Do not quietly omit abstentions.
- Leakage tests: entry interval ordering, feature/publication/witness cutoffs, lenient cap at subject date, as-of filtering before role selection, reveal separation, future descriptions excluded from IDF, mutable-page old dates rejected and b0:3 golden payloads unchanged.

## 7. Amendment and run records

Before the first scoring run, record this preregistration's commit ID, baseline input digests, vocabulary version and execution environment. Every result records its own input digests and configuration. Thresholds, fields, vocabulary, weights, subject anchors, outcome definitions and hit rules cannot change after that first run without an appended dated amendment, rationale and retention of the original results. Fixes to code that violated the frozen specification must retain affected run records and describe the defect.

No Time Machine scoring run has been performed at registration. Phase 0 does not validate the weights or promise that Phase 1 can pass.

## Amendment 1, 23 November 2026: provisional preview on AI-adjudicated evidence

**Decision by the project owner (Kevin Park).** To see the Time Machine working before the evidence is complete, the owner has chosen to build and run a clearly labelled **provisional preview**. This amendment records that choice. It does not change the strict rules above; it adds a second, separately labelled track.

**How the fields were decided.**

1. *First reading:* the proposals in `backtest-snapshots.json` (packet SHA-256 `380d9c5217434639db0f466aeed69ed5652ecbd5a6c59de2fe79ff493d0f6bbf`), written by Codex.
2. *Blind second reading:* on 22 November 2026, a separate Claude agent re-extracted 53 priority fields from the cited sources without access to the packet or review file. It could read the 7 live sources. It could not read any web.archive.org capture or the AUT ISBS PDF, so 21 archive-based fields (all of Parcelport, First AML and Myovolt, plus 3 VidApp fields) have no independent reading.
3. *Adjudication:* on 23 November 2026, Codex chose a final decision for all 72 fields (61 Accept, 7 Correct, 3 Unsure, 1 Reject).
4. *Human review:* **not performed.** No field in this track is human-confirmed.

Decisions: `research/healthtech-pilot/backtest-review-decisions.csv`. Each row records the decision, any corrected value, whether a blind second reading exists and whether it matched, `decided_by = codex`, `review_kind = ai_adjudicated` and `human_confirmed = no`.

**Rules for the preview track.**

- Fields with `Accept` or `Correct` count as **AI-adjudicated**, a review state distinct from `confirmed`. `Unsure` stays proposed and `Reject` is excluded.
- The strict Phase 1 gate (15 peers with five human-confirmed fields) is unchanged and still **not passed**. With AI-adjudicated fields, 9 Partly-eligible peers reach five fields.
- The preview may run the frozen `general-gower-b1:1` scorer, the backtest endpoint and the Time Machine page with fewer than 15 peers. Weights, vocabulary, admission bars, k, subjects, anchors, clocks and hit rules stay exactly as frozen above.
- Every preview output, API response and screen is labelled **"Provisional preview: AI-adjudicated evidence, not human-confirmed; strict evidence gate not passed."** Preview results are stored separately and are **not** the preregistered first scoring run.
- Any field can be changed later by editing the decisions file and re-running the ingest and audit. After preview results exist, a change to a decision is recorded with its date, and the earlier preview results are kept.

**Known limits at the time of this amendment.** Partly has no qualifying subject evidence, so its case abstains. Supie has 6 AI-adjudicated subject fields and is the only subject that can be scored. Halter has no qualifying evidence. One open inconsistency: Parcelport's sector note says merchants use free software and pay for freight, which conflicts with `product_type = workflow` (accepted).
