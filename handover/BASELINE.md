# Baseline and branch layout

- Repository: `spar473/venture_evidence_explorer` (private).
- `main`: original published baseline, retained as the default branch.
- `baseline/initial-release`: annotated Git tag identifying that original snapshot.
- Original commit: `cb00b27571fbff6e6972a3643fbe2900f9716283` (`Initial commit`).
- `implementation/vee-workbench`: current application implementation and the complete desktop handover.

`main` is a conventional default branch name. The meaningful baseline tag identifies the starting point without rewriting a published root commit or breaking existing clones. The initial commit message itself has not been rewritten; a request to rename that message or the default branch needs an explicit choice because those are different Git operations.

Implementation and handover packaging are separate commits. Publishing uses `[skip ci]` in their messages to retain the earlier instruction not to trigger remote CI during handover. The configured workflow is included; archived local test passes are not represented as a new GitHub Actions result. No merge or deployment is performed.

The Mac application directory remains intact. This Git checkout was assembled separately from the existing GitHub history, preserving all original tracked baseline files. Restore the tracked handover snapshot into an ignored working location on the new desktop before running the app.
