# Ceiling, typical and floor comps: method

Status: method spec, 21 November 2026. Implementation and display are gated as described below. Nothing here permits showing a probability before a release gate in `docs/healthtech-pilot/NEXT_PHASE_PLAN.md` passes.

## Inspiration and terms

| Term | Meaning here |
|---|---|
| **Player comps (ceiling / floor)** | The NBA scouting format: "best case he becomes X, worst case Y". Named examples that make a range of paths concrete. They are *not* probabilities. |
| **Reference class forecasting** | Predict from the outcomes of a relevant historical group (the "outside view"), not from the subject's own story. |
| **Similarity-based projection** | FiveThirtyEight's CARMELO approach: find the most similar historical players, then project from what happened to them. |
| **Similarity-weighted k-nearest neighbours (k-NN)** | The practical implementation: take the k most similar historical ventures and give closer ones more weight. |

VC adaptation: **named comps first** (always available, honest), **probabilities later** (only when the cohort supports them).

## 1. Start the clock (anchor event)

Every comparison is made at a comparable stage, chosen with the UI's "Align at" selector:

- `first_institutional_round` (default)
- `first_provider_or_clinical_study`
- `first_regulatory_decision`
- `first_paid_customer`

For each venture, the anchor date is the date of that event, with its precision. Partial dates become intervals. A venture without a dated anchor event is listed as "Not alignable", never dropped silently.

## 2. Snapshot at the anchor

Features come only from sources whose **availability witness** is dated on or before the anchor date (see the witness contract). There are five dimensions:

| Dimension | Example features | Type |
|---|---|---|
| Clinical workflow | modality, clinical user, output type; description text | categorical + text |
| Buyer and sales path | buyer type (hospital, clinic, consumer, pharma), procurement path | categorical |
| Regulatory path | device class, jurisdiction, decision obtained | ordinal / categorical |
| Stage evidence | milestone checklist values (prototype, provider study, submission, paid pilot, full-time team) | Yes / No / ? |
| Funding context | months since founding, round-size band, lead investor type | numeric / categorical |

A missing feature is **missing**, never "No".

## 3. Similarity

- **Per-dimension similarity** s⁽ᵈ⁾ ∈ [0, 1], using Gower similarity for mixed types. Numeric features use range-normalised absolute difference. Categorical features use a match score. Text uses cosine similarity of a **local** sentence-embedding model over witnessed descriptions, with B0 kept as the baseline.
- Features missing for either venture are excluded from that pair's average. The share of features available is reported as **coverage**.
- **Overall similarity:** s = Σ_d α_d s⁽ᵈ⁾ / Σ_d α_d, summed over dimensions with coverage. The α weights are fixed in advance and documented, and are tuned later on training vintages only.
- The UI shows the per-dimension breakdown, because a venture can be a strong peer on procurement and a weak one on clinical validation.

## 4. Peer set

- Top k by similarity (default k = 12), with a minimum similarity and a minimum coverage.
- Fewer peers are returned when evidence is thin. If fewer than 3 qualify, the tool abstains.
- The subject is excluded, and so is any peer whose identity is linked to it.

## 5. Ceiling, typical and floor

Choose only from inside the top-k. **No reaching outside the peer set** for a better story.

- **Outcome ladder** at the chosen horizon: exit or IPO > Series B+ > Series A > observed with no outcome > lost to follow-up > closed.
- **Ceiling:** the best-ranked outcome; ties go to the higher similarity.
- **Floor:** the worst-ranked *resolved* outcome, with verified closure preferred. If no closure exists among the top-k, show the worst observed case and say "No verified closure among the closest peers".
- **Typical:** the median outcome rank among resolved peers.
- Each card shows why it matches, where it differs, its similarity breakdown, its same-stage snapshot (or why that is withheld), and a link to its evidence.
- `unknown` peers are listed but never chosen as a comp.

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
