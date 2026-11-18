# Venture Evidence Explorer — current-state review

Reviewed 18 November 2026, Pacific/Auckland. **A working local pilot with three reproducible issues to fix before relying on saved-draft editing and identity-review chronology.** This was a review, not an implementation change. The original project/database were preserved.

## Findings, in priority order

### F1 — P1: a delayed save can attach another venture's form to the wrong draft

Location: `/Users/kevinnn.park/Documents/venture_evidence_explorer/frontend/src/intake.tsx:37`; draft-switch controls at line 59.

Reproduced in a rendered browser against a disposable database:

1. Open saved draft A, edit its description and save a revision.
2. Delay the save response. The saved-draft sidebar remains enabled; open draft B.
3. Release A's save response. The form still contains B, but the response unconditionally sets the saved-record pointer back to A.
4. Save again. B's name/content are appended to A's revision history; B remains unchanged.

The probe observed A becoming revision 3 named “Review fixture B”, while B remained revision 1. Immutable history retains earlier versions, but the latest record is wrong. Existing request invalidation protects comparison responses, not save responses.

Recommended correction: bind saves to an explicit editor/draft identity and request generation. A late result must not replace the active editor identity after navigation. Disable switching while a save is pending or safely reconcile its completion in the background. Guard errors and busy-state transitions too. Add a delayed-response/switch-draft regression asserting that neither venture acquires the other's content.

### F2 — P2: restoring an edit loses its saved-draft identity and can create a duplicate

Location: `/Users/kevinnn.park/Documents/venture_evidence_explorer/frontend/src/intake.tsx:25`; persistence at line 31 and save-route selection at line 37.

Open an existing draft, edit it and reload. The form values are restored from local storage, but `saved` resets to null. The restored editor offers “Save draft” and posts to the create endpoint. The probe created a second draft ID; the original remained revision 1. Switching away from the intake tab also remounts this component and loses that context.

Recommended correction: retain the draft identity and base revision alongside recoverable edits, then re-fetch/reconcile the current server revision. Keep unsaved edits if another revision exists and show a conflict instead of silently creating a new record. Preserve the retry key for an uncertain save where needed. “Start another draft” should explicitly clear the identity. Add reload/tab-return/conflict tests.

### F3 — P2: mapping chronology checks can be bypassed through an observation reference

Location: `/Users/kevinnn.park/Documents/venture_evidence_explorer/backend/research_adapter.py:226`.

The mapping validator checks retrieval chronology only when the cited evidence row is itself in `sources`. A citation to an observation is subject-checked but its source retrieval date is not followed.

The synthetic probe used a 2020-01-01 mapping decision:

| Evidence citation | Underlying source retrieved | Observed result |
|---|---|---|
| `src_rl_pricing` | 2026-11-18 | Correctly rejected: decision predates source inspection |
| `obs_rl_solution` from that source | 2026-11-18 | Dry run passed; a resolved mapping was actually stored in the disposable DB |

Recommended correction: resolve the supported evidence types through their provenance to source inspections and relevant assessment/review dates, enforcing a consistent chronology rule. A different reference type must not bypass the same date boundary. Define how source-less subject assertions can support an identity decision. Test observation/report/conclusion/requirement chains as applicable, partial dates and valid later decisions. Rejection must leave mapping documents, decisions and import rows unchanged.

**These findings were produced with synthetic fixtures only.** The live database currently has zero saved drafts, zero mapping decision documents, two proposed mappings and no human acceptance records. The probes do not establish that real records have been corrupted or accepted incorrectly. Fixes have not been applied.

## What now works

| Handover stage | Current observed state | Remaining boundary |
|---|---|---|
| Two-dossier research pilot | Adapter/dry-run accounting, additive graph storage, source/report/event distinctions, unknowns, question readiness, dossier UI and exports exist; preservation verifier passes | Brand/project mappings remain proposed; legal identity is separately unresolved. Research is not automatically projected into B0. |
| Saved new-venture intake | Append-only drafts/revisions, duplicate preview, unreviewed attributions, saved-draft comparison and accepted-only refusal are implemented | F1/F2 need correction. Draft descriptions are query input, not accepted corpus evidence. |
| Historical discovery pipeline | 274 staged leads across 27 source families, filters, detail/alias/case inspection, raw provenance, CSVs and promotion refusal exist | Zero promotions; no accepted deduplicated NZ population or complete history since 2000. Period filters use supplied outcome reports. |
| Evaluation | Frozen corpus/task manifests, blank human review materials, judgment validation, metrics gates and comparison tooling exist | Actual human judgments, factual audit, independent held-out research and usefulness/time measurements are absent. Only B0 is runnable. |
| Release reproducibility | Fresh-install records/logs now exist for Python 3.10/3.11/3.12 and Node 22/macOS bundled Chromium; current checks independently pass below | This review reused installed dependencies. Python 3.13 and Linux/remote CI remain unexecuted in the supplied record. |

## Actual database state

Read-only inspection and SQLite backup confirmed integrity `ok` and no foreign-key errors. Six applied migrations are present.

- Core retrieval directory: **10 ventures, 7 sources, 20 observations**, 7 awards and 50 proposals. No human review events.
- Research graph: **2 subjects, 34 observations, 6 sources, 6 event candidates, 6 reports, 21 unknowns, 6 readiness records**, 3 reconciliation cases, 2 access gaps, 13 requirements and 4 supported conclusions. Two proposed identity mappings; zero decision documents.
- Discovery: **274 candidate leads, 27 organisations/source families, 42 sources, 365 overlapping listings, 4 outcome reports, 2 name links and 16 unresolved cases**. These comprise 730 stored discovery records; 2,218 graph links are references, not extra ventures.
- Saved drafts/revisions: **0/0** in the live database. Discovery reviews: **0**. No genuine decisions were fabricated by this review.

The product can now stage and inspect hundreds of leads. Its comparison corpus still contains the original ten ventures. Neither staged leads nor rich dossier fields automatically become trusted comparison features. This distinction matters for the original ambition of comparing hundreds of NZ ventures across time.

## Checks independently rerun

All execution used a disposable source copy or a read-only backup of the live DB. Application dependencies were reused/copied, not freshly installed for this review.

| Check | Observed result |
|---|---|
| Baseline bootstrap | Pass; original 10-venture seed counts |
| Integrity/re-import verifier | Pass: references, unknowns, idempotent import, atomic conflict refusal and subject checks |
| Backend suite, Python 3.10.10 | **113 passed, 2 skipped**, one upstream Starlette/AnyIO deprecation warning; 18.92 seconds. Skips are Python 3.12-only paths. |
| OpenAPI/generated TypeScript | Drift check passed |
| Frontend | TypeScript and Vite production build passed; 31 modules |
| Existing browser suite, installed macOS Chrome / Node 26.12.1 | **20 passed**, 48.5 seconds; disposable server at 127.0.0.1:8184 |
| Research preservation/rollback verifier | Pass: byte-preserving dry run, lossless graph, repeat equality, conflict rollback, caller-transaction refusal, original-table/B0 preservation and accepted-only isolation |
| Frozen evaluation on the live-DB backup | Six development tasks run: two return results, four abstain. Status **not_evaluated / judgments_missing**; factual audit and intervals remain null. Result coverage is operational, not relevance. |
| Additional adversarial probes | F1 and F2 reproduced in a browser; F3 reproduced in Python with a direct-source rejection control. A separate screenshot capture also passed. These diagnostic passes confirm defects, not correct application behaviour. |
| Delivered release manifest | All **155** `REMAINING_SHA256SUMS.txt` entries matched current files |
| Preservation during review | All **166** snapshotted original files remained unchanged, including the live SQLite file; 153 source/configuration files anchor the reviewed copy |

The existing engineering report's clean-install/platform claims were read alongside its release records and fresh-install logs. They were not repeated as fresh installations here. Current backend/build/browser checks are direct observations. No remote repository, CI service or external venture source was queried.

An initial browser-probe file-writing command used the wrong working-directory-relative path and failed before creating its test file. The path was corrected in the disposable copy; the final probes above completed. This was a review harness error, not an application defect.

## Interface assessment against the project goals

The directory has a consistent, restrained table layout and clear source dates. The new navigation exposes the implemented workflows. Evidence, unknowns and withheld conclusions are materially more inspectable than in the starter.

The remaining presentation gap is information order. In the RosterLab dossier capture, almost the entire first screen is identity uncertainty and mapping audit; the product/evidence content begins near the bottom. Lead with a short attributed venture summary, intended users/customer distinction and a compact evidence timeline, keeping identity/review limitations visible but concise. Unknown date spans and targets must retain their semantics.

Discovery still exposes implementation-like strings such as `pending_review`, `source_observations`, `source_capture` and repeated stable IDs in the main table. Use readable labels and concise gap summaries, with exact IDs/raw rows available in disclosures and exports. This is a usability improvement, not a data-integrity finding.

The app remains primarily tables and textual evidence inspection. The richer visual comparison/timeline experience and a reviewed national historical corpus are not yet delivered. Review/intake/discovery/evaluation infrastructure is now ahead of the evidence curation and empirical user validation.

## Recommended next work

1. Fix F1–F3 with focused regression tests and rerun affected checks. Preserve the original seed, prior research records and B0 behaviour.
2. Improve the dossier's first screen and readable discovery labels without hiding uncertainty or changing evidence semantics.
3. Curate a bounded set of genuinely comparable alternatives and plausible distractors; collect real identity/source/relevance decisions before expanding trusted comparisons.
4. Complete independent held-out research and Linux/Python 3.13 checks when the necessary inputs/environments are available. Do not replace absent judgments with numbers.

`Fix_Prompt.md` is a ready-to-use coding handover for the three confirmed defects. `Verification_Record.json`, probe outputs, source manifest, logs and captures accompany this review. The application itself was not changed.
