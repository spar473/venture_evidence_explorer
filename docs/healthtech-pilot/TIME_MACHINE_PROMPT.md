# Coding-agent prompt: Time machine (backtest) mode

Written 2026-11-21 against `main` @ `090b8d0`. Paste everything below the line into the coding agent.

---

You are continuing Venture Evidence Explorer (VEE), repo `spar473/venture_evidence_explorer`, local checkout at the repo root. Work on a new branch `feature/time-machine` cut from `main` (`090b8d0`). First, commit this file as `docs: add time-machine prompt`.

## Why this phase exists

Today every subject abstains ("No real subject has comps yet", README). A visitor never sees the main feature. The time machine fixes that **without fabricating anything**. It replays a company whose outcome we already know:

1. **Freeze** the evidence at that company's entry anchor.
2. **Choose comps** only from peers that had entered before that date, scored only on features witnessed by then.
3. **Show** what an analyst could have seen then.
4. **Reveal** the company's actual dated path afterwards.

This is FiveThirtyEight CARMELO's idea (historical comparables → range of careers) and it is also COMPS_METHOD §7 validation, made visible.

## Facts about the current data (verified 2026-11-21; re-check before you start)

- Cohort A (`backend/cohort_audit.run_audit()`): 55 included companies across 33 raw sector labels. Primary statuses: 2 reached, 1 closed, 9 observed with no outcome, 10 lost, 33 unknown.
- Known-outcome subjects and their entry anchors:
  - `public_partly`: entry 2020-10-08 (day). Pre-Series A 2021-10-12. Series A 2022-12-13 → **reached**.
  - `public_supie`: entry 2021-11-09 (day). Voluntary administration 2023-10-30, liquidation 2023-11-09 → **closed**.
  - `discovery_halter`: entry 2016-12 (month). Series A 2018-01 → **reached**. Only about 9 cohort companies entered before it, so Halter is a **stretch** subject: run it, but expect it to abstain.
- None of the three has a witnessed entry snapshot. `research/healthtech-pilot/witnessed-snapshots.json` has 18 profiles: 5 university subjects, 13 mostly healthtech peers.
- `backend/precedent_similarity.py` (`witnessed-gower-b0:3`) is healthtech-specific. `Clinical workflow` carries a 0.25 hard gate, and categorical fields use exact string equality. A cross-sector backtest cannot clear it, by design.

## Standing rules (unchanged, non-negotiable)

- Never fabricate. Every feature value needs `source_id`, `witness_id` and a locator passage. Missing stays missing ("?" / "Not in public record").
- No rate, probability or "% success" anywhere in the UI. The backtest shows **cases**, not rates.
- Keep `witnessed-gower-b0:3` and every existing view, test and threshold exactly as they are. The time machine adds a **new, versioned** similarity profile alongside it.
- Keep: no CDN, loopback-only, the provenance, witness and immutability contracts, and the OpenAPI contract with generated TS types.
- After each phase, run every check in README "Checks": pytest, `export_contract.py --check`, Playwright, ruff and prettier. Then open the running app (`scripts/healthtech_demo.py --serve`), check the changed views, commit and push. If a push fails on authentication, stop and give me the exact command.

## Phase 0: pre-register before you look (docs only)

Create `docs/design/BACKTEST_PREREG.md` and commit it **before** any backtest run. It fixes:

- the subject list (Partly, Supie; Halter as stretch) and their anchors;
- the peer eligibility rule:
  - peer entry anchor < subject anchor;
  - peer snapshot features must be witnessed ≤ the **subject's** anchor (strict) or within the existing contemporaneous window of the peer's own anchor (lenient);
- the `general-gower-b1:1` dimensions, weights, vocabulary and thresholds (Phase 2);
- the "what happened next" horizons (36 months from the subject's anchor);
- what counts as a hit for the internal report:
  - Did the realised path of the subject fall within the ceiling–floor span of its comps?
  - Was the typical comp's 36-month status the same as the subject's?

Thresholds may not change after the first run. If they must change, write a dated amendment in the same file explaining why, and keep both results.

## Phase 1: data (the real work; budget most of the time here)

Use only public, dated sources, paraphrase passages, and follow `DATA_USE.md`. Add a new packet `research/healthtech-pilot/backtest-snapshots.json` (or extend `witnessed-snapshots.json` with a new scope `backtest_entry`; pick one and justify it in the PR).

1. **Subject entry snapshots** for Partly, Supie and Halter, using only sources published or archived on or before each anchor. Target fields:
   - `description`, `product_type`, `buyer`, `business_model`, `sector_normalised`, `market_focus`;
   - `prototype`, `paid_pilot_or_revenue`, `full_time_team`;
   - `round_size_band`, `lead_investor_type`, `months_since_founding`.
2. **Peer entry snapshots, prioritised.** For cohort companies that entered before 2021-11-09, prefer those whose status is not `unknown`. As of today that means:
   - `public_supie`;
   - lost to follow-up: `discovery_astrix`, `discovery_cropsy`, `discovery_formuslabs`, `discovery_miruku`, `discovery_tamorx`, `discovery_zincovery`, `public_1centre`, `public_myovoltlimited`, `public_narrative`, `public_socialclub`;
   - observed with no outcome: `discovery_cetogenix`, `discovery_energybank`, `discovery_heartlab`, `discovery_respiraq`, `public_carepatron`, `public_immersve`, `public_jasper`, `public_parcelport`, `public_vidapp`.
   Then add the unknowns, newest entries first.
3. **Normalise sectors.** Add a `sector_normalised` mapping table with provenance. Merge, for example, "Cleantech" / "Clean technology" and "Healthtech" / "Healthtech software". Store the raw label unchanged next to it.
4. **Witnesses.** Every new source gets a `publisher_dated` witness or, where the page is undated, an `archived_capture` with its Wayback timestamp. Record retrieval dates.
5. Report coverage: fields filled per company, and the share of peers with ≥ 5 witnessed fields. Put it in `STATUS.md`.

**Acceptance:** at least 15 peers eligible for Partly have ≥ 5 witnessed fields, and the validator in `backend/witnessed_snapshots.py` (extended to the new scope) passes. If you cannot reach 15, stop after this phase and report the shortfall honestly. Do not lower the bar.

## Phase 2: a sector-general similarity profile

New module `backend/precedent_similarity_general.py`, `VERSION = 'general-gower-b1:1'`, reusing the scoring structure of `precedent_similarity.py`:

- **Dimensions** (weights fixed in the pre-registration):
  - Product and customer: `description`, `product_type`, `buyer`, `business_model`;
  - Market: `sector_normalised`, `market_focus`;
  - Stage evidence: `prototype`, `paid_pilot_or_revenue`, `full_time_team`;
  - Funding context: `round_size_band`, `lead_investor_type`, `months_since_founding`.
  - There is no clinical hard gate. The gate becomes: Product and customer similarity ≥ the pre-registered value.
- **Controlled vocabulary with partial credit.** Add `schema/vocabulary/general-b1.json`: each categorical field has a small tree, e.g. buyer → {consumer, business → {SMB, enterprise}, public_sector, clinician → {radiologist, GP, …}}. Similarity = 1 for the same node, 0.5 for siblings under the same parent, 0 otherwise. Normalise singular and plural forms and case first. The vocabulary is versioned and has its own tests.
- **Descriptions:** keep the IDF overlap as the default. Add an *optional* precomputed embedding similarity (a local sentence-transformers model run at packet-build time, with vectors stored in the packet). The runtime must not need the network. Ship it **only** if the ablation in Phase 4 shows it changes comp selection sensibly. Otherwise leave it behind a flag and document the result.
- Report per-dimension scores exactly as `DimensionScore` does today, so the existing "Per-dimension breakdown" UI can be reused.

**Tests:**
- vocabulary partial credit;
- singular and plural normalisation;
- b0:3 outputs are byte-identical before and after this phase;
- the general profile refuses any feature witnessed after the subject anchor in strict mode.

## Phase 3: backend endpoint

`GET /api/backtest/{company_id}?witness_mode=strict|lenient&peer_history=as_of_anchor|today`

- Builds the subject's snapshot at its entry anchor (Phase 1 data only).
- Eligible peers follow the pre-registered rule. They are ranked with `general-gower-b1:1`, then ceiling, typical and floor are selected using the existing `select_comps` logic and `MIN_PEERS`.
- `peer_history=as_of_anchor` (the **default**) returns only peer events dated ≤ the subject anchor: what an analyst could actually have known. `today` returns peer events to the present, and every such event is flagged `hindsight: true`.
- The subject's own post-anchor events are returned in a separate `reveal` block with dated events, sources and its 36-month primary status. The frontend hides this block until the user clicks.
- If fewer than `MIN_PEERS` qualify, return the abstention payload (reuse `nearest_candidates`). Abstaining is a valid backtest result.
- Export the OpenAPI contract, regenerate the TS types, and add the endpoint to `docs/research_api.md`.

**Leakage tests** (add to `tests/test_leakage_and_competing_events.py` or a new `tests/test_backtest.py`):
- no peer entered on or after the subject anchor;
- no peer feature has a witness date after the anchor in strict mode;
- `as_of_anchor` returns no peer events after the anchor;
- the `reveal` block is the only place where post-anchor subject events appear;
- a present-day page with an old printed date does not qualify as a witness.

## Phase 4: offline validation report (not shown as rates in the UI)

`scripts/backtest_report.py` runs every subject in the pre-registration plus a leave-one-out pass. For every cohort company with a witnessed entry snapshot and a non-unknown status, treat it as the subject. Write `outputs/backtest-report.json` (gitignored) and a short human summary in `docs/healthtech-pilot/BACKTEST_RESULTS.md`:

- per subject: abstained or not, the comps chosen, similarity and coverage, and the hit or miss under the pre-registered definition;
- an ablation: comps with and without vocabulary partial credit, and with and without embeddings;
- sensitivity: comp selection under ±0.05 weight perturbations per dimension. Report how often ceiling, typical and floor change.

Write the results up plainly, including misses. A small n is stated as a small n.

## Phase 5: UI, the "Time machine" page

Add a third sidebar page, **Time machine**, next to Outcome library and Precedents. Use `?page=timemachine` (extend the `page` state in `frontend/src/workbench.tsx`). Use plain analyst language throughout.

1. **Header:** a subject picker limited to the pre-registered subjects. One line of context: "It's 8 October 2020. Partly has just announced its first institutional round. Here is what was public."
2. **Step 1, the snapshot.** A compact card of the subject's witnessed fields. Each value is labelled with its "Public by" date and a source link.
3. **Step 2, the comps.** Ceiling, typical and floor cards in the CARMELO style:
   - company name, a similarity score shown as a number with a quality band ("close" ≥ 0.6, "loose" 0.35–0.6), and the top 3 matched and differing fields;
   - each card's "What happened next" mini-timeline uses `peer_history`. The toggle is labelled "Only what was known in Oct 2020" (default) / "Include what we know today". Hindsight events get a visible "hindsight" badge.
   - If the subject abstains, show the existing abstention table instead and keep the reveal available.
4. **Step 3, the reveal.** A single button, "Reveal what happened to Partly". It expands the subject's real dated path on the same clock as the comps (reuse `workbench-trajectory.tsx`), plus its 36-month status.
5. **Footer:** "Backtest case, not a forecast. Method: `general-gower-b1:1`, pre-registered on [date]", linking to `BACKTEST_PREREG.md` and `BACKTEST_RESULTS.md`.
6. Accessibility: the reveal is a real `<button aria-expanded>`, every chart has a "View as table" fallback, it works by keyboard alone, and it is usable at 390 px width.

**Playwright** (`frontend/e2e/time-machine.spec.ts`):
- the reveal content is not in the DOM before the click;
- the strict and as-of-anchor defaults are applied;
- the hindsight badge appears only in "today" mode;
- the abstention path renders for Halter if it abstains;
- no "%", "probability" or "likely" strings appear on the page.

## Phase 6: demo and docs

- README: put a new step 1 at the top of the 3-minute demo, "Time machine: Partly (0:00–1:00)", and move the existing steps down. Add one screenshot.
- Update `STATUS.md`, `NEXT_STEPS.md` and `docs/CHANGELOG.md`.
- Open a PR to `main` that summarises each phase's acceptance results, including anything that fell short.

## Out of scope for this branch

Repo hygiene, licence, visual redesign, static export and deployment. Those are tracked separately. Don't touch them here, except where the new page needs the same styles as existing pages.
