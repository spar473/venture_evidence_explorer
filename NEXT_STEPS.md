# Next steps

## Analytics rollout

The [analytics evaluation](docs/ANALYTICS_EVALUATION.md) records the browser checks, seeded outputs and Pages status. The next evidence work is human review of the entry facts, six more well-covered earlier peers for Partly and a dated Partly offering and buyer source.

Updated 2026-11-23. Data decisions waiting on the owner are listed in [STATUS.md](STATUS.md).

## Improvement checklist sequence

The six pre-demo repository and language fixes are complete. Code uses MIT with a separate data notice; the listed agent records and generated outputs are removed, the sidebar wraps long names, and the five main jargon labels use plain language. The repo is public. Eleven explicitly approved merged branches were removed; the unmerged test branch and implementation branches were preserved.

## Time Machine evidence priorities

1. Review all 72 field decisions with a named human reviewer. Start with the 21 archive-based fields that have had no independent reading. [Field review](docs/healthtech-pilot/BACKTEST_REVIEW.md).
2. Research six additional Partly-eligible peers with at least five sourced facts each. Marama has four strict proposals and Formus and Inhibit have three each. The 1Centre material is available only in the lenient view. [Coverage checkpoint](docs/healthtech-pilot/BACKTEST_COVERAGE.md).
3. Find an inspectable Partly source from before 8 October 2020 that establishes entry facts about the offering, customers or stage.
4. Resolve Parcelport's product type. Its charge was for freight while dispatch software was supplied free. Check the source again and record the classification with a rationale.

Use `scripts/audit_backtest_coverage.py --require-gate` before enabling the strict view. The current preview runs have a separate output directory and a visible AI review label. [Preview evaluation](docs/healthtech-pilot/PREVIEW_EVALUATION.md).

## Before the demo

1. ~~Hand-check the seven PwC Young Company Finance rows.~~ Done 2026-11-21: all 7 match (STATUS.md).
2. ~~Decide on Partly's "Series A" label.~~ Done 2026-11-21: a publisher-dated NZ Herald source states it (STATUS.md).
3. **Rehearse the 3-minute path** in the README on a fresh `healthtech_demo.py` database.

## Next 4–6 weeks: data, not thresholds

4. **Archive every cited URL.** Add a Wayback or hashed-text `archived_capture` witness for each source. Re-source the remaining dead link (HiNZ, for HeartLab). Both Kindrik links were replaced on 2026-11-21.
5. **First live comps.** Add witnessed workflow and buyer features (modality, clinical user, output, buyer, procurement path) for the 12 healthtech entries, until at least one subject clears the existing bars. The "Why no comps yet" panel shows which fields are missing. Do not change the thresholds.
6. **Grow the cohort toward the gate:** 150 companies, 30 primary outcomes, and unknown plus lost below 25%. Use public portfolio pages, register closures and hand-read announcements only (see DATA_USE.md). Report coverage by vintage and sector as it grows.

## Engineering, after the demo

7. **Upgrades, one PR each, behind the full suite:** Playwright 1.65 (then drop the `ubuntu-24.04` pin), FastAPI and Starlette 1.x, TypeScript 7.
8. **Move hard-coded mappings into the packets.** `FIXTURE_TO_COHORT` and `RESEARCH_ANCHORS` should carry their own provenance.
9. **Cache the cohort audit** per input digest, or import it into SQLite at bootstrap, instead of re-reading JSON on every request.
10. **Typing:** add pyright (basic) to CI. Annotate the precedents, similarity and evidence modules first.
11. **Retire or freeze intake** behind research mode. It is off the demo path and carries 9 browser tests.
12. **Optional historical outcome view.** Make `/workbench/outcomes` and `/gates` honour As-of, if analysts need it. They are currently labelled present-day.

## Not planned

- Lowering comps thresholds or widening the 90-day contemporaneous window.
- Showing any rate, probability or "early signal" before the gate passes.
- Bulk imports from paid databases.
- An LLM summarisation layer without witness dates and locators.
