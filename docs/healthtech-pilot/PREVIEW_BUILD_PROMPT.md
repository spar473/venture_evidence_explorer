# Coding-agent prompt: Time Machine provisional preview

Written 23 Nov 2026 for branch `codex/time-machine`. Paste everything below the line into the coding agent.

---

**How this phase is judged:** the work is done only when every **blocking** check in Phase E passes and `PREVIEW_EVALUATION.md` shows the evidence. The target state is described in **Ideal outcome** at the end. Read both before you start, and build towards them rather than auditing at the end.

You are continuing Venture Evidence Explorer (VEE) on branch `codex/time-machine`. The project owner has chosen to build a **provisional preview** of the Time Machine before the strict evidence gate passes. Read **Amendment 1** at the end of `docs/design/BACKTEST_PREREG.md` first. It is authoritative for this phase. Everything else in the preregistration stays frozen.

## Step 0: commit what is already in the working tree

These files were added by the owner's review session and are not committed yet:
- `research/healthtech-pilot/backtest-review-decisions.csv` (72 field decisions; `review_kind = ai_adjudicated`, `human_confirmed = no`)
- Amendment 1, appended to `docs/design/BACKTEST_PREREG.md`
- this prompt, `docs/healthtech-pilot/PREVIEW_BUILD_PROMPT.md`

If they are not yet committed, commit them as `docs: record AI-adjudicated field review and provisional preview amendment`.

## Standing rules

- Never fabricate. Never present the preview as validated, human-confirmed or predictive. No rates, probabilities or "% success".
- Do **not** weaken the strict track. The strict gate, `--require-gate` and all existing tests keep their meaning. The preview is a second, labelled track beside it.
- Weights, vocabulary, bars, k = 12, `MIN_PEERS = 3`, subjects, anchors, evidence clocks and hit rules stay exactly as frozen.
- Keep `witnessed-gower-b0:3` outputs byte-identical.
- After each phase, run the full README check list, then open the running demo and look at the changed views. Commit, then push. If a push fails on authentication, stop and print the exact command for the owner.

## Phase A: ingest the decisions (single source of truth)

1. Add a review state `ai_adjudicated` beside `proposed` and `confirmed`. Write `scripts/ingest_backtest_review.py`, which reads the CSV and applies it to the packet:
   - `Accept` → `ai_adjudicated`, value unchanged;
   - `Correct` → `ai_adjudicated`, with `final_value` as the value and the original kept as `proposed_value`;
   - `Reject` → `rejected`, excluded everywhere;
   - `Unsure` → stays `proposed`.
   Record `decided_by`, `review_date`, `second_reading_value`, `readings_match` and `human_confirmed` on each feature.
2. The ingest is idempotent and validates that every CSV key exists in the packet and vice versa. Editing one CSV row and re-running it must change only that field. This is how the owner will adjust decisions later.
3. Extend `scripts/audit_backtest_coverage.py` to report two gates side by side: **strict** (human-confirmed, unchanged, still failing) and **preview** (AI-adjudicated). Expected preview result today: 9 Partly-eligible peers with ≥ 5 fields.
4. Tests:
   - the ingest is idempotent and changing one row changes one field;
   - `Reject` and `Unsure` never count;
   - the strict gate ignores `ai_adjudicated`;
   - the preview label is present in the audit output.

## Phase B: scorer and backtest endpoint (from TIME_MACHINE_PROMPT phases 2 and 3)

- Implement `general-gower-b1:1` exactly as frozen in §3 of the preregistration, including the vocabulary tree and partial credit. Leave embeddings out.
- Implement `GET /api/backtest/{company_id}?track=preview|strict&witness_mode=strict|lenient&peer_history=as_of_anchor|today`.
  - `track=strict` returns the gate-not-passed refusal.
  - `track=preview` uses `ai_adjudicated` fields only.
  - Every preview response carries `provisional: true` and the label text from Amendment 1.
- Expected outcomes, to be stated honestly rather than worked around:
  - **Partly abstains:** no subject evidence.
  - **Halter abstains:** no subject evidence.
  - **Supie is the only scoreable subject,** and may well abstain too, because no peer is a consumer retail business.
- Abstention is a valid result. Return the existing `nearest_candidates` payload with per-dimension scores.
- Add a **preview-only** list, `nearest_available`: the top 3 peers by similarity regardless of the bars. Each is flagged `not_a_comp: true`, with its scores and the bars it failed, so the page can show real companies without implying they qualified.
- All leakage tests from TIME_MACHINE_PROMPT phase 3 apply. Store preview runs under `outputs/preview/`, never as the preregistered run record.

## Phase C: the Time Machine page (from TIME_MACHINE_PROMPT phase 5)

Build the page as specified there (`?page=timemachine`, subject picker, snapshot, ceiling/typical/floor or abstention, reveal button, footer), with these preview additions:
- A persistent banner at the top: "Provisional preview: AI-adjudicated evidence, not human-confirmed. Strict evidence gate not passed (9 of 15 peers)."
- Every field shows a small review badge: `AI-adjudicated`, `AI-adjudicated · second reading matched`, or `Proposed`. Hovering the badge shows who decided it and when.
- When the subject abstains, show the "Why no comps yet" table, then a clearly separated section, "Nearest available, not comps", using `nearest_available`, with each failed bar visible.
- Partly and Halter appear in the picker with a one-line reason: "No qualifying evidence public by [date]".
- Playwright tests:
  - the banner is always present;
  - reveal content is absent before the click;
  - the "not comps" section never uses the words ceiling, typical or floor;
  - no "%", "probability" or "likely" strings.

## Phase D: docs

- Update `STATUS.md`, `NEXT_STEPS.md` and `CHANGELOG.md`. Add `docs/healthtech-pilot/PREVIEW_RESULTS.md`: per subject, the outcome (comps or abstention), scores and which bars failed, written plainly.
- Next-steps list:
  1. human confirmation of the 72 fields, at least the 21 archive-based ones;
  2. research 6 more Partly-eligible peers;
  3. find a pre-8 Oct 2020 Partly source;
  4. resolve the Parcelport product_type inconsistency.
- Open a PR to `main` titled "Time Machine: provisional preview", summarising each phase's results, including abstentions.

## Phase E: evaluate before you hand over

Write `docs/healthtech-pilot/PREVIEW_EVALUATION.md` with one table: criterion, result (pass / fail / not applicable), and evidence (test name, command and its output summary, or screenshot path). Claims without evidence count as fail. **Blocking** criteria must all pass. If one cannot pass, stop, leave it as fail with the reason, and say so at the top of the PR. Never weaken a test to make it pass.

### E1. Integrity (blocking)
- [ ] **Provenance walk.** An automated test renders the preview payload for every subject and asserts that every displayed field value has a source, a witness date, a locator and a review state. Values with no provenance fail the test.
- [ ] **No leakage.** All leakage tests from TIME_MACHINE_PROMPT phase 3 pass, plus one new test: with `peer_history=as_of_anchor`, no event or text dated after the subject's cutoff appears anywhere in the response except the `reveal` block.
- [ ] **Strict track untouched.** `--require-gate` still exits 1. The strict gate ignores `ai_adjudicated`. `witnessed-gower-b0:3` golden payloads are byte-identical to `main`.
- [ ] **Labelling.** The provisional banner is present on every preview screen and in every preview API response. "Nearest available" items never carry the words ceiling, typical or floor.
- [ ] **No forbidden claims.** No "%", "probability", "likely", "predict", "success rate" or "validated" anywhere in the rendered preview (checked by Playwright on the DOM text).

### E2. Method correctness (blocking)
- [ ] **Hand-checked scores.** In `PREVIEW_EVALUATION.md`, compute the `general-gower-b1:1` similarity and coverage by hand for two real pairs: Supie vs its top-ranked peer, and Narrative vs Social Club. Show each dimension. A unit test asserts that the code produces the same numbers to 3 decimal places.
- [ ] **Vocabulary.** Tests cover: identical node = 1.0; parent/child or meaningful siblings = 0.5; different branches = 0; artificial root never gives credit; unknown token treated as missing and reported.
- [ ] **Determinism.** Running the preview twice on the same inputs produces byte-identical JSON. Record the output SHA-256.
- [ ] **Adjustability.** Changing one row in `backtest-review-decisions.csv` and re-running the ingest changes exactly that field, and the audit and preview output change accordingly. Prove it in a test using a temporary copy.

### E3. What a visitor sees (blocking)
- [ ] **First screen tells the story.** At 1440×900, without scrolling, `?page=timemachine` (default subject Supie) shows four things: the banner, one plain sentence saying what happened (comps found, or no close comps and why), the subject snapshot, and the Reveal button. Commit the screenshot.
- [ ] **60-second demo path** written in the README and walked in Playwright: open the page, read the snapshot, see comps or "nearest available", reveal, open one source link.
- [ ] **Plain language.** No UI text uses: witness, witnessed, anchor, alignable, Gower, IDF, n_eff, α, snapshot scope, as-of-anchor. Those words may appear only in the method docs and in tooltips that explain them. Enforce with a Playwright text check.
- [ ] **Partly and Halter** appear with a one-line, dated reason. They are never silently missing.

### E4. Design and accessibility (blocking where marked)
- [ ] **(blocking)** axe-core in Playwright: zero serious or critical violations on the Time Machine page.
- [ ] **(blocking)** Keyboard only: reach the subject picker, the toggle, the Reveal button (real `<button aria-expanded>`) and every source link. Every chart has a "View as table" fallback.
- [ ] **(blocking)** At 390 px width there's no horizontal overflow, and the reveal and banner stay readable. Commit the screenshot.
- [ ] Uses the existing design tokens and components. No new global CSS file; new styles live with the page.
- [ ] Each comp or nearest card shows at most 3 matched and 3 differing fields. Similarity is a number plus a band ("close" ≥ 0.6, "loose" 0.35–0.6, "not a comp" below the bars), never a bare decimal.
- [ ] Empty and abstention states say why, and name the evidence that would change the result.

### E5. Engineering (blocking where marked)
- [ ] **(blocking)** The full CI matrix is green: Python 3.10–3.13, Playwright, ruff, prettier, `export_contract.py --check`.
- [ ] **(blocking)** New Python modules pass pyright (basic) with zero errors. Add pyright to CI for those modules only.
- [ ] Every new module has tests. Measure coverage on new code only and report it.
- [ ] No new runtime dependencies. If one is unavoidable, justify it in the PR.
- [ ] The backtest endpoint responds in under 300 ms (p95 of 20 calls) on the demo database. Report the number.
- [ ] Legacy views and `?mode=research` behave as before (existing tests unchanged and passing).

### E6. Documentation and reviewability
- [ ] `PREVIEW_RESULTS.md` explains, per subject in plain English: what happened, which peers were closest, which bars failed, and what evidence would change it. Write misses and abstentions as plainly as hits.
- [ ] The PR description has before/after screenshots, the E1–E5 results table, the provisional status and known gaps.
- [ ] `STATUS.md`, `NEXT_STEPS.md` and `CHANGELOG.md` are updated, and the README's 3-minute demo starts with the Time Machine.

### E7. Fresh-eyes review
Before opening the PR, review the running page and docs as two specific readers. If you can start a separate reviewer agent that has not seen the build, use it.
- **An Icehouse software engineer / data analyst.** Typical questions: how is similarity computed? What stops hindsight leaking? Who checked the facts? What happens with sparse data? Is it reproducible?
- **An Icehouse investment analyst screening a new company.** Typical questions: what does this tell me in 30 seconds? Which past company is this most like, and how did it go? How much should I trust it? Where's the source?

List each reader's top 5 questions in `PREVIEW_EVALUATION.md`, with where the page or docs answer each one. Fix what you can. List the rest as known gaps.

## Ideal outcome

**For this phase.** Someone opens the demo and lands on the Time Machine:
- The banner says plainly that this is a provisional preview built on AI-checked evidence.
- The first line says something true and specific, for example "It's 9 November 2021. Supie has just raised its first round. No past NZ venture in the pool is a close match; here are the three nearest and why they fall short."
- The snapshot shows what was public then, each fact one click from its source and date.
- They press **Reveal** and see Supie's real path on the same clock: voluntary administration, then liquidation in November 2023.
- Within 60 seconds they understand the idea: compare a young company only with what was knowable at the time, show your evidence, and don't pretend when the match is weak.
- An engineer who clones the repo can run one command to reproduce the result byte for byte, change one decision in the CSV and watch it flow through, and find every number explained in `PREVIEW_EVALUATION.md`.

**Beyond this phase, the state this preview should make easy to reach:**
1. A human confirms the 72 fields (at least the 21 archive-based ones), 6 more peers are researched, and a pre-8 Oct 2020 Partly source is found.
2. The strict audit passes. The same page then switches from "provisional preview" to the strict track by configuration alone: the banner goes, the badges read "human-confirmed", and no page code changes.
3. Partly runs as the main case, with ceiling, typical and floor comps and a reveal of its Series A.
4. The project reads as a confident, honest research tool that an Icehouse engineer would want to discuss and an analyst would actually open while screening.

**Scorecard targets** (from the 21 Nov review):

| Dimension | Before | Target after this phase |
|---|---|---|
| What a visitor sees | D+ | B: real evidence, a reveal, honest abstention |
| UX and visual design | C+ | B: plain language, first screen tells the story, accessible |
| Method and data rigour | B+ | A−: hand-checked scores, deterministic, adjustable, labelled |
| Engineering | B+ | A−: typed, tested, CI green, fast |

Report your own honest grade against each target at the end of `PREVIEW_EVALUATION.md`, with one line of evidence per grade.
