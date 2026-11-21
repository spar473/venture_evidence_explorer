# Data status

Last updated 2026-11-22. This file records the pre-demo data checks and open data decisions. The outcome audit below remains frozen at 2026-11-21.

## Time Machine: preregistered, data gate not met

The protocol was committed as `d0c7c27` before any Time Machine scoring run. See [preregistration](docs/design/BACKTEST_PREREG.md) and [coverage checkpoint](docs/healthtech-pilot/BACKTEST_COVERAGE.md) for exact rules, sources, input digests and the full Partly research queue.

| Subject | Date-eligible earlier peers | Peers with ≥5 confirmed strict fields | Peers that could clear after proposal review | Subject confirmed / proposed fields |
|---|---:|---:|---:|---:|
| Partly | 32 | 0 | 2 | 0 / 0 |
| Supie | 39 | 0 | 2 | 0 / 6 |
| Halter | 8 | 0 | 0 | 0 / 0 |

Twenty field extractions for CodeLingo, Social Club, Narrative and Supie are recorded as **proposed**, with sources, locators and normalisation rationale. No human confirmation is claimed. CodeLingo has five proposals and Social Club six; Narrative has three. Supie is a subject and is not an earlier peer for Partly.

The fixed Phase 1 gate requires **15 Partly-eligible peers with at least five confirmed strict fields each**. It is not met. Even confirming every current proposal would leave thirteen more covered peers to research. This is the coverage of this research pass, not proof that the remaining historical evidence does not exist. No general matcher, Time Machine endpoint, backtest result or UI is released. The existing app's source packets and thresholds are unchanged.

Partly's current NZ Entrepreneur page shows a 2021 update, so it was excluded from the 2020 snapshot. Scoop and archive access were unavailable through the research tool; no original version was inspected. Halter has no qualifying pre-entry source in this pass. A later biography cannot fill its 2016 snapshot.

Sector normalisation separately preserves all 33 raw labels and their source records: 31 editorial mapping proposals, with `Foodtech` and `Software & Services` still unresolved. These mappings do not count as historical evidence. Reproduce the audit with `.venv/bin/python scripts/audit_backtest_coverage.py --output outputs/backtest-coverage.json`; `--require-gate` exits 1 until the unchanged data bar passes.

The first round of checks, against 6f2e1bd, changed no packet. The PwC rows were then hand-checked (all match), and a follow-up data-hygiene change re-sourced three events in `cohort-follow-up.json` through the sourced-event path: Partly's Series A, Partly's pre-Series A and First AML's Series B. **The audit counts are unchanged.**

Current audit (`run_audit()`, as of 2026-11-21, 55 included entries):

| Endpoint | Reached | Closed first | Exit first | Observed, no outcome | Lost | Unknown |
|---|---|---|---|---|---|---|
| Primary (Series A or later, 36 months) | 2 | 1 | 0 | 9 | 10 | 33 |
| Secondary (next priced equity round) | 2 | 1 | 0 | 5 | 6 | 41 |

The outcome gate stays withheld: fewer than 150 companies, fewer than 30 outcomes, and coverage below requirement.

## Pre-demo checks

### PwC Young Company Finance rows: hand-checked, all match

Checked 2026-11-21 against PDFs the owner downloaded by hand: YCF 2017 Results, YCF deals 2019 and YCF deal data 2020, the same files as the stored source URLs. Each cited page was read and compared with the stored date, label, round number, location and named investors.

| Company | Cited row | PDF shows | Result |
|---|---|---|---|
| Halter | 2019 p.12, Dec-16 | Dec-16 · Auckland · Seed · round 1. The sector cell reads "Health Care Equipment & Services"; the stored passage already notes this and reconciles the sector to agritech. | ✓ |
| Tiro Lifesciences | 2019 p.19, Aug-14; p.20, Nov-14 | Aug-14 · Christchurch · Seed · round 1. Nov-14 · Seed · round T1. | ✓ |
| Firstcheck | 2017 p.2, May-17; 2019 p.6, May-17 | 2017: May-17 · New Plymouth · Seed · round 1 · lead Launch Taranaki, syndicate Launch Taranaki, Angel HQ, MIG and SCIF. 2019: May-17 · Seed · round 1. | ✓ |
| Inhibit Coatings | 2020 p.3, Dec-19 | Dec-19 · Wellington · Seed · round 1 · syndicate Enterprise Angels, AngelHQ, Ice Angels and SCIF | ✓ |
| TDRI | 2019 p.5, Nov-18 | Nov-18 · Christchurch · Seed · round 1 | ✓ |
| Koti Technologies | 2019 p.25, Jun-12; p.26, Nov-12; p.21, Mar-13 | Jun-12 · Christchurch · Seed · round 1. Nov-12 · Seed · round T1. Mar-13 · Seed · round T1. | ✓ |
| Social Club | 2017 p.1, Mar-17; 2019 p.6, Mar-17 | 2017: Mar-17 · Auckland · Seed · round 1 · lead Ice Angels, with private investors. 2019: Mar-17 · Seed · round 1. | ✓ |

**Result:** 7 of 7 companies match, and all 17 cited rows agree with the stored claims. No sourced-event correction was needed and no count changed.

The same tables also show later rounds, which do not affect the entry decisions: Halter Oct-17 round 2 (Start-up), Tiro Apr-16 round 2, Firstcheck Dec-17 round 2 and Jul-19 round 3, Koti Nov-14 round 2 and Feb-15 round 3, and Social Club Dec-17 round 2.

### Partly Series A: label now stated (decision closed)

- **Resolved 2026-11-21.**
  - New source: NZ Herald, "Partly, founded by ex-Rocket Lab engineer, closes largest Series A raise in NZ history" (`partly_herald_2022`). It is publisher-dated 13 Dec 2022 (03:30 UTC) and was read on 2026-11-21.
  - Both the headline and the opening paragraph name the round a **Series A**: $37 million raised at a $180 million valuation. The article is behind a paywall below the lead, but the label, amount and valuation all appear in the visible headline and lead.
- **Event change.**
  - `partly_priced_series_a` now cites the Herald, with a publisher-dated witness.
  - The date moves from 2022-12-16 (Idealog) to 2022-12-13 (`completed_at_announcement`, the Herald's publication day).
  - The label "Series A" is unchanged and is now stated by the source.
  - The next-round proof cites the Herald paragraph. Idealog (16 Dec 2022, `partly_idealog`) stays in the packet as corroboration of the raise and valuation, although it never uses the label.
- **Effect.** Primary and secondary status are unchanged (reached). The secondary event-time bound narrows to 2020-10-08 → 2022-12-13. Counts are unchanged.

### Toku `clinical_user = optometrist`: weak but stated

- Source: Startup Daily, 29 Jun 2021 (`ws_toku_startupdaily_2021`). Re-read on 2026-11-21.
- The article says THEIA "is expected to be available to Australian optometrists and healthcare professionals" later that year. It says the device is operated by "a technician or allied health professional". The clinical trial was at Middlemore Eye Hospital and private practices.
- The stored passage ("names optometrists as a target user group") is accurate, but the source frames it as a future audience alongside other professionals, not as the current user.
- Toku is a fixture subject, not a Cohort A entry, so no count depends on it. Comps already abstain for it.
- Suggested follow-up (not applied): widen the value to "optometrist or eye-care professional", or add the operator role as a separate witnessed feature.

### First AML: stays unknown

- Entry: Mar 2019 seed (Flux Accelerator), so the 36-month window runs to Mar 2022.
- Rounds found inside the window, both explicitly labelled:
  - A Series A of about NZ$7.3m around Sep 2020, seen only in a headline and an aggregator listing.
  - A NZ$30m Series B led by Blackbird Ventures, announced by First AML on 2 Nov 2021 (firstaml.com/resources/series-b-funding, live). Since 2026-11-21 this announcement is the stored source for `firstaml_b_2021`, with event date 2021-11-02.
- Neither source discloses a share price, a valuation or priced terms. The search also found no corroborating register filing.
- Rule: `lettered_round_status` counts a lettered round as reached only when `instrument == priced_equity`. A labelled round with unspecified equity stays `unknown`, by design. Unknown is never converted to "No".
- **Why it stays unknown:** no public source shows the Series A or Series B as priced equity. Adding the Series A as an `equity_unspecified` event would not change the status, so nothing was applied.
- What would change it: a source that states a valuation or price per share for either round. The 2021 Series B is the likelier one.

### Dead links found in the assessment

| Old source ID | URL state | Action (2026-11-21) |
|---|---|---|
| `firstaml_kindrik_2021` (Kindrik) | 404 | **Replaced** by `firstaml_series_b_2021`, First AML's own publisher-dated announcement (2 Nov 2021). It reports NZ$30m, Blackbird-led, with no price. The event moves from 2021-11-11 to 2021-11-02. First AML stays unknown. |
| `partly_counsel_2021` (Kindrik) | 404 | **Replaced** by `partly_startupdaily_2021`, Startup Daily, publisher-dated 12 Oct 2021: "NZ$3.7 million pre-series A", led by Blackbird. The event moves from 2021-10-27 to 2021-10-12, and the claim is kept. |
| HiNZ May 2019 (HeartLab entry features) | 404 | Not yet addressed |

For both replacements, the company's follow-up review is re-dated 2026-11-21, because each review must post-date the retrieval of its sources. Each new source also has a publisher-dated witness.

## Decision log

- **2026-11-21 · As-of scope: labelled, not wired.** `/api/workbench/outcomes` and `/api/workbench/gates` still ignore the precedent As-of date. The Outcome library, the sidebar footer on that page, and both "Outcome rates locked" cards now say "present-day". Making the audit as-of aware would mean re-running the frozen classification at arbitrary cutoffs, a larger change that touches the outcome rules, so the smaller labelling change was taken. Revisit after the demo if analysts need historical cohort views.
- **2026-11-21 · Default landing.** The workbench now opens on the Outcome library. `/?page=precedents` opens the precedent workbench directly.
- **2026-11-21 · Abstention explained, thresholds unchanged.** When comps abstain, the precedent response returns up to three nearest candidates with their per-dimension breakdown and missing fields. They are not comps, and no outcome is attached.
- **2026-11-21 · Partly label.** The owner first chose to keep the "Series A" label pending. A publisher-dated NZ Herald source that states the label was then found and attached, so the round stays `series_a` and the reclassification was not needed.
