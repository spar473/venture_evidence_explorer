# Healthtech pilot checkpoint · 19 November 2026

Branch: **`implementation/healthtech-pilot`**. Implementation commit: **`2c6273dd914529f6d3116e60c68f4cbea6325b16`**. This status note is the only change in the following documentation commit.

Checkout: `/Users/kevinnn.park/Documents/venture_evidence_explorer/healthtech-checkout`. The supplied parent folder had no Git metadata and was preserved. A separate clone fetched `https://github.com/spar473/venture_evidence_explorer.git`; the requested branch started at `cff7896`, three documentation commits beyond workbench `bff2c06`. A final fetch confirmed no remote divergence. No reset, force operation, push, merge or deployment occurred.

The existing **Research dossiers → Automated Breast MRI Reporting → Provider evaluation comparison** path works. It returns Volpara and Formus as two cited **pathway precedents**, with differences, dated reference-document evidence, later reports, unknowns and open mappings. Source links reveal original claims and locators. Historical mode abstains: the frozen 0.2.1 research contract cannot represent archive-availability witnesses. Same-stage anchors remain null. Future/overlapping partial dates, later assessments, disputes and possible self-identities cannot qualify earlier comparisons.

## Reproduce

With the documented dependencies and frontend installed/built, one command validates, dry-runs, imports and repeats all three packets in a fresh temporary database, then serves the demo:

```sh
python scripts/healthtech_demo.py --serve --evaluate
```

For this machine’s existing Python environment, from the checkout above:

```sh
../.venv/bin/python scripts/healthtech_demo.py --serve --evaluate --port 8002
```

The already-running demo is at **http://127.0.0.1:8001**, using `/private/tmp/vee-healthtech-final-demo/demo.sqlite`. Its reports and blank review materials are under `/private/tmp/vee-healthtech-final-demo/`. The normal UI was opened and the Volpara applicant-testing claim inspected through its rationale link. Use `--port 8002` for a second service. Omit `--serve` to prepare imports only. An explicit `--output-dir` must be new/empty; existing databases are never replaced.

For setup, run `npm --prefix frontend ci` and `npm --prefix frontend run build`; install the root locked Python requirements first. Individual dry-run/apply commands are in `docs/research_import.md`. No runtime database, dependency directory, generated build, test output or backup is committed.

## Executed verification

- `python -m pytest -q`: **140 passed, 2 skipped**. The skips require Python 3.12’s SQLite autocommit API; this environment is Python 3.10.10. Nine healthtech regressions cover packet safety, preservation, attribution, temporal eligibility, self-exclusion, disputes, sparse abstention, extension imports and blank review fields.
- `python scripts/verify.py`: **PASS**.
- `python scripts/verify_research.py --as-of 2026-11-19`: **PASS** for the original packet; also **PASS** with `--packet research/healthtech-pilot/packet.json` and `--packet research/healthtech-pilot/extension.json`.
- `python scripts/check_migrations.py` and `python scripts/export_contract.py --check`: **PASS**.
- `npm --prefix frontend run build`: **PASS**, including TypeScript checking.
- Full Playwright suite with the temporary-database server: **36 passed**. After the final review/self-identity eligibility change, the four affected healthtech browser tests passed again. Desktop/narrow layout, source navigation, export, recovery, existing intake/discovery/B0/dossier flows and historical abstention were exercised.
- `python scripts/healthtech_demo.py --evaluate`: **PASS**, including unchanged dry-run DB bytes and full-row repeat-import equality for all three packets, integrity/FKs, frozen B0 inputs and six development tasks. Human fields remain blank; relevance metrics are not evaluated.
- `git diff --check`: **PASS**. Existing dependencies and local Chrome were reused; no fresh-install or remote CI result is claimed.

## Case disposition and next task

Integrated: MRI Reporting, Formus, Volpara, Neurofanos, PulseMap, IVF Decision Support Tool, VistaVision and Toku. Neurofanos/IVF have scoped Formus analogies; VistaVision has a Toku commercialisation analogy; PulseMap abstains because its modality/evaluation evidence is thin. RosterLab reuses its unchanged original dossier as an abstaining contrast. Alimetry and Wellumio remain inventory leads only; no additional source claims were imported for them. See `SOURCE_LOG.md` for IDs and checked sources.

The two new packets contain eight distinct research subjects, fourteen distinct sources and forty-four distinct observations after shared Formus IDs are reconciled by exact equality. Current funding/legal status remains unknown. Formus’s 2023 FDA letter and company page with a May 2026 header remain separate claims. Neurofanos’s university grant, proposed IP licence and contemplated pre-seed round remain distinct.

**Next concrete task:** review the MRI pair using the blank six-task materials, then obtain a dated provider-side evaluation protocol/admission decision and reconcile the Formus product/submission identifiers. A separately versioned archive-witness contract and verified historical entry anchors are needed before enabling early snapshots. Scenarios and any forecast cohort remain later phases; no success probabilities or causal adoption prerequisites are claimed.
