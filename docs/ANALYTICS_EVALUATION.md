# Analytics views acceptance

23 November 2026. Provisional AI-checked evidence. The strict human-review gate remains unmet. The scope is the three registered subjects and the frozen New Zealand seed-entry cohort. Scenario overrides apply only to the selected subject.

| Criterion | Result | Evidence |
| --- | --- | --- |
| E1 · Provenance and chronology | Pass | `test_entry_profile_evidence_has_provenance_and_no_later_facts` covers every registered subject and peer fact. `test_cohort_counts_and_sources_match_frozen_audit` checks event and field citations and the status clock. Entry score payloads carry no later events. Retrospective review metadata and cohort event histories travel in separate `reveal` blocks. The browser test opens Supie’s liquidation source only after changing playback. |
| E1 · Strict gate and frozen clinical scorer | Pass | `scripts/audit_backtest_coverage.py --require-gate` exited **1**. Zero of 15 required peers have enough human-confirmed facts. Nine reach the field bar with AI checks. `test_preview_audit_excludes_rejected_unsure_and_strict_ignores_ai` and `test_witnessed_profile_http_bytes_match_main` passed. |
| E1 · Labels and forbidden terms | Pass | Each analytics view has the provisional banner. Playwright checked DOM text outside the labelled synthetic figures, with zero forbidden claims or method terms. No role names appear on nearest peers. |
| E2 · Hand checks and vocabulary | Pass | The worked pairs below match `test_hand_checked_real_pairs`. The baseline token, alias, hierarchy, flat-category and artificial-root cases passed in `test_vocabulary_exact_partial_cross_branch_flat_root_and_unknown`. The scenario POST checks allowed overrides and rejects invented values. |
| E2 · Adjustability | Pass | `test_one_csv_edit_changes_only_one_packet_field_and_the_audit` uses a temporary copy of the decision file. The profile and scenario routes share the same input loader and audit. |
| E2 · Reproducibility and scenario results | Pass | The preview, robustness and synthetic reproducibility checks passed. The seed-7 digests and expected results appear below. The offline scorer matched live Python to six places for each peer in all 18 subject/preset combinations. |
| E3 · Story above the fold | Pass | The hero figure in each view fits in a 1440 × 900 viewport. The [captures](#screenshots) show the first screen of each view. Profile opens at the first round, gives the abstention and supports one-month keyboard steps. Partly and Halter show dated reasons. |
| E3 · 60-second walk-through | Pass | The [README demo](../README.md#3-minute-demo) starts with Supie. `profile playback reveals each dated event and its source by keyboard` covers the entry snapshot, score explanation, playback, review badge and a Companies Office link. The external navigation in this test uses a local response fixture. |
| E4 · Chart accessibility | Pass | Playwright focused a mark and toggled the table fallback on each chart. SVGs have accessible summaries. Axe reported zero serious or critical findings at 1440 and 390 px in the four default views. |
| E4 · Mobile, styles and abstention | Pass | Playwright measured a 390 px scroll width on all four views at a 390 px viewport. Styles are scoped to the analytics page and use the existing base focus and type tokens. Peer details show the score band and up to three shared features and three differences. Entry abstentions name the evidence that would help. |
| E5 · Local engineering | Pass | Python 3.11, `pytest -q` (**264 passed, 2 skipped**), ruff check and format, Prettier, generated contracts and scoped pyright (zero errors). New Python analytics code measured **93% statement coverage** in the targeted suite. The synthetic CLI additionally ran twice in an isolated subprocess. |
| E5 · Hosted matrix | Pending | The engineering workflow covers Python 3.10–3.13, contracts, lint and browser regressions. The Pages workflow adds the static build, offline scorer parity and the eight browser checks. Hosted acceptance requires the pull request checks to finish. |
| E5 · Runtime budget | Pass | Observable Plot is the single added direct runtime dependency. In a loopback disposable demo, nearest-rank p95 over 20 warm GETs was **3.19 ms** for backtest, **3.95 ms** for profile, **3.34 ms** for cohort, **0.95 ms** for robustness and **0.90 ms** for synthetic figures. |
| E5 · Legacy and static behavior | Pass | The live Playwright suite passed **62** checks. Its one production-redirect check runs in the static suite. The original specs use the compatibility router, including the local research workspace. The production router separately verifies redirects for the old Time Machine, Precedents and Outcomes links. Static Playwright passed **8 of 8**. |
| E6 · Review materials | Pass | [Previous case results](healthtech-pilot/PREVIEW_RESULTS.md), [screenshots](#screenshots), [status](../STATUS.md), [next steps](../NEXT_STEPS.md), [changelog](CHANGELOG.md) and [README](../README.md). |
| E7 · Fresh-eyes review | Pass | An independent reviewer opened the running views and the three cases in local Chromium. The questions and fixes are recorded below. |

Playwright counted **39**, **41**, **48** and **30** words of visible body copy for Profile, Cohort, Scenario and Method, respectively. The count covers the provisional banner and visible prose. Chart data, field labels, navigation and controls are interface labels. The forbidden-language check also scans chart and control text outside the labelled synthetic figures.

## Screenshots

| View | Desktop at 1440 × 900 | Mobile at 390 × 844 |
| --- | --- | --- |
| Company profile | [Desktop](analytics-screenshots/profile-1440.png) | [Mobile](analytics-screenshots/profile-390.png) |
| Cohort explorer | [Desktop](analytics-screenshots/cohort-1440.png) | [Mobile](analytics-screenshots/cohort-390.png) |
| Scenario lab | [Desktop](analytics-screenshots/scenario-1440.png) | [Mobile](analytics-screenshots/scenario-390.png) |
| Method lab | [Desktop](analytics-screenshots/method-1440.png) | [Mobile](analytics-screenshots/method-390.png) |

[Before redesign, Time Machine first screen](healthtech-pilot/screenshots/time-machine-desktop.png)

## Hand checks and case results

The weighted sum includes only dimensions with a defined score and divides by their combined weight. Coverage sums each dimension weight times the jointly observed fraction. The strict preview entry clocks and the comparison corpus follow the [preregistered method](design/BACKTEST_PREREG.md#3-frozen-general-similarity-profile).

| Dimension | Weight | Supie and Social Club, 9 Nov 2021 | Narrative and Social Club, 21 May 2019 |
| --- | ---: | --- | --- |
| Product and customer | 0.35 | Description 0.05514230, product 0, buyer 0. Mean 0.01838077, 3 of 4. Coverage contribution 0.2625. | Description 0, product 0.5 for software siblings, buyer 1. Mean 0.50, 3 of 4. Coverage contribution 0.2625. |
| Market | 0.15 | Sector 0.5 for digital siblings, market 1. Mean 0.75, 2 of 2. Coverage contribution 0.15. | Sector 0.5 for digital siblings. Mean 0.50, 1 of 2. Coverage contribution 0.075. |
| Stage evidence | 0.30 | Prototype 1. Mean 1, 1 of 3. Coverage contribution 0.10. | Prototype 1. Mean 1, 1 of 3. Coverage contribution 0.10. |
| Funding context | 0.20 | No comparable fields. Coverage contribution 0. | No comparable fields. Coverage contribution 0. |

Supie and Social Club share `online`. Its weight is 2.01160091 and the 14-term union weighs 36.48017893 using the ten-record entry corpus. The final similarity is `(0.35 × 0.01838077 + 0.15 × 0.75 + 0.30 × 1) / 0.80 = 0.52366659` with coverage **0.5125**. Product and customer misses 0.25. Narrative shares zero terms with Social Club. Its similarity is `(0.35 × 0.50 + 0.15 × 0.50 + 0.30 × 1) / 0.80 = 0.6875` with coverage **0.4375**.

- **Supie.** Zero of 39 eligible peers qualify on recorded facts. Nine have enough entry facts. Formus Labs and Inhibit Coatings tie on the product-and-customer ordering at 0.250 on that dimension and 0.175 overall. They miss overall similarity, shared evidence and peer fact checks. Social Club leads overall similarity with a product-and-customer score of 0.018. A dated offering and buyer record for closer peers could change the result.
- **Partly, 8 October 2020.** No scoreable subject facts. Nine of 32 earlier peers reach the field bar on this track. A dated offering and intended-buyer source is needed.
- **Halter, 1 December 2016.** No scoreable subject facts. One of eight earlier peers reaches the field bar. The entry month is imprecise. The score uses its earliest day and needs a dated offering and intended-buyer source by then.
- **Cohort explorer.** The full audit includes 453 candidates and 55 entries, with 2 verified Series A or later within 36 months, 33 unknown and 10 lost to follow-up. Historical entry counts use retrospectively accepted entry dates. Follow-up uses source availability and the selected date. The heatmap withholds later reviews.
- **Scenario lab.** Recorded, business buyer, business plus subscription, software, software plus business and revenue alone yield **0, 4, 5, 3, 7, 0** qualifying peers for Supie. The business-buyer preset includes Social Club at **0.669**, First AML **0.661**, Narrative **0.615** and Parcelport **0.527**. Overall-similarity robustness is calculated for the full frozen peer pool.
- **Method lab.** The real audit gate shows **55 of 150** companies, **2 of 30** verified outcomes and **43 of 55** unknown or lost. The estimator runs on seeded generated observations. The sample-size comparison uses 55, 150 and 500 simulated observations. Calibration compares independently generated fitting and held-out groups.

Social Club’s preregistered sensitivity ranges are **0.476–0.573** for product and customer, **0.480–0.565** for stage, **0.507–0.540** for market, and **0.524–0.524** for funding. Four peers tie for the third place at 0.47 in the recorded ranking. All four remain tied at the membership boundary in 2,000 of 2,000 seeded draws.

## Reproduction

Run `scripts/preview_backtest.py`, `scripts/export_static.py` and `scripts/synthetic_cohort.py --seed 7` with the project Python. The artifact digests below were measured with Python 3.11. Scenario scores use the same eligible peers and source cutoff as their recorded case. The playback date advances the event display.

| Output | SHA-256 |
| --- | --- |
| Provisional backtest | `24c167b16a215a8b930a8e164b613980a44603a590d7612c7def3618cfc45480` |
| Supie robustness, 2,000 draws | `806fb8f971e5910f6e4181e3586177c81fc599c088d74124923ec4f1be84b131` |
| Partly robustness, 2,000 draws | `9b9e657e46637a31851f7efba38f0e199d4b2467ab442678c61b65be0917e03a` |
| Halter robustness, 2,000 draws | `adf268459ea62a8b477e04c22d17d34f5c040ba16313f94191d41e925cb01bc1` |
| Synthetic cohort | `e95f4bce608d2b030ad989452040e0dc985f344f8f6d24f88ecbfe9c41de835c` |
| Synthetic figures | `42e687d753787de3f98559ef6930142a3806c57dafb81bfd8a5c44b00d36137a` |

## Fresh-eyes questions

| Reader | Question | Where the view or documentation answers it |
| --- | --- | --- |
| Icehouse software engineer or data analyst | What clock controls each view? | Profile playback, Scenario scoring date and the [preregistration](design/BACKTEST_PREREG.md). A pre-entry profile URL and its date input now normalize to the first round. |
| Icehouse software engineer or data analyst | Why is Social Club’s overall score high with a small offering match? | Peer map, score breakdown, shared evidence and the arithmetic above. |
| Icehouse software engineer or data analyst | Who checked each fact and when? | Entry and peer evidence drawers give publisher, locator, availability date and reviewer details. The heatmap withholds later review decisions. |
| Icehouse software engineer or data analyst | Does a filter change ranking stability? | The profile KPI and Scenario robustness identify full-pool sensitivity. Filtering changes the displayed comparison set and scenario counts. |
| Icehouse software engineer or data analyst | Can I rebuild or change the run? | Static export manifest, reproducibility commands, API contracts and the parity test. The [review CSV workflow](../README.md#run-it) preserves earlier run records. |
| Icehouse investment analyst | How much weight should I give this? | Provisional banner, strict entry-evidence requirement, and separate real outcomes gate in Method lab. |
| Icehouse investment analyst | Who is nearest and why are there no comps? | Company profile distinguishes product-and-customer ordering, overall score, score band, ties and missed checks. |
| Icehouse investment analyst | What happened later and can I open the source? | Playback and dated event marks. The reviewer found Supie’s liquidation, Partly’s December 2022 Series A and Halter’s January 2018 Series A in the local evidence. |
| Icehouse investment analyst | Which assumption changes the peer set? | Preset and custom counts, the hypothetical inputs alongside recorded subject facts in each peer drawer, and later peer events labelled as hindsight. |
| Icehouse investment analyst | What can I learn from the larger cohort? | Counts by vintage and sector, company drilldowns, event strip and evidence heatmap. The real gate gives the full-cohort counts alongside the synthetic exercises. |

## Known gaps

- Human confirmation remains pending. Six further well-covered earlier peers for Partly and a dated Partly entry source are needed. Parcelport’s product classification still needs resolution.
- The registered case selector covers Supie, Partly and Halter. The live research workspace and previous workbench provide broader search. Pages serves the read-only analytics build and points research users to the server-backed workspace.
- The audit records 43 of 55 companies with unknown or lost follow-up. Current outcomes and scenarios are descriptive. No verified historical role is established for the Supie presets.
- GitHub Pages uses the GitHub Actions publishing source and a main-only deployment environment. The static demo is checked locally. Its first Pages deployment follows a push to `main`.
- Production source links are external. The browser walk-through checked navigation and local provenance. The fresh-eyes reviewer did not re-verify third-party source contents.

## Lighthouse

Lighthouse 13.6.0, default mobile simulation against the loopback static build. The latest reading on the final layout was **64** for Profile, **100** for Cohort, **100** for Scenario and **79** for Method. The local measurements varied across runs. The performance threshold is non-blocking.

## Self-assessment

Targets were visitor B+, UX A−, method A− and engineering A−.

| View | Visitor | UX | Method | Engineering | Basis |
| --- | --- | --- | --- | --- | --- |
| Company profile | B+ | A− | A− | A− | The entry story, tie and source walk work on both widths. Partly and Halter remain sparse. |
| Cohort explorer | B+ | B+ | A− | A− | Count drilldowns are clear. The 12 heatmap columns use abbreviations on narrow screens and expand in the table. |
| Scenario lab | B+ | A− | A− | A− | Preset counts, source-linked events and the weighting tie are inspectable. The three empty recorded cases constrain comparisons. |
| Method lab | B+ | A− | A− | A− | The synthetic charts and real counts are clearly labelled. The sample-size demonstration uses one seeded draw of each nested group. |
