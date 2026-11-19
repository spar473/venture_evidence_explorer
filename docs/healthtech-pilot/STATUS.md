# NZ healthtech pilot checkpoint · 20 November 2026

Branch `implementation/healthtech-pilot`. The P2 audit is verified through `0cb82fe74e82d523c76b95f357bb63483133f3b2`. The P1 demo implementation is `cc20ef0a66ee97ae5feae5b67e2910abb6cbb208`.

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

## P2 entry and follow-up audit

The latest public-source run evaluated **454 named candidate records**, including the 274 staged discovery leads. **50** have support for a first institutional pre-seed or seed in 2012–2022. **403** remain unresolved and Bspkl's documented first seed falls outside the window. The source-covered cohort is still 100 entries short of the 150-company gate. The app's 30 selectable fixture companies remain available for individual comparisons.

| Entry vintage | Included companies |
| --- | ---: |
| 2012 | 1 |
| 2013 | 1 |
| 2014 | 2 |
| 2015 | 2 |
| 2016 | 3 |
| 2017 | 7 |
| 2018 | 4 |
| 2019 | 9 |
| 2020 | 2 |
| 2021 | 9 |
| 2022 | 10 |

The 304 entry reports and 79 sources include historical Young Company Finance tables and investor disclosures that support entries in every vintage. The 2016 investor account confirms Halter's initial institutional investment and the deal table supplies the December month. In the staged discovery pack, all 365 portfolio listings still lack an investment date. The historical report also contains anonymous deals and stage or location codes that are insufficient for legal-entity identification or entry eligibility. [Entry evidence](../../research/healthtech-pilot/cohort-entry-evidence.json) · [Young Company Finance historical appendix](https://www.pwc.co.nz/publications/2019/startup/young-company-finance-deals.pdf) · [Powerhouse portfolio disclosure](https://announcements.asx.com.au/asxpdf/20161128/pdf/43d85vnsf8cf54.pdf)

Young Company Finance reported 66 early-stage deals in the first half of 2022 and 76 in the second. Those counts include follow-ons and use deals as the unit. The audit reports ten qualifying first entries for that vintage and preserves both market benchmark counts for context. [Spring 2022 report](https://www.nzgcp.co.nz/assets/Media/startup-investment-report-spring-2022_sml.pdf) · [Autumn 2023 report](https://www.nzgcp.co.nz/assets/Media/startup-investment-autumn-2023.pdf)

Follow-up evidence is applied after fixing the entry list. Eleven companies have bounded follow-up searches. Nine have verified activity through the 36-month horizon with no qualifying outcome identified in their reviewed sources. Horizon coverage remains unresolved for 39. The status tally is one priced lettered round, one closure within the window, zero acquisitions or IPOs before the outcome, seven observed without a qualifying outcome, three lost to follow-up and 38 unknown. These are audit counts. [Follow-up evidence](../../research/healthtech-pilot/cohort-follow-up.json)

The Companies Register confirms liquidation and later removal for both Supie and Tiro Medical, formerly Tiro Lifesciences. Supie's liquidation follows its seed within 36 months, with a financing search through the closure date. Tiro's 2025 liquidation and 2026 removal are later than its 36-month window, so its earlier outcome remains unknown. [Supie register](https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/7775376) · [Tiro register](https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/5024040)

Run the read-only audit from the checkout. Use `--include-decisions` to export each decision or `--company-id public_tirolifesciencesltd` to inspect one history and its sources.

```sh
python scripts/audit_reference_cohort.py
```

The deterministic audit replay, **163 backend tests**, **40 browser tests**, production build, smoke verification, migration checks, generated API contract and disposable demo passed. The fixture dry run wrote zero rows and reimport preserved the database. Entry decisions were identical with the registry and staged outcome evidence withheld. The M0 gate remains closed on cohort size, confirmed primary outcomes and follow-up coverage. P3 curves, embedding retrieval and predictive models remain pending.

**Next task** — Review the remaining named-investor deal leads and the earlier NZVIF deal appendices for dated first-round evidence, then extend bounded follow-up on included cases.
