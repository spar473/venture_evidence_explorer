# Retired SHA-256 manifests

These six manifests used to sit at the repository root. They recorded file digests for the handover and review packages of 17–19 November 2026. They were retired on 2026-11-21 because they no longer verify against the tree; files they list have since been edited, moved or removed. Results from the milestone assessment:

| Manifest | Lines verifying |
|---|---|
| `ENGINEERING_SHA256SUMS.txt` | 65 / 89 |
| `PILOT_SHA256SUMS.txt` | 93 / 121 |
| `RELEASE_SHA256SUMS.txt` | 27 / 45 |
| `REMAINING_SHA256SUMS.txt` | 125 / 155 |
| `REVIEW_FIX_SHA256SUMS.txt` | 135 / 161 |
| `SHA256SUMS.txt` | 18 / 28 |

They are kept unchanged as provenance records. To see them alongside the files they described, check out the commit that last changed each one (`git log -- <name>`).

Integrity is now carried by git history and CI. The handover notes and other retired agent records were removed from the current tree on 2026-11-22. They remain available in [the historical tree](https://github.com/spar473/venture_evidence_explorer/tree/090b8d0/docs/archive), alongside the context for these unchanged manifests.
