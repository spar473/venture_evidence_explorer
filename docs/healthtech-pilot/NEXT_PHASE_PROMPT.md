# Copy-paste prompt for the coding agent

Paste everything below the line into the coding agent, with the repository folder connected.

---

You are continuing work on Venture Evidence Explorer (VEE), branch `implementation/healthtech-pilot` (repo `spar473/venture_evidence_explorer`, local checkout in `healthtech-checkout/`).

## Step 0: sync the branch
- The branch has 6 local commits that are not on GitHub. `docs/healthtech-pilot/NEXT_PHASE_PLAN.md` and `NEXT_PHASE_PROMPT.md` are untracked.
- Commit those two files as `docs(healthtech): plan NZ reference pool and outcome distributions`, then push to `origin implementation/healthtech-pilot`. If the push fails on authentication, stop and tell me the exact command to run.

## Read first
1. `docs/healthtech-pilot/NEXT_PHASE_PLAN.md` (revised 20 Nov). This is the plan you are implementing. It is authoritative where it conflicts with older docs. Pay particular attention to: "What the pool represents", "Outcome rules", "Snapshot contract" and the methods-ladder gates.
2. `docs/healthtech-pilot/STATUS.md` and `docs/healthtech-pilot/FORECAST_FEASIBILITY.md` for the current state.
3. `README.md`, `docs/architecture.md`, `docs/evidence_contract.md`, `docs/research_import.md`, `docs/research_api.md`, `docs/discovery.md` for existing contracts.

## Goal of this phase
Lay the foundation for an NZ entry-cohort reference pool: companies defined by a fixed entry rule (first institutional pre-seed/seed round, 2012–2022), whatever happened to them afterwards. A Series B+-only pool is explicitly rejected because it causes survivorship bias. This session builds the schema, historical-availability proof and a 30-company **test fixture**, and shows sourced trajectories. It does **not** produce any rates or probabilities.

## Do in this session, in order
**P0 Presentation**
- Rewrite the top of `README.md` into a 5-line pitch: what the tool does, who it is for, one demo path. Move the long caveat paragraphs into `docs/METHOD.md` and link to it. Keep accuracy; cut repetition.
- Do not create any new `*_SHA256SUMS.txt` manifests or new completion-report files. Update `STATUS.md` instead.

**P1 Schema, availability witnesses and test fixture**
- Additive, checksummed migration for:
  - pool companies (linked to existing venture identities and aliases);
  - stage events, using the vocabulary, date-precision rules and outcome definitions in the plan (store round labels exactly as the source gives them);
  - the six status categories (`reached_outcome`, `closed_before_outcome`, `acquired_or_ipo_before_outcome`, `observed_no_outcome`, `lost_to_follow_up`, `unknown`), kept distinct;
  - **source availability witnesses** (`publisher_dated` or `archived_capture` with capture timestamp);
  - as-of snapshots whose features reference witnessed sources only.
- Automated tests:
  - a snapshot cannot reference a source whose witness date is after the snapshot date, and a present-day page with an old printed date does not qualify;
  - closure requires positive evidence;
  - no rate or curve endpoint accepts fixture-only data.
- A research packet plus importer path (reuse the existing dry-run → apply pattern) for a **30-company test fixture** across sectors. Include the existing healthtech references (Volpara, Formus Labs, Toku Eyes, Alimetry, Wellumio), several well-known Icehouse portfolio companies (e.g. Halter, Sharesies, Hnry, Tracksuit) and **at least 8 quiet cases** (stalled at seed, verified closure, or lost to follow-up). Every event needs a source URL, publication date, retrieval date, passage and witness where available. Mark the packet as `fixture`, not cohort.
- Public sources only. No automated extraction from Dealroom, Crunchbase, PitchBook or LinkedIn. A missing event is censored or unknown, never failure.
- Research-stage subjects (Neurofanos, Automated Breast MRI Reporting, IVF Decision Support Tool, VistaVision, PulseMap) stay **analogy queries**: they get peers and peer trajectories, but no position on the cohort time axis and no rate statements.

**P1 UI (if time remains)**
- **Trajectory strip:** months since entry × stage for named fixture companies and a subject's peers from the existing B0 retrieval. Closures end in a cross; censored lines end in an open circle.
- **Coverage panel:** companies by status, sources by witness type, companies lacking a witnessed entry snapshot.
- **No Kaplan-Meier, cumulative incidence or other rate curves this session.**

## Do not do yet
- P2 rule-based cohort expansion, M0 base rates (cumulative incidence with competing risks), embedding retrieval (M1), or any predictive model (M3). They are gated in the plan.
- No paid APIs or credentials. No invented human judgments. No outcome inferred from absence of news.

## Verification before each commit
- `python -m pytest -q`, the Playwright suite, `scripts/verify.py`, `scripts/check_migrations.py`, `scripts/export_contract.py --check`, and the dry run of any new import.
- Open the running app and check each new view renders. A test passing is not enough.

## Git
- Small, descriptive commits after each verified step (P0, P1 schema + witnesses, P1 fixture data, P1 UI).
- After each verified commit, push to `origin implementation/healthtech-pilot`.

## When you finish
Update `docs/healthtech-pilot/STATUS.md` with what was built, the fixture counts by status and by witness type, the tests run with their results, and the single next step (the P2 inclusion-rule run). Then give me a plain-language summary of at most 10 lines.
