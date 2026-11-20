# NZ healthtech pilot checkpoint · 20 November 2026

Branch `implementation/healthtech-pilot`. The original 50-entry audit is anchored at `0cb82fe74e82d523c76b95f357bb63483133f3b2`. The P1 demo implementation is `cc20ef0a66ee97ae5feae5b67e2910abb6cbb208`.

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

The latest public-source run evaluated **453 named candidate records**, including the 274 staged discovery leads. **55** have support for a first institutional pre-seed or seed in 2012–2022. **397** remain unresolved and Bspkl's documented first seed falls outside the window. The source-covered cohort is still 95 entries short of the 150-company gate. The app's 30 selectable fixture companies remain available for individual comparisons.

| Entry vintage | Included companies |
| --- | ---: |
| 2012 | 1 |
| 2013 | 1 |
| 2014 | 2 |
| 2015 | 2 |
| 2016 | 3 |
| 2017 | 9 |
| 2018 | 4 |
| 2019 | 10 |
| 2020 | 2 |
| 2021 | 10 |
| 2022 | 11 |

The 314 entry reports and 106 sources include historical Young Company Finance tables and investor disclosures that support entries in every vintage. The 2016 investor account confirms Halter's initial institutional investment and the deal table supplies the December month. In the staged discovery pack, all 365 portfolio listings still lack an investment date. The historical report also contains anonymous deals and stage or location codes that are insufficient for legal-entity identification or entry eligibility. [Entry evidence](../../research/healthtech-pilot/cohort-entry-evidence.json) · [Young Company Finance historical appendix](https://www.pwc.co.nz/publications/2019/startup/young-company-finance-deals.pdf) · [Powerhouse portfolio disclosure](https://announcements.asx.com.au/asxpdf/20161128/pdf/43d85vnsf8cf54.pdf)

Young Company Finance reported 66 early-stage deals in the first half of 2022 and 76 in the second. Those counts include follow-ons and use deals as the unit. The audit reports eleven qualifying first entries for that vintage and preserves both market benchmark counts for context. [Spring 2022 report](https://www.nzgcp.co.nz/assets/Media/startup-investment-report-spring-2022_sml.pdf) · [Autumn 2023 report](https://www.nzgcp.co.nz/assets/Media/startup-investment-autumn-2023.pdf)

### Bounded review of the original 50

The secondary outcome was frozen and pushed in `f8f3c7a` before this review. Its audit counts distinct completed priced equity rounds with evidence of new money for the company and a share price or round valuation. It has its own minimum of 30 verified events. Both outcomes require at least 150 entries, measured 36-month follow-up and fewer than 25% of cases unknown or lost to follow-up.

On 20 November 2026 the review covered all 50 original entrants and was committed and pushed in `97c7fe9` before expansion. Each record logs the official company number and status, the public filing index and date span screened, the dated news query, the named fund query, public leads and the remaining evidence gaps. The filing screen covered calendar years from the entry year through three years later. Outcome timing uses exact dates or retained bounds from the sources. Filing titles and annual returns are recorded as legal history. Underlying allotment consideration was not confirmed from the public index. Thirty entries also have enough positive source evidence for a formal coverage review. The rest have a search log with the remaining gaps. [Per-company search and evidence ledger](../../research/healthtech-pilot/cohort-follow-up.json)

| Status | Series A or later | Next priced equity round |
| --- | ---: | ---: |
| Reached outcome | 1 | 0 |
| Verified closure first | 1 | 1 |
| Acquisition or IPO first | 0 | 0 |
| Observed without confirmed outcome | 17 | 14 |
| Lost to follow-up | 10 | 6 |
| Unknown | 21 | 29 |
| Unknown plus lost to follow-up | 31 of 50 (62%) | 35 of 50 (70%) |
| Verified still observed at 36 months | 21 | 17 |
| Observation at 36 months unresolved | 22 | 30 |

Both gates remain closed. Twelve matched legal entities have documented removals or liquidation, ten more than the previous run. Supie is the only confirmed in-window competing closure. The other legal events occurred later. The original StretchSense entity and its successor are recorded separately, and Photonic Innovations' reversed liquidation is excluded from terminal events. Partly's 2022 Series A is priced. Its earlier pre-Series A terms are open, so the time of its first subsequent priced round is unresolved. The Carepatron investor note points to a May 2022 first raise, while the entry ledger retains the July 2022 publication proxy pending reconciliation. No rates or curves were computed. [Entry and legal evidence](../../research/healthtech-pilot/cohort-entry-evidence.json) · [Supie register](https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/7775376)

### Five additions after the 50-case review

| Company | Earliest supported entry | Evidence |
| --- | --- | --- |
| Aplenty, then known as Hot Lime Labs | November 2017 | KiwiNet dates the first round and names Powerhouse and Flying Kiwi Angels. Powerhouse calls it seed funding. YCF calls the same investment proof of concept. Both labels are retained. |
| Rocos | November 2017 | YCF names Sparkbox in the first Seed round. The register confirms Rocos Global Limited, now DroneDeploy New Zealand Limited, as the same company. |
| Marama Labs | February 2019 | YCF records the Seed tranche with WNT Ventures in the incorporation month. The investor confirms the Wellington university spinout. |
| SafeStack | September 2021 | YCF dates the new company capital. The issuer announces the pre-seed in October, and NZTE quotes the founder identifying the same Jelix-led raise as the first. |
| Liquium | May 2022 | Wellington UniVentures dates the closing month and the named co-investor calls it a seed round. YCF reports the same syndicate in June. |

All 50 original entry and follow-up decisions were identical after expansion. The new entries have unknown outcomes pending follow-up. Across all 55, the primary tally is **1 reached, 1 closed first, 0 exits first, 17 observed without confirmed outcome, 10 lost and 26 unknown**. The secondary tally is **0 reached, 1 closed first, 0 exits first, 14 observed without confirmed outcome, 6 lost and 34 unknown**. Unknown plus lost is **36 of 55** and **40 of 55**, respectively. Both gates remain closed.

The earlier asset and stage records remain open for CropLogic, Googly and Veritide. Nectar’s issuer reports a September 2017 angel round before the December YCF entry, with its stage and investor unresolved. The expansion compared the contemporary NZVIF tables with the retrospective appendix and named investor notices. [Entry evidence and locators](../../research/healthtech-pilot/cohort-entry-evidence.json)

Run the read-only audit from the checkout. Use `--include-decisions` to export each decision or `--company-id public_tirolifesciencesltd` to inspect one history and its sources.

```sh
python scripts/audit_reference_cohort.py
```

The deterministic audit replay, **167 backend tests**, **40 Playwright tests**, production build, smoke verification, migration checks and generated API contract check passed. The fixture dry run wrote zero rows. The disposable demo verified exact reimports and integrity. A separate browser check opened the running MRI dossier and confirmed the three named comparisons, later milestones and source notes. After expansion the fixture still renders Supie’s verified closure trajectory. Entry decisions were identical with registry and staged outcome evidence withheld.

**Next task** — Resolve the next-round evidence gaps in the expanded cohort by checking the five new entrants and prioritising in-window issuances with identifiable pricing or capital records.
