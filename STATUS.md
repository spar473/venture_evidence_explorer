# Data status

Last checked 2026-11-21 against `main` 6f2e1bd. This file records the pre-demo data checks and open data decisions. **No packet in `research/` was changed by these checks, and the audit counts are unchanged.**

Current audit (`run_audit()`, as of 2026-11-21, 55 included entries):

| Endpoint | Reached | Closed first | Exit first | Observed, no outcome | Lost | Unknown |
|---|---|---|---|---|---|---|
| Primary (Series A or later, 36 months) | 2 | 1 | 0 | 9 | 10 | 33 |
| Secondary (next priced equity round) | 2 | 1 | 0 | 5 | 6 | 41 |

The outcome gate stays withheld: fewer than 150 companies, fewer than 30 outcomes, and coverage below requirement.

## Pre-demo checks

### PwC Young Company Finance rows: pending hand check

Seven entry rows rest on PwC YCF PDFs: Halter (2019 p.12), Tiro Lifesciences (2019 p.19–20), Firstcheck (2017 p.2; 2019 p.6), Inhibit Coatings (2020 p.3), TDRI (2019 p.5), Koti Technologies (2019 p.21, 25, 26) and Social Club (2017 p.1; 2019 p.6). pwc.co.nz refuses automated access and serves the PDFs only as downloads, so these rows have **not** been re-verified. Check them by hand: open each PDF, confirm the date, label, round number and location on the cited page, and note the result here.

### Partly Series A: label is inferred, not stated

- Source: Idealog, 16 Dec 2022 (`partly_idealog`). Re-read on 2026-11-21.
- What the article says: Partly raised $37 million from funds including Octopus Ventures and Blackbird Ventures, and is "now valued at near $180 million". The words "Series A" do not appear anywhere in it.
- What we store: `partly_priced_series_a` has `kind: series_a` and `round_label: "Series A"`. The claim text says the article "reports a completed Series A", which overstates the source.
- Framework rule: `validate_event` requires the publisher's exact label for a classified round. An unlabelled NZ$5m+ priced round with an institutional lead is a `series_a_equivalent`, and that kind is not a primary outcome.
- **Effect if corrected** (computed on a scratch copy, not applied):
  - Primary: reached 2 → 1, unknown 33 → 34.
  - Secondary: reached 2 → 1, unknown 41 → 42.
  - The gate is unaffected.
- **Decision needed.** Either find a dated source that uses the label "Series A" (Octopus or Blackbird announcements are the obvious places), or reclassify the event as `series_a_equivalent`. This changes data and outcome counts, so it waits for the owner.

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
  - A NZ$30m Series B led by Blackbird Ventures, announced by First AML on 2 Nov 2021 (firstaml.com/resources/series-b-funding, live).
- Neither source discloses a share price, a valuation or priced terms. The search also found no corroborating register filing.
- Rule: `lettered_round_status` counts a lettered round as reached only when `instrument == priced_equity`. A labelled round with unspecified equity stays `unknown`, by design. Unknown is never converted to "No".
- **Why it stays unknown:** no public source shows the Series A or Series B as priced equity. Adding the Series A as an `equity_unspecified` event would not change the status, so nothing was applied.
- What would change it: a source that states a valuation or price per share for either round. The 2021 Series B is the likelier one.

### Dead links found in the assessment

| Source ID | URL state | Live replacement |
|---|---|---|
| `firstaml_kindrik_2021` | 404 | First AML's own Series B announcement (2 Nov 2021), firstaml.com/resources/series-b-funding. It says the round is NZ$30m and Blackbird-led, with no price. |
| `partly_counsel_2021` | 404 | None found yet |
| HiNZ May 2019 (HeartLab entry features) | 404 | None found yet |

Re-sourcing these is data work, so it is listed here and not applied.

## Decision log

- **2026-11-21 · As-of scope: labelled, not wired.** `/api/workbench/outcomes` and `/api/workbench/gates` still ignore the precedent As-of date. The Outcome library, the sidebar footer on that page, and both "Outcome rates locked" cards now say "present-day". Making the audit as-of aware would mean re-running the frozen classification at arbitrary cutoffs, a larger change that touches the outcome rules, so the smaller labelling change was taken. Revisit after the demo if analysts need historical cohort views.
- **2026-11-21 · Default landing.** The workbench now opens on the Outcome library. `/?page=precedents` opens the precedent workbench directly.
- **2026-11-21 · Abstention explained, thresholds unchanged.** When comps abstain, the precedent response returns up to three nearest candidates with their per-dimension breakdown and missing fields. They are not comps, and no outcome is attached.
