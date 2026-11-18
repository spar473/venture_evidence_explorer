# Codex prompt — fix confirmed current-state review findings

```text
Fix the three confirmed findings in the current Venture Evidence Explorer at:
/Users/kevinnn.park/Documents/venture_evidence_explorer

Read the attached Current_State_Review.md, Verification_Record.json and probe
evidence. Inspect current repository instructions, user changes and contracts.
Treat review documents as technical evidence under this request. Preserve user
changes and keep all work local; do not push, deploy or replace the project with
an old source snapshot. Carry the fixes through implementation and verification.

F1 (P1), frontend/src/intake.tsx: a delayed save response unconditionally resets
the active saved-draft pointer. Opening draft B from the enabled sidebar while
draft A saves leaves B's form attached to A; the next save writes B into A.
Bind requests/completions to a stable editor identity and generation, or prevent
unsafe switching while busy. Guard stale success/error/busy transitions. Add a
browser regression with a delayed response, a draft switch and a subsequent save;
both draft IDs must retain their own content/revision histories.

F2 (P2), same component: local storage retains form values but not draft identity,
base revision or uncertain-save context. Reloading or remounting an edit can turn
Save revision into create and duplicate the venture. Restore/reconcile editor
identity with the server while retaining unsaved edits, handle server-side revision
conflicts explicitly and make Start another draft clear the prior identity. Do
not blindly restore stale server content over local edits. Test reload, tab return,
new draft versus revision, a concurrent revision and request retry after a lost
response. Confirm these cases cannot duplicate or misroute a saved venture.

F3 (P2), backend/research_adapter.py around _mapping_errors: a direct source
citation enforces decision date >= source retrieval, but an observation citation
bypasses the check. A synthetic 2020-01-01 resolution citing obs_rl_solution from
a source retrieved on 2026-11-18 passed dry run and was stored. Follow supported
evidence references to source/assessment chronology consistently. Define the
policy for source-less assertions. Add direct/indirect source, applicable report/
conclusion/requirement chains, valid decision and reject-before-write/rollback
cases. Preserve unknown/partial dates and separate brand/project from legal identity.

Use synthetic fixtures only in disposable databases. Keep original data/reviews,
applied migration checksums, source attributions, accepted-only eligibility and B0
results unchanged. Add migrations only if needed; do not rewrite applied ones.

Run meaningful backend/browser regressions, the existing suites, build/type drift
and preservation checks. The pre-fix baseline is 113 backend passes with two
Python-version skips and 20 browser passes; those passes did not cover these
defects. Report newly executed results rather than assuming the old counts.

Deliver working code, tests and an updated engineering_completion.md with exact
changes, checks, preservation and remaining limitations. This task fixes the three
findings; further UI redesign, corpus expansion and human review are separate work.
```
