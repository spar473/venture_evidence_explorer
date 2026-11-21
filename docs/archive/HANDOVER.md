# Where `handover/` went

The `handover/` tree was removed from `main` on 2026-11-21, in the pre-demo cleanup. Nothing was deleted from history.

| What | Where |
|---|---|
| Git tag | `archive/handover-2026-11-21`, pointing at commit `a28e631` (the last commit with `handover/` on `main`) |
| GitHub Release | [archive/handover-2026-11-21](https://github.com/spar473/venture_evidence_explorer/releases/tag/archive/handover-2026-11-21) |
| Release asset | `vee-handover-2026-11-21.zip` (4,929,352 bytes, 348 files), produced by `git archive a28e631:handover` |
| Asset SHA-256 | `3db7b8c43c48c16b70a0d7b11ac604f4328c678899c56e988ae9af9506992ade` |

The tree held the 18 November handover package:
- `BASELINE.md`, `CONTINUATION.md`, `DESKTOP_START.md` and `README.md`;
- three SQLite snapshots;
- two zips and the import and verification reports;
- `inputs/current-state-review/` (its `SHA256SUMS.txt` verified 23/23);
- package manifests, including `PACKAGE_SHA256SUMS.txt`, which no longer verified.

## Restore

The tree stays browsable in git:

```sh
git show archive/handover-2026-11-21:handover/README.md
git checkout archive/handover-2026-11-21 -- handover
```

Alternatively, download the release asset and check its digest before unzipping:

```sh
gh release download archive/handover-2026-11-21 --pattern 'vee-handover-2026-11-21.zip'
shasum -a 256 vee-handover-2026-11-21.zip
```

`scripts/restore_handover_snapshot.py --from handover/snapshots/vee-2026-11-18.sqlite` works once `handover/` is restored.
