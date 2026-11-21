# Next steps

Updated 2026-11-21, after the pre-demo polish sprint. These are in priority order. Data decisions waiting on the owner are listed in [STATUS.md](STATUS.md).

## Before the demo

1. **Hand-check the seven PwC Young Company Finance rows** (Halter, Tiro Lifesciences, Firstcheck, Inhibit Coatings, TDRI, Koti Technologies, Social Club), and record the result in STATUS.md. pwc.co.nz blocks automated access.
2. **Decide on Partly's "Series A" label.** The source does not use that label. Either find a dated source that does, or reclassify the round as `series_a_equivalent`, which moves primary reached from 2 to 1.
3. **Rehearse the 3-minute path** in the README on a fresh `healthtech_demo.py` database.

## Next 4–6 weeks: data, not thresholds

4. **Archive every cited URL.** Add a Wayback or hashed-text `archived_capture` witness for each source. Re-source the three dead links (HiNZ, and Kindrik for Partly and First AML; First AML's own Series B page is a live replacement).
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
