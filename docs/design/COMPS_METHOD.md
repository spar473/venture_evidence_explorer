# Ceiling, typical and floor comps: method

Method v3, 21 November 2026. The comp response records similarity version `witnessed-gower-b0:3` and the selected witness mode. Probabilities remain subject to the release gates in `docs/healthtech-pilot/NEXT_PHASE_PLAN.md`.

## Inspiration and terms

| Term | Meaning here |
|---|---|
| **Player comps (ceiling / floor)** | The NBA scouting format: "best case he becomes X, worst case Y". Named examples that make a range of paths concrete. They are *not* probabilities. |
| **Reference class forecasting** | Predict from the outcomes of a relevant historical group (the "outside view"), not from the subject's own story. |
| **Similarity-based projection** | FiveThirtyEight's CARMELO approach: find the most similar historical players, then project from what happened to them. |
| **Similarity-weighted k-nearest neighbours (k-NN)** | The practical implementation: take the k most similar historical ventures and give closer ones more weight. |

The workbench shows named comps when the witnessed peer set supports them. Probability display requires the corresponding release gate.

## 1. Start the clock (anchor event)

The UI's "Align at" selector chooses the peer stage:

- `first_institutional_round` (default)
- `first_provider_or_clinical_study`
- `first_regulatory_decision`
- `first_paid_customer`

For each peer, the anchor date is the date of that event, with its precision. Partial dates become intervals. Peers without a dated anchor stay visible under "Not alignable". A company subject uses the same event on its own timeline. A university analogy subject uses its witnessed profile at the selected as-of date and can be compared before it has a qualifying anchor. The UI labels this comparison "Subject today vs peers at their <anchor>" and shows the subject cutoff. Trajectories still require a dated event to establish day zero.

## 2. Snapshot at the anchor

Features require a dated **availability witness** under the existing witness contract. For peers and company subjects, the witness, publication when known, and latest possible occurrence when known must be on or before the earliest possible anchor date. For an analogy subject, the same tests use the selected as-of date. Disputed claims are excluded. There are five dimensions:

| Dimension | Example features | Type |
|---|---|---|
| Clinical workflow | modality, clinical user, output type; description text | categorical + text |
| Buyer and sales path | buyer type (hospital, clinic, consumer, pharma), procurement path | categorical |
| Regulatory path | device class, jurisdiction, decision obtained | ordinal / categorical |
| Stage evidence | milestone checklist values (prototype, provider study, submission, paid pilot, full-time team) | Yes / No / ? |
| Funding context | months since founding, round-size band, lead investor type | numeric / categorical |

A missing feature is **missing**, never "No".

**Strict** is the default witness mode. **Contemporaneous** is an optional mode for peer comparison cards, rankings and their evidence and exports. It can fill missing clinical workflow or buyer and sales fields with a qualifying source witnessed within 90 calendar days of the peer's earliest possible anchor date and by the selected as-of date. The source must describe the offering or intended buyer at that stage. Later sales, pilots, clearances, financing and other milestone events leave the anchor snapshot as it was. Strict evidence takes priority for fields it already supports. Each admitted late claim displays `+n days` from the earliest possible anchor date. The subject, estimator, validation snapshots, frozen outcome classifications and release gates use their original cutoffs.

## 3. Similarity

- **Per-dimension similarity** s⁽ᵈ⁾ ∈ [0, 1], using Gower similarity for mixed types. Numeric features use range-normalised absolute difference. Categorical features use a match score. Text uses the B0 symmetric IDF-weighted token overlap over witnessed descriptions.
- Features missing for either venture are excluded from that pair's average. The share of features available is reported as **coverage**.
- **Clinical workflow similarity must be at least 0.25.** The dimension needs comparable evidence and sufficient similarity on its own. The overall similarity minimum of 0.35 and weighted coverage minimum of 0.15 also apply.
- **Overall similarity:** s = Σ_d α_d s⁽ᵈ⁾ / Σ_d α_d, summed over dimensions with coverage. The α weights are fixed in advance and documented, and are tuned later on training vintages only.
- The UI shows the per-dimension breakdown, because a venture can be a strong peer on procurement and a weak one on clinical validation.

### 3.1 Dimension weights (α), as implemented in `witnessed-gower-b0:3`

These are the fixed weights in `backend/precedent_similarity.py` (`DIMENSIONS`). They were set before any outcome was looked at. They have **not** been tuned, because no training vintage has complete follow-up yet. The weights sum to 1.00.

| Dimension | α | Fields | Comparison per field |
|---|---|---|---|
| Clinical workflow | 0.25 | modality, clinical user, output type, description | Categorical exact match (case-insensitive); description uses IDF-weighted token overlap |
| Buyer and sales path | 0.20 | buyer, procurement path, business model | Categorical exact match |
| Regulatory path | 0.15 | regulatory class, jurisdiction, regulatory decision | Regulatory class is numeric (range 2), so 1 − \|a − b\| / 2; the others are exact match |
| Stage evidence | 0.25 | stage, prototype, provider study, submission, paid pilot, full-time team | Exact match. Milestones enter only as an explicit Yes or No, never as an inferred "No" |
| Funding context | 0.15 | months since founding, round size band, lead investor type | Months since founding is numeric (range 120), so 1 − \|a − b\| / 120; the others are exact match |

- **Overall similarity** renormalises over the dimensions that have at least one comparable field: s = Σ α_d s⁽ᵈ⁾ / Σ α_d. A peer that shares only one dimension is therefore scored on that dimension alone. This is why the coverage minimum exists.
- **Weighted coverage** is Σ α_d × (comparable fields in d ÷ fields in d), taken over all five dimensions. It does not renormalise. Its minimum is 0.15.
- **IDF corpus.** Description IDF is computed over the subject plus the eligible, alignable peers in the same request (`corpus_idf`). It is not computed over the whole database. A different peer universe can therefore change text scores slightly.
- **Regulatory class as numeric.** Classes are treated as ordered (0–2), so class 1 against class 2 scores 0.5 rather than 0. This is a deliberate choice. Changing it changes the version string.
- **Thresholds.** The thresholds are clinical workflow ≥ 0.25, overall ≥ 0.35, weighted coverage ≥ 0.15, k = 12 and at least 3 peers for named roles. They are returned with every precedent response (`thresholds`). When the tool abstains, the response also returns up to three `nearest_candidates`. These are peers that share at least one witnessed field but fail a bar, with the per-dimension breakdown and the fields missing on each side. Nearest candidates are never comps, carry no outcome, and do not change the thresholds.

## 4. Peer set

- Top k by similarity (default k = 12), with a minimum similarity and a minimum coverage.
- The ranked list includes any qualifying peers. If fewer than three qualify, the tool abstains from selecting named roles.
- The subject is excluded, and so is any peer whose identity is linked to it.

## 5. Ceiling, typical and floor

Choose only from inside the top-k. **No reaching outside the peer set** for a better story.

- **Outcome ladder as of the requested date** goes from exit or IPO, to Series B+, Series A, operating on seed, lost or quiet, and verified closure. This display ladder uses dated, linked, undisputed evidence available by the cutoff, including events beyond 36 months. Labelled priced equity establishes Series A or B+. A verified terminal event supersedes operating and financing evidence. Where an exit and closure have overlapping date intervals, the order is unresolved. Subsequent ordinary activity leaves the last verified financing rank in place.
- Operating on seed requires a dated operating event on or after institutional entry. A quiet classification requires the nominated activity and a completed, dated follow-up search with at least 18 months since the last verified activity. Its status date is the search cutoff. An operating, financing, exit or closure card uses the relevant event's reported date and precision. Peers without enough evidence for a status stay in the ranked list and are ineligible for cards.
- Ceiling and floor select the highest and lowest resolved ranks. A verified closure takes the floor whenever present. Each rank breaks ties by higher similarity, then stable company ID. The typical card uses the unused peer closest to the lower median outcome rank, breaking ties by similarity then company ID. With only two resolved peers of different ranks, show ceiling and floor.
- If all resolved peers share one rank, show the closest as a single **Representative comp** with the note "closest resolved peers share the same outcome". Keep the "No verified closure among the closest peers" flag where applicable.
- Each card shows its verified status date and evidence link, matching and differing fields, similarity breakdown and anchor snapshot. The 36-month primary and secondary outcome classifications remain the basis for outcome rates and gates.

## 6. Probability (built and tested, displayed only after a gate passes)

**Naive estimator** (from reference class / k-NN):

  p̂ = Σᵢ wᵢ yᵢ / Σᵢ wᵢ,   wᵢ = sᵢ^γ

Dropping censored peers (still observed, or lost to follow-up) biases this estimator. The implemented version is a **kernel-weighted competing-risks estimator**: an Aalen–Johansen cumulative incidence over the k peers, with weights wᵢ, treating closure and exit as competing events and censoring at last verified activity.

- **Effective sample size:** n_eff = (Σ wᵢ)² / Σ wᵢ². Abstain if n_eff < 10.
- **Shrinkage toward the cohort base rate p₀:** p̃ = (Σ wᵢ yᵢ + m·p₀) / (Σ wᵢ + m). The prior strength m is tuned on training vintages.
- **Uncertainty:** a bootstrap over peers (or a Beta posterior), reported as a 90% interval.

## 7. Validation (before any display)

- **Temporal holdout:** tune k, α, γ and m on earlier entry vintages only, using leave-one-company-out. Test on later vintages whose follow-up window is complete. No company appears in both sets.
- **Baselines:** the cohort base rate, and a logistic regression.
- **Metrics:** Brier score, log loss, a reliability (calibration) curve, and interval coverage. Always report n and the number of events.
- **Ship rule:** display only if the model beats the base rate on held-out Brier score and is calibrated. Otherwise keep showing comps and the gates.

## 8. Entry cohorts

| Cohort | Entry event | Outcome | Use |
|---|---|---|---|
| A. NZ seed-entry (exists) | First institutional pre-seed or seed, 2012–2022 | Series A+ / next priced round within 36 months | Company precedents |
| B. UoA programme-entry (to build) | Velocity / CIE programme entry, complete finalist lists first (2020, 2023) | First verified institutional round within 36 months of entry | Legitimate comps and, later, rates for **university ventures** |
| C. Healthtech deployment (feasibility done) | First verified provider evaluation | Routine provider use within 24 months | Healthtech-specific outcome |

University projects remain **analogy queries** against cohort A until cohort B has follow-up.

## 9. Language

In VC, "comps" also means valuation comparables. The UI therefore says **"Ceiling, typical and floor comps"** under the **Precedents** heading, and never shows valuations.
