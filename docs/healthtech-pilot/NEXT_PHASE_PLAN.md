# Next phase: NZ reference pool and outcome distributions

Status: plan, revised 20 November 2026 after code-agent review. Nothing in this document is implemented yet.

## Goal

Given an early NZ venture, show where comparable NZ companies started, how long each step took, and how many stalled or closed. Then, if the data supports it, estimate the chance of reaching a defined milestone within a defined window.

Example of the question we want to answer honestly:

> Among NZ medtech/healthtech companies in our source-covered cohort, how long did the fastest, typical and slowest take to reach Series A after their first seed round, and how many closed first?

## The design change: include companies that did not succeed

A pool made only of Series B+ companies shows only success, so every comparison would look positive (survivorship bias). The two pools answer different questions:

| Pool | Question it can answer | Question it cannot answer |
|---|---|---|
| Established companies (Series B+) | *If* a venture follows a successful path, how long does each step take and what had peers proven at each stage? | How likely is the venture to succeed? |
| Entry cohort (companies meeting a fixed entry rule, whatever happened next) | What share reached the next stage, how fast, and how many closed first? | Nothing extra, as long as coverage and follow-up are reported honestly |

We build the **entry cohort**. The established companies are a labelled subset of it, so benchmarking against them still works.

## What the pool represents

The pool is a **source-covered cohort**: every company that the defined discovery sources record as meeting the entry rule. It is not "every NZ company". Coverage is measured, not assumed:

- Apply the inclusion rule **before** looking at any outcome, and record the date and source of each inclusion decision.
- Run a coverage audit by vintage and sector, for example cross-checking against NZGCP deal-count reports and the Angel Association / Young Company Finance figures where they exist. Report the gaps.
- **The 30-company P1 set is a hand-picked test fixture.** It exercises imports, timelines and quiet cases. It is never used for rate estimates. Rate estimates come only from the rule-based cohort built in P2.

## Pool definition (v1)

**Entry event:** the first publicly reported institutional pre-seed or seed round of a NZ-founded or NZ-headquartered company, dated between 2012-01-01 and 2022-12-31. The 2022 cut-off allows at least three years of follow-up before 2026.

**Unit:** one company. Renames and pivots resolve to one company ID with aliases (the existing identity model already supports this).

**Discovery sources** (public pages only, each capture dated):
- Public portfolio pages of NZ funds: Icehouse Ventures, Blackbird (NZ companies), GD1, Movac, Punakaiki Fund, NZGCP Aspire, Pacific Channel, Booster Innovation Fund, Outset Ventures, Sprout, Nuance Capital, Cure Kids Ventures, Matū, WNT Ventures, Enterprise Angels and Angel Association announcements.
- The existing discovery queue (`research/expanded-discovery/`, 274 staged leads).
- News and press releases for round dates.
- NZ Companies Office register for legal entity, incorporation date and removal from the register (closure evidence).
- University sources (UoA, CIE, Velocity) to flag university origin.

**Data-use rules:** no automated extraction from Dealroom, Crunchbase, PitchBook or LinkedIn. LinkedIn posts are captured by hand, with URL and date. Record each source's retrieval date.

**Sector:** cross-sector pool, with sector, buyer type, business model and regulatory pathway as filters. Healthtech/medtech is the first analysed subset, not the only content. NZ healthtech alone is too small for statistics.

## Outcome rules (freeze before building any curve)

**Primary outcome:** a priced equity round that the company, lead investor or a news report labels "Series A" or a later letter (B, C…), within 36 months of the entry event.
- "Pre-Series A", seed extensions, bridges, convertible notes, grants and crowdfunding do **not** count. Record them as separate events.
- Store the label exactly as the source gives it. An unlabelled round of at least NZ$5M led by an institutional VC is recorded as `series_a_equivalent` and analysed only in a sensitivity check, never silently merged.
- Acquisition or IPO before Series A is its own outcome, recorded and reported separately.

**Decision · 20 November 2026.** M0 will also estimate cumulative incidence for the pre-listed secondary outcome, **the next completed priced equity round within 36 months of entry**. A later seed, seed extension, bridge or unlabelled financing can qualify when dated evidence establishes a distinct round, a share price or round valuation, and new equity capital for the company. Tranches of the entry round, convertible instruments before conversion, grants and secondary share transfers do not qualify. Verified closure and acquisition or IPO before the next priced round are competing events.

The secondary outcome uses the same source-covered entry cohort and 150-company minimum as the primary analysis. Its release gate requires at least **30 independently qualifying secondary events**, a reported count still under observation at 36 months, and **unknown plus lost to follow-up below 25%** of the cohort. Apply the same follow-up rule to both outcomes. Assess each gate against its own event and status counts. Freeze this decision before collecting the next batch of follow-up evidence.

**Status categories (kept distinct; never merged):**

| Status | Meaning | Treatment |
|---|---|---|
| `reached_outcome` | Primary outcome observed with dated evidence | Event |
| `closed_before_outcome` | Verified closure (register removal, liquidation notice, founder announcement) before the outcome | **Competing event**: it prevents the outcome |
| `acquired_or_ipo_before_outcome` | Exit before Series A | Competing event, reported separately |
| `observed_no_outcome` | Verified activity continues, no outcome yet | Censored at last verified activity |
| `lost_to_follow_up` | No verified activity for 18+ months and no closure evidence | Censored at last verified activity and flagged; counted on every chart |
| `unknown` | Not enough evidence to place the company | Excluded from rates and counted on every chart |

**Estimation:** use **cumulative incidence with competing risks** (Aalen-Johansen estimator) for the probability of reaching Series A over time. Do not use 1 − Kaplan-Meier with closures treated as censored, because that ignores competing events and overstates the chance of reaching Series A.

## Snapshot contract: proof of historical availability (P1 requirement)

The current research schema cannot prove that a source version was public at a past cutoff, so historical mode abstains (`docs/research_api.md`). P1 adds that support:

- Every source used in an as-of snapshot carries an **availability witness**, one of:
  1. `publisher_dated`: a press release or news article with a publication date the publisher states, captured with its URL; or
  2. `archived_capture`: an archive capture (e.g. Wayback Machine URL plus capture timestamp) dated on or before the snapshot date, which is required for undated or mutable pages such as portfolio pages and company "About" pages.
- A source without a witness can still support the present-day timeline but is **excluded from any as-of snapshot**.
- An automated test enforces it: snapshot features may only reference sources whose witness date is on or before the snapshot date. An old date printed inside a present-day page does not qualify.

## As-of snapshots

For each company, a feature snapshot at entry (and later at each stage), using only witnessed sources:

- Stage, months since founding, team size if published, number of founders, prior founder exits (public only), university origin, sector, buyer, business model, regulatory class, capital raised to date, lead investor type, and a short description written from witnessed sources.

## Subject ventures (3–5)

Neurofanos, Automated Breast MRI Reporting, IVF Decision Support Tool and VistaVision, with PulseMap kept as the abstain case. Use public sources only for every subject.

These are research-stage projects. **They remain analogy queries** (retrieve peers and show peer trajectories) until a subject has a verified qualifying entry event. Only then can it be placed on the cohort's time axis or receive any rate-based statement.

## Methods ladder

Each rung must work and be checked before the next starts.

| Rung | Method | Output | Gate to next rung |
|---|---|---|---|
| T Trajectories (from P1) | Sourced stage timelines for named companies; no rates | Trajectory strip and coverage panel | Available at 30 companies |
| M0 Base rates | Cumulative incidence of Series A with closure as a competing event, overall and by sector and vintage | Curve with confidence band, number at risk, and counts per status | Rule-based cohort of 150+ companies **and** at least 30 primary-outcome events **and** a reported count of companies still observed at 36 months, with lost-to-follow-up under 25% |
| M1 Peer retrieval | Local sentence-embedding model (no paid API) over witnessed description text, plus structured filters. Compare against the existing B0 lexical method | Top-k peers with match reasons and differences | Review shows embedding peers are as relevant as B0 or better on the six existing tasks |
| M2 Peer outcome view | Peer trajectories against cohort cumulative incidence | The main visual: "where this venture could go, by NZ precedent" | M0 gate met; denominator, censoring and status counts visible on every chart |
| M3 Gated models | (a) logistic regression and gradient boosting on entry snapshots; (b) TabPFN; (c) optional kNN in-context LLM. Temporal holdout (earlier vintages train, later test), no company in both sets | Calibrated probability of the primary outcome, with uncertainty | Beats the M0 base rate on held-out Brier score and calibration. If not, ship T, M0–M2 only |

M3 rules:
- LLMs already know famous NZ outcomes (Volpara, Halter). Any LLM-based model must anonymise inputs and pass a re-identification test before its backtest counts.
- Report results relative to the base rate, never as raw accuracy alone.
- Bayesian shrinkage toward a global prior is optional. It is a good fit for small NZ subgroups.
- Paid APIs need a separate explicit decision. Default to local models.

## Visualisations

1. **Trajectory strip (from P1):** months since entry on the x-axis and stage on the y-axis. Named companies are drawn as step lines; closures end in a cross and censored lines end in an open circle. For an analogy-query subject, peers only; no subject marker on the time axis.
2. **Coverage panel (from P1):** companies by status, sources by witness type, and companies with no witnessed entry snapshot.
3. **Cumulative incidence curve (after the M0 gate):** share reaching Series A over time against the share closing first, with number at risk below.
4. **Evidence panel:** for each peer, what was public at the same stage, with source, witness and date.

## Milestones

- **P0 Presentation (half a day).** Rewrite the README opening into a 5-line pitch plus one screenshot or GIF. Move caveats to `docs/METHOD.md`. No new checksum manifests.
- **P1 Schema, witnesses and test fixture.** Additive migration for pool companies, stage events, status categories, availability witnesses and as-of snapshots. Import the 30-company test fixture across sectors, including at least 8 quiet cases (stalled at seed, verified closure, or lost to follow-up). Include several well-known Icehouse portfolio companies (e.g. Halter, Sharesies) and the existing healthtech references. Ship the trajectory strip and coverage panel. **No rate curves.**
- **P2 Rule-based cohort.** Apply the frozen inclusion rule to the discovery sources. Grow to 150+ companies. Record closures from the Companies Office. Run the coverage audit.
- **P3 Base rates and peer outcome view (M0 + M2 with B0 peers).** Only after the M0 gate is met.
- **P4 Embedding retrieval (M1).** Evaluate against B0.
- **P5 Gated models (M3).** Only if P3 passes.

## Acceptance checks

- Every chart shows N and the count for each status.
- No outcome is inferred from a missing source; closure needs positive evidence.
- Snapshot features never use sources whose witness date is after the snapshot date (automated test).
- No rate, probability or curve is computed from the hand-picked fixture.
- The existing test suites still pass. New logic has unit tests.
- Demo path: Research dossiers → Neurofanos (analogy query) → peer trajectory strip → evidence for one peer → coverage panel.

## References

- Maarouf, Bakiaj and Feuerriegel (2026). *Predicting Startup Success Using Large Language Models: A Novel In-Context Learning Approach.* arXiv:2601.16568.
- Chen et al. (2025). *VCBench: Benchmarking LLMs in Venture Capital.* arXiv:2509.14448.
- *Predicting Founder Success Without an LLM: An Interpretable Tree-Based Approach to VCBench* (2026). Cambridge Open Engage.
- Hollmann et al. (2025). *Accurate predictions on small data with a tabular foundation model* (TabPFN). Nature 637, 319–326.
- Wang, Ihlamur and Alican (2025). *SSFF: Startup Success Forecasting Framework.* arXiv:2405.19456.
- Stegherr, Schmoor, Lübbert, Friede and Beyersmann (2020). *Estimating and comparing adverse event probabilities in the presence of varying follow-up times and competing events.* arXiv:2001.05709. Kaplan-Meier ignores competing events; Aalen-Johansen is the reference estimator.
- PitchBook. *VC Exit Predictor technical documentation.* Prediction-date rules against look-ahead bias and leakage.
- Angelopoulos and Bates et al. *Theoretical Foundations of Conformal Prediction.* arXiv:2411.11824.
