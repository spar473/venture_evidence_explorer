# NZ healthtech pilot checkpoint · 20 November 2026

Branch `implementation/healthtech-pilot`. Verified implementation commit `cc20ef0a66ee97ae5feae5b67e2910abb6cbb208`. This note is the following documentation commit.

The README now opens with a five-line pitch and the MRI demo. Migration 007 adds the fixture, round dates and source passages, six outcome states, historical availability witnesses, and snapshots with evidence at or before the cutoff. The importer stores the original packet and its normalized records. A dry run leaves the database byte-for-byte identical, and an exact repeat writes zero rows.

**Research dossiers → NZ reference fixture** opens the coverage panel and a selector for all 30 companies. Select Supie to see the verified closure marker, or Cleanery to see the open-circle follow-up marker. **Research dossiers → Neurofanos → Peer trajectories** shows Formus Labs with a year-precision 2019 entry and a dated pre-Series A report. **Inspect source evidence** shows the publisher, passage, dates and applicable witness. **What was public at the time** shows the witnessed features at the later Formus stage. The entry snapshot remains open.

The original healthtech pilot still has eight comparison pairs across five distinct reference ventures. The four projects with pathway precedents show those peers in the new view because the existing lexical B0 run returned zero fixture-linked matches for these queries. PulseMap abstains. The five projects remain analogy queries with timelines for the peers only. The fixture serves named histories and counts, with rates and probabilities reserved for a future eligible cohort.

| Project | Reference ventures |
| --- | --- |
| Automated Breast MRI Reporting | Volpara, Formus Labs, Wellumio |
| Neurofanos | Formus Labs, Wellumio |
| IVF Decision Support Tool | Formus Labs, Alimetry |
| VistaVision | Toku Eyes, with the Toku Inc. mapping still open |
| PulseMap PAD Detector | Abstains |

## Fixture coverage

The hand-picked fixture spans healthtech, agriculture, finance, payments, space, software, retail and other sectors. All requested reference companies are integrated as named records, including the five healthtech references and Halter, Sharesies, Hnry and Tracksuit. Fifteen companies have a source-supported entry. The other fifteen remain leads with unresolved eligibility. Twenty companies lack a witnessed entry snapshot. Across the fixture there are 49 sourced event claims and 12 witnessed stage snapshots, including ten at entry.

| Status | Companies |
| --- | ---: |
| Reached qualifying Series A or later within 36 months | 1 |
| Verified closure first | 1 |
| Acquisition or IPO first | 0 |
| Observed without a qualifying outcome | 5 |
| Lost to follow-up | 3 |
| Unknown | 20 |

The nine quiet cases are Supie, Cleanery, HeartLab, Quashed, Carepatron, Immersve, Astrix Astronautics, Runn.io and Excellent. Supie's closure comes from the liquidators' report. Bounded public follow-up supports the other classifications. Volpara's acquisition remains visible while its entry is unresolved. The pending Toku Eyes and Toku Inc. link leaves the Series A claim inspectable without an elapsed time or derived outcome. Formus regulatory claims continue to appear as separate reports. Its company-reported usage revenue supplies evidence of commercial use. The date of first payment remains open.

The 56 sources comprise 40 publisher-dated witnesses, zero verified archive captures and 16 sources without a witness. The HeartLab report links to an inaccessible contemporary HiNZ item, so the fixture uses a retrospective source and leaves its entry snapshot open. The ASX prospectus exceeded the public reader's full-text limit; an indexed excerpt was available. Some Scoop pages returned an access interstitial on direct opening; dated claims were checked against public indexed passages. [Fixture packet](../../research/healthtech-pilot/reference-fixture.json) · [Pilot source log](SOURCE_LOG.md)

## Reproduce

With the repository's locked dependencies installed, run these commands from the checkout.

```sh
python scripts/import_reference_pool.py
npm --prefix frontend run build
python scripts/healthtech_demo.py --serve --port 8006
```

Open the [local demo](http://127.0.0.1:8006) and select **Research dossiers**. The demo bootstraps a fresh temporary database, dry-runs and applies the existing dossier packets and the fixture, then verifies exact reimports. Omit `--serve` to run the same import verification without starting the app.

## Executed verification

- `python -m pytest -q` on Python 3.12.15 passed all **153** tests. Starlette emitted a dependency deprecation warning.
- The full Playwright suite with local Chrome and a disposable database passed all **40** tests. Opened the running app separately to inspect Supie's closure, the Neurofanos peer evidence and the sparse PulseMap view. Verified the trajectory response for all five projects.
- The frontend production build, `python scripts/verify.py`, `python scripts/check_migrations.py` in three transaction modes and `python scripts/export_contract.py --check` all passed.
- The fixture dry run wrote zero rows. The disposable demo applied 220 records, verified byte equality after a second apply, and passed SQLite integrity and foreign-key checks.

**Next task** — Run P2 against the public discovery sources using the frozen first institutional pre-seed or seed entry rule for 2012–2022, and audit eligibility, closure evidence and follow-up coverage before any outcome estimation.
