# Coding-agent prompt: Time Machine provisional preview

Written 23 Nov 2026 for branch `codex/time-machine`. Paste everything below the line into the coding agent.

---

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
