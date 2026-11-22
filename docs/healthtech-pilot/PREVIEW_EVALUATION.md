# Time Machine preview evaluation

The primary run uses strict evidence and historical peer records on the provisional track. The strict human-review gate currently has zero of the required 15 Partly peers. The provisional evidence count is nine.

## Acceptance evidence

| Criterion | Result | Evidence |
|---|---|---|
| E1 · Provenance walk | pass | `test_preview_payload_provenance_and_historical_clocks` walks every subject and both evidence modes through the HTTP endpoint. The Playwright first-screen test checks the six visible Supie facts, source URLs, dated evidence, locators and review badges. |
| E1 · Historical leakage | pass | `test_preview_payload_provenance_and_historical_clocks` checks every accepted peer interval, evidence clocks, history and every ISO day outside `reveal`. `test_uncovered_and_future_descriptions_do_not_fit_idf` excludes a future description in both modes. `test_historical_role_does_not_use_later_publication_or_mutable_register` tests filtering before outcome ranking. The existing coverage tests exercise the lenient cap and mutable source rule. |
| E1 · Strict track | pass | `scripts/audit_backtest_coverage.py --require-gate` exits 1 with zero human-confirmed peers. `test_preview_audit_excludes_rejected_unsure_and_strict_ignores_ai` compares both audits. `test_witnessed_profile_http_bytes_match_main` checks four raw HTTP hashes from `main` at `0b7e5d8` on each Python version. A separate side-by-side run of 24 requests for five university projects and Halter had zero byte differences. The request and hash manifest SHA-256 was `43a0026787c2e14ad6bfb11c991ee6b6f0f33202bd6ce3c75692380858a43b87`. The fixture retains both sets of raw hashes because Python 3.12 changed floating-point summation. |
| E1 · Provisional labelling | pass | Endpoint tests check all six subject/mode combinations, unknown subject, invalid query, and strict refusal. `the historical toggle marks later evidence and every subject keeps the banner` checks all cases and the alternate timeline. The first-screen test checks every nearest card and its section label. |
| E1 · Forbidden claims | pass | The Time Machine Playwright suite checks rendered DOM text on the initial, changed-subject, reveal, chart table and hindsight paths. |
| E2 · Hand-checked scores | pass | The calculations below give Supie–Social Club at 0.524 similarity and 0.513 coverage, and Narrative–Social Club at 0.688 similarity and 0.438 coverage. `test_hand_checked_real_pairs` checks both totals to three places and compares all dimension scores and joint coverage. |
| E2 · Vocabulary | pass | `test_vocabulary_exact_partial_cross_branch_flat_root_and_unknown` checks equality, parents, siblings, cross-branch, root, flat geography, aliases and plural forms, explicit missingness and numeric distances. |
| E2 · Determinism | pass | Two `scripts/preview_backtest.py` runs produced the same bytes under `outputs/preview/`. SHA-256 `24c167b16a215a8b930a8e164b613980a44603a590d7612c7def3618cfc45480`. `test_preview_run_is_byte_reproducible_and_separately_labelled` compares two subprocess outputs. The earlier `2aee9c6c` run is retained. The new payload adds the second-reading status to reviewer details. |
| E2 · Adjustability | pass | `test_one_csv_edit_changes_only_one_packet_field_and_the_audit` changes one row in a temporary CSV. Supie's customer field changes from household to consumer in the packet, audit and preview. The strict gate stays at zero. `test_ingest_cli_keeps_input_and_is_byte_identical_on_rerun` verifies the CLI and source packet immutability. |
| E3 · First screen | pass | `the first screen and 60-second demo show evidence, abstention and the source after reveal` measures the entire banner, summary, snapshot and Reveal button within 1440×900 before scrolling. [Desktop screenshot](screenshots/time-machine-desktop.png). |
| E3 · 60-second demo | pass | [README, step 1](../../README.md#3-minute-demo). The same browser test walks from the snapshot to nearest peers, opens the reveal, then verifies the resulting Companies Register tab URL. The browser test serves a fixture at that external URL to keep CI independent of third-party availability. |
| E3 · Plain language | pass | The Time Machine Playwright tests scan visible DOM text for each prohibited method term. Terms remain in the implementation and the method docs. |
| E3 · Partly and Halter | pass | `the historical toggle marks later evidence and every subject keeps the banner` checks both reasons in the picker area, both dated abstention states and each reveal. |
| E4 · Axe | pass | `axe has no serious or critical violations in the entry, reveal and hindsight views` reports zero serious or critical violations, including the open time chart. |
| E4 · Keyboard and chart table | pass | `keyboard can operate every control and reach every source including revealed events` starts from the skip link, activates Reveal and hindsight, opens the chart table, and reaches each source link. The keyboard picker test changes cases with the native select. |
| E4 · 390 px width | pass | `390px layout keeps the banner and expanded reveal readable` asserts a 390 px document width with no horizontal overflow and verifies the banner, expanded button and liquidation text fit inside the check viewport. [Mobile screenshot](screenshots/time-machine-mobile.png). |
| E4 · Design system | pass | `frontend/src/time-machine.css` uses workbench tokens and extends the shared card, toolbar and trajectory. The style and layout changes are scoped to the page and its navigation link. |
| E4 · Cards and bands | pass | The first-screen Playwright test verifies the three loose nearest scores, each missed product/customer bar and no more than three rows in each matched/differing list. |
| E4 · Empty states | pass | The snapshots and Why no comps yet panels explain the missing historical facts. The [case results](PREVIEW_RESULTS.md) specify the source or peer records that would change each case. |
| E5 · Full CI matrix | pass | [GitHub Actions run 45031407588](https://github.com/spar473/venture_evidence_explorer/actions/runs/45031407588) passed all six jobs for reviewed preview commit `e978bca`. The Python 3.10–3.13 jobs passed `pytest -q` and `export_contract.py --check`. The browser and lint jobs passed Playwright, ruff, Prettier and pyright. |
| E5 · Scoped pyright | pass | `pyright --pythonpath .venv/bin/python` in basic mode reported zero errors, warnings and information messages. `pyrightconfig.json` includes seven new Python modules. The lint workflow runs the same check. |
| E5 · New code tests and coverage | pass | Coverage 7.17.4 ran 23 targeted tests with branch and subprocess coverage on the seven new Python modules. Combined coverage was 96%, with 551 of 562 statements run. Playwright's Chromium V8 coverage remapped through the production source map covered 637 of 657 lines (97.0%) and 117 of 143 branches (81.8%) in `time-machine.tsx` across the three cases, reveal, chart table and hindsight. |
| E5 · Runtime dependencies | pass | Runtime requirements are unchanged. Pyright, coverage and the axe Playwright adapter are development dependencies. |
| E5 · Endpoint p95 | pass | 20 sequential HTTP GETs to `/api/backtest/public_supie` on a new disposable demo process over loopback. Nearest-rank p95 was **21.21 ms** and the cold maximum was **141.57 ms**. |
| E5 · Legacy and research views | pass | All 55 browser tests passed locally, including the 49 unchanged legacy tests. Backend strict comparison responses match the raw `main` responses. |
| E6 · Per-subject results | pass | [Provisional results](PREVIEW_RESULTS.md) describes all three cases, their evidence and the nearest scores where available. |
| E6 · PR evidence | pass | The [Time Machine pull request](https://github.com/spar473/venture_evidence_explorer/pull/14) includes the E1–E5 results, provisional status, known gaps and before, desktop and mobile screenshots. |
| E6 · Project docs and demo | pass | [Status](../../STATUS.md), [next steps](../../NEXT_STEPS.md), [changelog](../CHANGELOG.md) and [demo](../../README.md#3-minute-demo). |
| E7 · Fresh-eyes review | pass | An independent reviewer exercised all three live cases, both peer histories and strict refusal, and reproduced the earlier preview digest. Questions, repairs and remaining gaps are listed below. |

## Hand calculations

For each dimension, take the mean of jointly observed field scores. Divide the weighted sum of the defined dimension scores by the sum of their weights. Coverage uses all four dimension weights, with each weight multiplied by its jointly observed fraction. Missing fields do not contribute to similarity or coverage. See the [frozen scoring rules](../design/BACKTEST_PREREG.md#3-frozen-general-similarity-profile).

### Supie and Social Club

The description corpus contains ten records. The two descriptions share only `online`. Of 14 distinct terms in their union, `online` and `platform` occur in three documents each and the twelve others occur in one document each. With `w(df) = 1 + ln((10 + 1) / (df + 1))`, the union weighs `2w(3) + 12w(1) = 36.48017893`. The shared term weighs `w(3) = 2.01160091`, so description similarity is **0.05514230**.

- **Product and customer, weight 0.35.** Description 0.05514230. Food and beverage versus marketplace 0. Household versus business 0. Business model missing on both sides. Mean **0.01838077** across three of four fields. Coverage contribution **0.2625**.
- **Market, weight 0.15.** Online retail versus media 0.5 as siblings in digital. New Zealand versus New Zealand 1. Mean **0.75** across two of two fields. Coverage contribution **0.15**.
- **Stage evidence, weight 0.30.** Working product yes versus yes 1. Paying customers and full-time team missing on both sides. Mean **1** across one of three fields. Coverage contribution **0.10**.
- **Funding context, weight 0.20.** Round size, lead-investor type and months since founding are missing. No score and **0** coverage contribution.

Similarity `(0.35 × 0.01838077 + 0.15 × 0.75 + 0.30 × 1) / 0.80 = 0.52366659`. Coverage `0.2625 + 0.15 + 0.10 = 0.5125`. Product and customer misses the **0.25** bar.

### Narrative and Social Club

Use Narrative's 21 May 2019 entry as the cutoff for this pair check. Its eight-description corpus gives a union weight of **33.26532409** for this pair. No term is shared, so the description score is **0**.

- **Product and customer, weight 0.35.** Description 0. Workflow versus marketplace 0.5 as software siblings. Business versus business 1. Business model exists only for Narrative. Mean **0.50** across three of four fields. Coverage contribution **0.2625**.
- **Market, weight 0.15.** Enterprise software and media are digital siblings, scoring 0.5. Market served exists only for Social Club. Mean **0.50** across one of two fields. Coverage contribution **0.075**.
- **Stage evidence, weight 0.30.** Working product yes versus yes 1. No joint record for paying customers or full-time team. Mean **1** across one of three fields. Coverage contribution **0.10**.
- **Funding context, weight 0.20.** Round size, lead-investor type and months since founding are missing. No score and **0** coverage contribution.

Similarity `(0.35 × 0.50 + 0.15 × 0.50 + 0.30 × 1) / 0.80 = 0.6875`. Coverage `0.2625 + 0.075 + 0.10 = 0.4375`. This pair clears the numerical checks. Narrative is used here for an arithmetic cross-check and is outside the three demo subjects.

## Fresh-eyes review

### Icehouse software engineer or data analyst

1. What produces 0.524 similarity when Social Club's product and customer match is 0.018? The hand calculation above and preregistration section 3 show the dimensions, thresholds and weights.
2. Which dates stop later information from entering the scores? The API notes and E1 tests show the separate clocks, role filtering and reveal isolation. The peer-history toggle leaves scores in place. Hindsight now shows when an older event's source was checked or available.
3. Who checked each fact, and what did the second reader confirm? The banner identifies the review track. Review and source details gives the reviewer, date and result of any comparison. Amendment 1 explains the blind second reading and its source access.
4. What happens when data are sparse? Partly shows nine of 32 earlier peers with five facts and Halter shows one of eight. Neither subject has enough evidence to score. Halter's snapshot explains why the first day of December is used.
5. Can I reproduce and edit a run? The README gives a one-command run, a temporary CSV workflow and the strict audit command. E2 gives the baseline digest.

### Icehouse investment analyst

1. Can I screen a new company here? The case picker limits the replay to Supie, Partly and Halter. The footer explains that all three were selected with known outcomes. The separate Precedents view offers venture search.
2. Which earlier company looks closest, and why did it fail? The nearest cards put Social Club first and show the shared features and missed product and customer check. The table caption distinguishes its shared evidence weighting from the cards' similarity order.
3. What happened to Supie and the nearest companies? The reveal shows Supie's administration and liquidation. The dated First AML announcement is visible, and the case results explain why it does not establish a priced round. Hindsight shows the additional peer records separately.
4. How much should this influence screening? The banner identifies AI review and the strict gate. The page gives specific failed checks and the case results show why all three cases abstained.
5. Where can I inspect the source and passage? Each snapshot fact and event links to a source. Review and source details exposes the field locators by touch or keyboard. The method and case results also open offline. `test_time_machine_links_serve_local_method_and_case_results` verifies both routes.

## Known gaps

- Human confirmation is pending for 72 field decisions, including 21 archive-based fields with no independent extraction. The preview is exploratory and the strict track remains gated.
- Six additional well-covered earlier peers and a qualifying Partly entry source are needed. Parcelport's offering classification is unresolved.
- Missing peer outcome records limit the historical comparisons. None of the three cases can be evaluated for the preregistered span or typical-case checks.
- The Register page was inaccessible to the independent reviewer's source checker. The link target was verified in Playwright and the liquidators' report independently corroborates both dates. [Supie case](PREVIEW_RESULTS.md#supie--9-november-2021).

## Scorecard

- **Visitor experience · B (target B).** The first screen has six dated facts, a clear abstention and a working reveal. Two cases still have empty snapshots.
- **UX and design · B (target B).** The mobile and desktop screenshots, keyboard source walk and zero serious or critical axe findings support the grade.
- **Method and data rigour · A− (target A−).** Two hand calculations, byte reproducibility, field-level adjustment and the historical-clock tests support the method. Human review remains pending.
- **Engineering · A− (target A−).** The CI matrix, scoped typing and measured coverage pass, with a 21.21 ms p95 on the final demo process.
