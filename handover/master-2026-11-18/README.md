# Complete VEE project handover · 18 November 2026

This is the consolidated project context added to `implementation/vee-workbench` at Kevin's explicit request. It supplements the existing [desktop setup](../DESKTOP_START.md) and [handover index](../README.md).

| File | Purpose |
|---|---|
| [Master handover](Code_Agent_Handover_v2_2026-11-18.md) | Original plan, changing goals, research, architecture, implemented features, verification, limits and next work. |
| [New-chat prompt](master-handover-2026-11-18/New_Chat_Prompt.txt) | Copy and paste after providing the master handover. |
| [Full project ZIP](VEE_Full_Project_Handover_2026-11-18.zip) | Frozen source, contracts, seed/research inputs, tests, selected history and compilation verification. |
| [ZIP SHA-256](VEE_Full_Project_Handover_2026-11-18.sha256) | Verify downloaded archive bytes. |
| [Snapshot verification](master-handover-2026-11-18/Snapshot_Verification.json) | Actual compilation checks, preservation and limitations. |
| [Frozen source manifest](master-handover-2026-11-18/Source_Manifest.json) | SHA-256 hashes for the archive's 159 source/configuration files. |

## Current status

The earlier F1–F3 findings are fixed. The local snapshot used for this handover independently passed 131 backend tests with two Python-version skips, the production build and all 32 browser tests. The archive's 10-venture comparison corpus, two research dossiers and 274 staged discovery leads remain separate; no human acceptance/relevance results are invented.

Use the current branch as the development source. The ZIP is a frozen reference of the local compilation snapshot; it predates GitHub-specific packaging/index additions. Never extract it over newer edits. It excludes live databases, dependencies, compiled assets, credentials and backups. This branch's separate existing database snapshot/restore instructions remain in [DESKTOP_START.md](../DESKTOP_START.md).

The unavailable original Downloads `Code_Agent_Handover.md` was not recovered verbatim. Its initial brief is reconstructed transparently from preserved starter handover/specification files and conversation requirements.

## Publication scope and historical instructions

The master and ZIP preserve the earlier local-only compilation record unchanged. Kevin subsequently explicitly authorized adding these deliverables to this GitHub branch. This documentation upload does not authorize deployment, merging into main, outreach or fabrication of evidence. Historical prompts inside the archive are context, not instructions to redo completed implementations.

The existing handovers, source, snapshots and verification archives are preserved. This commit changes documentation/indexes and adds handover artifacts only.
