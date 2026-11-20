# Target UI: Precedent & Outcome Workbench

Status: design spec, revised 21 November 2026. Reference mockups: `docs/design/target-ui/*.dc.html` (static HTML layouts; open in a browser or read as markup). Live canvas: https://claude.ai/artifact/Ju1R9jbrQj9FuQqejfCNnv. Method for comps and future probabilities: `docs/design/COMPS_METHOD.md`.

## Purpose

An analyst picks an early NZ venture and sees:
- its **ceiling, typical and floor comps** (named NZ precedents, in the style of NBA player comps);
- what those companies looked like at the same stage;
- what happened to them next: success, stalled or closed;
- which evidence is still missing.

Outcome probabilities stay locked until the cohort gates in `docs/healthtech-pilot/NEXT_PHASE_PLAN.md` pass.

## Navigation

Two questions, two top-level tabs:

1. **Precedents** (home, venture-level): pick a venture → sub-tabs **Overview · Evidence · Outlook** (Outlook shows a lock icon while gated).
2. **Outcome library** (cohort-level): what happened across the NZ cohort.

The sidebar also has a watchlist of the five university projects and, in the footer, a "Research mode" link (`?mode=research`) plus the evidence as-of date.

| Current tab | Target |
|---|---|
| Research dossiers: dossier list, healthtech comparisons, Compare elapsed time | Precedents › Overview and Precedents › Evidence |
| NZ reference fixture, peer trajectories | Precedents › Overview (peer chart) and Outcome library |
| Explore ventures | Research mode |
| Find comparisons (B0) | Research mode. B0 remains the text baseline inside the similarity score |
| Add venture, Discovery queue | Research mode |
| Data & exports | Research mode. Each new view keeps its own CSV export button |
| (new) | Precedents › Outlook: locked, with live gate progress |

Research mode shows the old tabs unchanged plus the full dossier audit view. No code is deleted.

## 1. Precedents › Overview (`Main.dc.html`)

- **Header bar:** venture search, as-of date, "Export screening note" (Venture Frame draft).
- **Subject header:**
  - name, kind (UoA research project or company), stage and tags;
  - tiles for precedent count, cited claims and open gaps;
  - for research-stage subjects, the line "Analogy query: no verified funding round yet".
- **Sub-tab bar:** Overview · Evidence · Outlook (locked).
- **"Where comparable NZ ventures went"** trajectory chart, interactive:
  - **Align at** selector: First institutional round (default) / First provider or clinical study / First regulatory decision / First paid customer. It re-aligns x = 0 for every peer.
  - Peers without the anchor event are listed under the chart as "Not alignable", with the reason.
  - Peer-set toggle: Curated precedents / Similar cohort.
  - A 36-month window band is drawn on the chart.
- **Ceiling, typical and floor comps:** three cards chosen from the top-k peers by the rules in `COMPS_METHOD.md` §5. Each card shows:
  - its role label (Ceiling / Typical / Floor) and a status badge;
  - why it matches and where it differs (or what stalled, for the floor);
  - its **similarity by dimension** (clinical workflow, buyer and sales path, regulatory path, stage evidence);
  - its same-stage snapshot, or the reason it is withheld;
  - a link to its evidence.

  Also on this panel:
  - an "All N similar peers" link opens the full ranked list, including `unknown` peers;
  - if no verified closure is among the closest peers, the floor card says so;
  - the tool abstains if fewer than 3 peers qualify.
- **Milestone checklist** (right panel): rows are milestones, columns are the subject and each comp at its anchor.
  - Values are **Yes / No / ?**. "No" requires explicit dated evidence; "?" means not in the public record at that date.
  - Every value links to its claim.
  - Diligence questions derived from the "?" and "No" cells appear below.
- **Locked Outlook card:** live gate progress (entries vs 150; primary and secondary events vs 30; unknown + lost vs 25%), with a link to the Outlook sub-tab.

## 2. Outcome library (`OutcomeLibrary.dc.html`)

- **Filters:** sector, entry vintage, outcome (Series A or later / next priced round), cohort (A: seed-entry; B: UoA programme-entry, once built).
- **Summary tiles:** candidates reviewed, confirmed entries, verified closures, outcomes known at 36 months.
- **Six-status bar:** counts for each status. Shape and pattern encode status as well as colour.
- **"Company stories on one clock" swimlane:**
  - partial dates drawn as interval bands;
  - an interval straddling the window labelled "unresolved";
  - post-window closures labelled "primary unknown";
  - rows paginated or virtualised.
- **Story cards** with source links.
- **Entries by vintage**, with the denominator shown. Young Company Finance figures are labelled as deals, not entries.
- **Cohort comparison panel:** healthtech/medtech against all other sectors. It shows status **counts** with denominators; rates stay locked until a gate passes.

## 3. Precedents › Evidence (`EvidenceMatrix.dc.html`)

- **Rows:** the subject (pinned) plus its comps and precedents.
- **Columns:** Clinical evidence, Regulatory, Commercial use, Funding at stage, and "+ Add field".
- **Cells:** claim, citation and witness badge. Missing values are hatched and read "Not in public record" or "Not yet extracted".
- **Time toggle:**
  - "Everything known today";
  - "What was public at the same stage", enforced through the witness contract against each row's anchor.
- **Claim detail panel:** passage, publisher, dates with precision, witness, review state, open questions, "Open source", and "Dispute claim" (append-only review event).

## 4. Precedents › Outlook (`OutlookGoal.dc.html` is the future layout only)

- **Now:** a locked page. It explains each gate with live progress, renders `PUBLIC_DATA_LIMITS.md` content in the app, and lists the permissioned data that would unlock it.
- **Future** (design target, only after a gate passes and the validation in `COMPS_METHOD.md` §7 succeeds):
  - horizons of 12/24/36 months;
  - competing-risks cumulative incidence;
  - effective sample size;
  - drivers;
  - a model card;
  - the runway scenario.

  **Never ship synthetic or placeholder numbers.**

## Venture Frame integration

"Export screening note" extends the existing Venture Frame measurement draft with:
- the subject;
- the anchor event;
- the ceiling, typical and floor comps with their similarity breakdowns;
- the milestone checklist values with claim IDs;
- the as-of date.

## Visual system

- **Colours:** navy sidebar #0F1B2D; page ground #F4F6F9; white cards with 14px radius and a 1px #E2E6EC border; primary #1F4E9E.
- **Type:** Inter (body) and Space Grotesk (headings), **self-hosted** because of the no-CDN rule, or the system stack.
- **Status encoding** (shape always paired with colour):

  | Status | Colour | Mark |
  |---|---|---|
  | Reached | #0072B2 | filled circle |
  | Observed | #009E73 | open ring |
  | Closed | #D55E00 | cross |
  | Lost | #8A94A6 | dashed line |
  | Unknown | grey | hatching |

  Intervals are translucent bands.
- **Contrast:** text at least 4.5:1. Status colours are for marks only.

## Charts

- React + SVG; `d3-scale`/`d3-shape` are allowed if added to the lockfile.
- Keyboard-focusable marks.
- Tooltip showing company, event, date and precision, and source; click opens the evidence drawer.
- An `aria-label` summary and a "View as table" toggle on every chart.
- Only real dated events are plotted. Uncertain dates are bands.

## Accessibility

WCAG 2.1 AA: real controls, visible focus, targets of at least 44px, `th` scope, `aria-current` on the active tab, and a usable layout at 390px width.
