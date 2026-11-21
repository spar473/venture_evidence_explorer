Superseded by [docs/design/COMPS_METHOD.md](../../design/COMPS_METHOD.md) on 21 Nov 2026.

# Copy-paste prompt: Precedent & Outcome Workbench (v2)

Paste everything below the line into the coding agent, with the `venture_evidence_explorer` folder connected. This replaces the earlier draft of this file.

---

You are continuing Venture Evidence Explorer (VEE) in `healthtech-checkout/` (repo `spar473/venture_evidence_explorer`).
- Current branch: `implementation/healthtech-pilot`, last commit `3f0905e`, in sync with origin.
- `main` is still the old, unrelated baseline (`bcca61e`); Phase 0 replaces it.
- Uncommitted design docs are waiting in `docs/design/` and `docs/healthtech-pilot/WORKBENCH_PROMPT.md`.

## Goal

Turn VEE into a **Precedent & Outcome Workbench**. An analyst picks an early NZ venture and sees:
- its **ceiling, typical and floor comps** (NBA player-comp style), taken from NZ precedents matched at a comparable stage;
- what those companies looked like then;
- what happened next, including stalls and closures;
- which evidence is missing.

Probabilities stay locked until the cohort gates pass.

## Read first (authoritative, in this order)

1. `docs/design/TARGET_UI.md`: navigation, page contents, visual system, charts, accessibility.
2. `docs/design/COMPS_METHOD.md`: anchor events, snapshot features, per-dimension Gower similarity, the peer-set rules, how ceiling, typical and floor are chosen, the gated probability estimator (kernel-weighted competing risks, n_eff, shrinkage), validation, and cohorts A/B/C.
3. `docs/design/target-ui/*.dc.html`: static layout references (Main = Precedents › Overview, EvidenceMatrix = Precedents › Evidence, OutlookGoal = future Outlook, OutcomeLibrary). Use them for layout only. Never ship their placeholder values, `[n]`, `[Closest closed peer]`, or anything marked "Sample".
4. `docs/healthtech-pilot/NEXT_PHASE_PLAN.md` (outcome rules, statuses, witnesses, gates), `STATUS.md`, `PUBLIC_DATA_LIMITS.md`.
5. `docs/architecture.md`, `docs/research_api.md`, `frontend/src/main.tsx`, `research.tsx`, `reference-pool.tsx`, `healthtech.tsx`, `backend/retrieval.py`, `backend/cohort_follow_up.py`.

## Standing rules

- **Never fabricate.**
  - No rate, probability or "% success" anywhere in the UI until a gate passes **and** the validation in COMPS_METHOD §7 succeeds.
  - Missing evidence is "?" or "Not in public record". "No" requires explicit dated evidence.
- **Charts plot only real dated events.** Partial dates become interval bands. Comps are chosen only from inside the top-k peer set.
- **Keep everything that exists.** Old tabs move behind `?mode=research`. Delete no backend code or tests.
- Keep the no-CDN rule (self-host fonts), plus the provenance, witness and immutability contracts.
- **After each phase:**
  - run `python -m pytest -q`, the Playwright suite, the frontend build, `scripts/verify.py`, `scripts/check_migrations.py` and `scripts/export_contract.py --check`;
  - open the running app and check the changed views;
  - commit with a descriptive message and push.

## Autonomy: keep going

Run all phases (0–6) in one continuous session **without asking me for confirmation**. When a judgement call comes up, choose the option most consistent with these docs, record it in a "Decisions" section of `docs/healthtech-pilot/STATUS.md` (date, decision, reason, alternative), and carry on.

**Stop and ask me only when:**
1. a push or GitHub step fails on authentication or branch protection (give me the exact command or setting);
2. `--force-with-lease` refuses the `main` update (someone changed `main`);
3. tests stay red after two genuine fix attempts and the cause is outside your change;
4. a step would change a frozen outcome definition, gate threshold or status rule in NEXT_PHASE_PLAN.md;
5. a step needs data only I have (e.g. the UoA cohort CSV), or a new paid API, credential or network dependency at runtime.

**Never stop** for routine choices: naming, layout details, which test to add, library versions inside the lockfile, the order of sub-tasks.

## PHASE 0: data correction and design docs (on `implementation/healthtech-pilot`)

1. Commit `docs/design/` (TARGET_UI.md, COMPS_METHOD.md, target-ui/*) and this prompt file.
2. **Halter is misclassified** as `observed_no_outcome`. Public sources:
   - NZ Herald, 29 Mar 2023: Halter's Series A in 2018 raised $7m (Beck, Founders Fund, K1W1, Promus).
     https://nzherald.co.nz/the-country/news/smart-cow-start-up-halter-defies-venture-capital-drought-with-85m-raise-reveals-early-uptake/UA4PTXED6ZDTXLM4OP3GOEKZX4
   - The Press, 10 Jul 2018: $8m from Data Collective.
     https://www.pressreader.com/new-zealand/the-press/20180710/281908773905264

   Entry is Dec 2016, so the horizon ends 2019-12-31.
   - Add the sourced Series A event with its date precision and witness, then re-audit. The primary status must become `reached_outcome`.
   - The Oct 2017 Promus-led seed is a candidate secondary event: `unknown` unless its pricing is proven, otherwise bounded by the 2018 Series A.
3. **Rule fix:** a company with a candidate financing event inside its window whose terms are unresolved cannot be `observed_no_outcome`; it is `unknown`. Add a test.
4. Re-check every company currently `observed_no_outcome` (primary and secondary) with one targeted search for lettered or priced rounds inside its window. Record each search and report the before/after counts in STATUS.md.
5. Push, then **replace `main` with this branch** (I have approved this). `main` (`bcca61e`) and this branch have unrelated histories, so a normal PR cannot work. Archive the old `main`, then point `main` here, keeping full history (no squash):
   ```sh
   git fetch origin
   git tag archive/main-baseline origin/main
   git push origin archive/main-baseline
   git push --force-with-lease=main:bcca61e origin implementation/healthtech-pilot:main
   ```
   Verify with `git fetch origin && git merge-base --is-ancestor <Phase 0 commit> origin/main`. `implementation/healthtech-pilot` stays as the frozen demo branch.

## PHASE 1: new branch and navigation

1. Create `implementation/precedent-workbench` from `origin/main` and push it. All later work happens on this branch.
2. Default navigation, per TARGET_UI.md:
   - two top-level tabs, **Precedents** (home) and **Outcome library**;
   - Precedents has the sub-tabs **Overview · Evidence · Outlook** (Outlook carries a lock icon while gated);
   - a sidebar watchlist with the five university projects;
   - a sidebar footer with "Research mode" and the as-of date.
3. `?mode=research` shows the old tabs unchanged (Explore ventures, Find comparisons, Add venture, Discovery queue, Data & exports, full dossier audit).
4. Apply the visual system: tokens, self-hosted Inter and Space Grotesk, and status encoding with shape plus colour.
5. Update the Playwright tests for the new navigation, and keep the old-tab tests running in research mode.

## PHASE 2: similarity and comps backend (COMPS_METHOD §1–5)

1. **Anchor events:** derive anchor dates (with precision and intervals) for `first_institutional_round`, `first_provider_or_clinical_study`, `first_regulatory_decision` and `first_paid_customer` from stage events and observations.
2. **Snapshot features at an anchor**, using witnessed sources only (reuse the witness contract and its trigger), across the five dimensions. Missing stays missing.
3. **Milestone checklist** endpoint: Yes / No / ? per milestone, with claim IDs. Unit-test that "No" requires explicit evidence.
4. **Similarity:**
   - per-dimension Gower similarity, with coverage;
   - text similarity from a small local sentence-embedding model if one can be added to the lockfile without network access at runtime; otherwise B0 IDF overlap as the text component;
   - α weights fixed in a versioned config;
   - similarity version recorded in every response.
5. **Peer set and comps:**
   - top-k with minimum similarity and minimum coverage; abstain below 3 peers;
   - ceiling, typical and floor chosen by the outcome ladder **within the top-k only**;
   - when there is no verified closure, return the "No verified closure among the closest peers" flag;
   - unknown peers are listed but never chosen.
6. **API:** `GET /api/precedents/{subject_id}?anchor=…&as_of=…` returns the peers, the per-dimension similarity, the three comps with reasons, not-alignable peers and abstentions. Regenerate the API contract.
7. **Tests:** deterministic fixtures for similarity, coverage, tie-breaks, the within-top-k rule, abstention and witness enforcement.

## PHASE 3: Precedents › Overview (improvements #1 and #2)

1. **Interactive trajectory chart** (React + SVG):
   - keyboard-focusable marks;
   - tooltip with company, event, date and precision, and source; click opens the evidence drawer;
   - a "View as table" toggle;
   - the 36-month window band;
   - a Curated / Similar cohort toggle.
2. **"Align at" selector** that re-aligns x = 0 per peer. Peers without the anchor event appear as "Not alignable", with the reason. Partial-date anchors produce bands.
3. **Ceiling, typical and floor comp cards**, each with similarity by dimension, why it matches, where it differs (or what stalled), the same-stage snapshot or the withheld reason, and an evidence link. Add an "All N similar peers" list.
4. **Milestone checklist** panel with derived diligence questions.
5. **Locked Outlook card**, with gate progress read live from the cohort audit.

## PHASE 4: Outcome library (improvement #3)

1. Filters, tiles and the six-status bar.
2. The swimlane, with interval bands, "unresolved" labels for intervals straddling the window, post-window closures labelled "primary unknown", and pagination.
3. Story cards, and entries by vintage with the denominator.
4. **Cohort comparison panel:** healthtech/medtech against all other sectors, as status counts with denominators. "Rates locked" until a gate passes.

## PHASE 5: Precedents › Evidence and › Outlook

1. **Evidence matrix:**
   - the subject row pinned;
   - witness badges, and hatched cells for missing values;
   - the time toggle, enforced against each row's anchor through the witness contract;
   - the claim panel, with "Dispute claim" as an append-only review event.
2. **Outlook (locked):**
   - live gate progress, PUBLIC_DATA_LIMITS rendered in the app, and the permissioned data that would unlock it;
   - implement the gated estimator from COMPS_METHOD §6 (kernel-weighted Aalen–Johansen, n_eff, shrinkage, bootstrap interval) **in the backend only**, unit-tested on synthetic fixtures;
   - the UI never renders its output while the gates are closed. Add a test that asserts this.

## PHASE 6: Venture Frame integration and wrap-up (improvement #4)

1. "Export screening note" extends the existing Venture Frame measurement draft with the subject, the anchor, the comps with their similarity breakdowns, the checklist values with claim IDs, and the as-of date. Test the round trip.
2. Update the README pitch, demo path and screenshot, and update STATUS.md.
3. Open a PR from `implementation/precedent-workbench` to `main`, with a summary, screenshots, test results, limitations and the Decisions log. **Do not merge**; I will merge it with "Create a merge commit".

## LATER (do not start in this run)

- **Cohort B: UoA programme entry.** Use the complete public Velocity finalist lists for 2020 and 2023 from my earlier UoA venture dataset (2019–2026, 194 identities). If that CSV is not in the repo, ask me for it. Apply the same follow-up and status rules.
- **Cohort C:** healthtech deployment outcome (FORECAST_FEASIBILITY.md).
- **Validation and display of probabilities:** only after gates pass, per COMPS_METHOD §7.

Work through the phases in order without pausing between them. Commit and push at every verified phase boundary, so that if the session or usage runs out, the next session can resume from STATUS.md. At the very end (or at a stop condition above), give me a summary of at most 10 lines: phases completed, counts changed, tests run, decisions made, next step.

**If you are resuming:** read STATUS.md and `git log`, then continue from the first incomplete phase.
