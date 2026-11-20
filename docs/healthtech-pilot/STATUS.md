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

The candidate count fell from 454 to 453 after the audit consolidated duplicate Rocos and SafeStack records and added Googly Inc Limited as an unresolved lead.

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
| Reached outcome | 1 | 1 |
| Verified closure first | 1 | 1 |
| Acquisition or IPO first | 0 | 0 |
| Observed without confirmed outcome | 17 | 14 |
| Lost to follow-up | 10 | 6 |
| Unknown | 21 | 28 |
| Unknown plus lost to follow-up | 31 of 50 (62%) | 34 of 50 (68%) |
| Verified still observed at 36 months | 21 | 17 |
| Observation at 36 months unresolved | 22 | 29 |
| Out of observation by 36 months | 7 | 4 |

Both gates remain closed. Twelve matched legal entities have documented removals or liquidation, ten more than the previous run. Supie is the only confirmed in-window competing closure. The other legal events occurred later. The original StretchSense entity and its successor are recorded separately, and Photonic Innovations' reversed liquidation is excluded from terminal events. The corrected audit counts Partly as a secondary event. Its priced 2022 Series A proves the event occurred between the 2020-10-08 entry and the 2022-12-16 Series A report. The 2021 pre-Series A terms still leave the exact timing open. The Carepatron investor note points to a May 2022 first raise, while the entry ledger retains the July 2022 publication proxy pending reconciliation. No rates or curves were computed. [Entry and legal evidence](../../research/healthtech-pilot/cohort-entry-evidence.json) · [Supie register](https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/7775376)

### Five additions after the 50-case review

| Company | Earliest supported entry | Evidence |
| --- | --- | --- |
| Aplenty, then known as Hot Lime Labs | November 2017 | KiwiNet dates the first round and names Powerhouse and Flying Kiwi Angels. Powerhouse calls it seed funding. YCF calls the same investment proof of concept. Both labels are retained. |
| Rocos | November 2017 | YCF names Sparkbox in the first Seed round. The register confirms Rocos Global Limited, now DroneDeploy New Zealand Limited, as the same company. |
| Marama Labs | February 2019 | YCF records the Seed tranche with WNT Ventures in the incorporation month. The investor confirms the Wellington university spinout. |
| SafeStack | September 2021 | YCF dates the new company capital. The issuer announces the pre-seed in October, and NZTE quotes the founder identifying the same Jelix-led raise as the first. |
| Liquium | May 2022 | Wellington UniVentures dates the closing month and the named co-investor calls it a seed round. YCF reports the same syndicate in June. |

The expansion preserved the original 50 entry decisions. The secondary timing correction updates Partly’s follow-up decision. The new entries have unknown outcomes pending follow-up. Across all 55, the primary tally is **1 reached, 1 closed first, 0 exits first, 17 observed without confirmed outcome, 10 lost and 26 unknown**. The secondary tally is **1 reached, 1 closed first, 0 exits first, 14 observed without confirmed outcome, 6 lost and 33 unknown**. Unknown plus lost is **36 of 55** and **39 of 55**, respectively. Both gates remain closed. [Public data limits and permissioned data gaps](PUBLIC_DATA_LIMITS.md)

| Observation at 36 months across 55 entries | Series A or later | Next priced equity round |
| --- | ---: | ---: |
| Verified still observed | 21 | 17 |
| Unresolved | 27 | 34 |
| Out of observation by 36 months | 7 | 4 |
| **Total** | **55** | **55** |

Partly reached both outcomes and Supie entered liquidation within the window, placing both companies out of observation for both outcomes. Zincovery and Social Club were classed as lost to follow-up for both outcomes, with last verified activity before month 36. Miruku, TamoRx and Narrative likewise last had verified activity before month 36 and were classed as lost to follow-up for the primary outcome. Their 36-month observation remains unresolved for the secondary outcome.

The earlier asset and stage records remain open for CropLogic, Googly and Veritide. Nectar’s issuer reports a September 2017 angel round before the December YCF entry, with its stage and investor unresolved. The expansion compared the contemporary NZVIF tables with the retrospective appendix and named investor notices. [Entry evidence and locators](../../research/healthtech-pilot/cohort-entry-evidence.json)

Run the read-only audit from the checkout. Use `--include-decisions` to export each decision or `--company-id public_tirolifesciencesltd` to inspect one history and its sources.

```sh
python scripts/audit_reference_cohort.py
```

The deterministic audit replay, **170 backend tests**, **40 Playwright tests**, production build, smoke verification, migration checks and generated API contract check passed. The fixture dry run wrote zero rows. The disposable demo verified exact reimports and integrity. A separate browser check opened the running MRI dossier and confirmed the three named comparisons, later milestones and source notes. After expansion the fixture still renders Supie’s verified closure trajectory. Entry decisions were identical with registry and staged outcome evidence withheld. The audit replay matched the prior entry and source evidence byte for byte and changed only Partly’s secondary status.

**Next task** — Resolve the next-round evidence gaps in the expanded cohort by checking the five new entrants and prioritising in-window issuances with identifiable pricing or capital records.

## Workbench Phase 0 · 21 November 2026

The audit rechecked all 17 companies with an observed status for either outcome. The two windows were unchanged. Both release gates remain closed. The 55 included entries and all legal-entity decisions were preserved.

| 36-month follow-up across 55 entries | Series A or later, before → after | Next priced equity round, before → after |
| --- | ---: | ---: |
| Reached outcome | 1 → 2 | 1 → 2 |
| Verified closure first | 1 → 1 | 1 → 1 |
| Acquisition or IPO first | 0 → 0 | 0 → 0 |
| Observed without a confirmed outcome | 17 → 9 | 14 → 5 |
| Lost to follow-up | 10 → 10 | 6 → 6 |
| Unknown | 26 → 33 | 33 → 41 |
| Unknown plus lost | 36 → 43 | 39 → 47 |
| Verified still observed at 36 months | 21 → 13 | 17 → 8 |
| Observation at 36 months unresolved | 27 → 34 | 34 → 42 |
| Out of observation by 36 months | 7 → 8 | 4 → 5 |

Halter's January 2018 Series A is inside its December 2016–December 2019 window. The October 2017 Promus announcement leaves the secondary event timing unresolved, so its supported interval is 1 December 2016 through 31 January 2018. [Case ledger](../../research/healthtech-pilot/cohort-follow-up.json)

### Targeted financing searches

Each quoted name was searched against round-stage and pricing terms, and the results were screened against the 36-month window below. The search date was 21 November 2026. Month-level entries retain the full month at both bounds.

| Company | Window | Query | Finding |
| --- | --- | --- | --- |
| Halter | 2016-12–2019-12 | `"Halter" seed Promus October 2017 Series A 2018 $7m $8m Data Collective` | Closed Series A in January 2018. October 2017 seed pricing remains open and the Data Collective report may overlap the same Series A. [Idealog](https://idealog.co.nz/tech/2018/06/meet-young-entrepreneur-helm-halter-nz-agritech-company-backed-peter-beck-and-peter-thiel) · [Promus](https://promusventures.com/2017/10/26/cowgorithms/) · [Computerworld](https://amcham.co.nz/Latest-News/6360908) |
| Aspiring Materials | 2021-10-15–2024-10-15 | `"Aspiring Materials" seed Series A equity raise pricing` | Motion-led 2023 raise. Letter stage and pricing open. [Issuer release](https://7c184638-5ea6-4266-87a7-5de5b27fa33a.filesusr.com/ugd/0b2ef1_838094dc6d5e4978bc127a061db02a1c.pdf) |
| Cetogenix | 2022-07-07–2025-07-07 | `"Cetogenix" funding seed follow-on Series A priced equity` | The 2024 continuation fund lists an existing investment. Company-level fresh financing in the window remains unconfirmed. [Pacific Channel](https://www.pacificchannel.com/stories/pacific-channel-launches-australasias-first-capital-continuation-fund) |
| Cleanery | 2022-06-09–2025-06-09 | `"Cleanery" startup New Zealand seed Series A funding priced round` | 2024 investment notice. Closing, new issue versus purchase and pricing open. [NZX](https://www.nzx.com/announcements/426045) |
| Dawn Aerospace | 2018-12–2021-12 | `"Dawn Aerospace" Dawn Aerospace Series A funding equity funding round` | May 2021 Movac backing lacks issuer, stage and pricing terms. Reported Series A closed after the window. [Company release](https://www.prnewswire.com/news-releases/spaceplane-company-secures-funding-from-nzs-largest-tech-vc-301300701.html) · [Series A](https://www.dawnaerospace.com/latest-news/dawn-raises-20million) |
| EnergyBank | 2021-10-21–2024-10-21 | `"EnergyBank" EnergyBank NZ start-up funding seed Series A priced round` | Founder confirms the entry seed. Search surfaced no distinct in-window financing. [Founder interview](https://nzentrepreneur.co.nz/founder-qa-energybank/) |
| HeartLab | 2020-10–2023-10 | `"HeartLab" Auckland HeartLab funding seed Series A priced equity Will Hewitt` | Reported a distinct later seed in 2021. Share price and valuation open. [TechCrunch](https://techcrunch.com/2021/09/16/new-zealand-startup-heartlab-raises-2-45m-to-bring-heart-scanning-software-to-the-u-s/) |
| Mint Innovation | 2017-03–2020-03 | `"Mint Innovation" Mint Innovation Series A Series B funding priced round` | Industry report calls the 2018 financing Series A. Founder dates the raise to December. Instrument remains open. The 2020 Series B was later than the window. [NZ Private Capital](https://nzprivatecapital.co.nz/wp-content/uploads/2021/05/20215-000676_NZPC-Monitor-2021_FINAL_Digital.pdf) · [Founder interview](https://thespinoff.co.nz/business/30-03-2019/mint-innovation-is-making-e-waste-less-wasteful) |
| RespirAq | 2021-12–2024-12 | `"RespirAq" RespirAq NZ funding seed Series A priced equity` | First close of a distinct post-seed round was reported in September 2024. Share pricing remains open. [KiwiNet](https://kiwinet.org.nz/News/Women_in_Deep_Tech) |
| Sharesies | 2017-05–2020-05 | `"Sharesies" Sharesies Series A funding investment round share price New Zealand` | The 2019 raise is recorded. No verified pricing or stage label surfaced for it. [PwC and NZGCP](https://www.pwc.co.nz/pdfs/2023/startup-investment-autumn-2023.pdf) |
| Carepatron | 2022-07-26–2025-07-26 | `"Carepatron" Carepatron Series A funding priced equity` | Separately reported 2023 seed lacks pricing. No lettered round surfaced in the window. [TechCrunch](https://techcrunch.com/2023/11/03/carepatron/) |
| Immersve | 2022-06-20–2025-06-20 | `"Immersve" Immersve Series A funding equity round` | Indexed April 2024 seed lead has unresolved issuer and instrument. Callaghan reports R&D grant support without linking it to that lead. [CB Insights](https://www.cbinsights.com/company/immersve/financials) · [Callaghan Innovation](https://www.callaghaninnovation.govt.nz/about-us/up-and-coming-companies/) |
| Jasper | 2019-04–2022-04 | `"Jasper" Jasper NZ property startup Series A funding priced equity company` | Issuer identifies M7 financing as a SAFE. No conversion, new priced financing or letter stage was confirmed in the window. [Issuer release](https://www.prnewswire.com/news-releases/seed-funding-in-proptech-biz-accelerates-democratisation-of-commercial-property-investment-300915474.html) |
| Parcelport | 2017-12–2020-12 | `"Parcelport" Parcelport NZ Series A funding priced equity` | 2019 AngelHQ lead described as convertible by a secondary index. No primary report or verified conversion appeared in the bounded search. [Public search lead](https://bouncewatch.com/company/parcelport) · [Issuer history](https://www.zappy.nz/about-us) |
| Quashed | 2021-03-05–2024-03-05 | `"Quashed" Quashed insurance Series A funding round New Zealand` | A July 2022 trade article reports a second raise without stage or pricing. Turners investment was announced in August 2024 after the window. [Insurance Business](https://www.insurancebusinessmag.com/nz/news/breaking-news/online-insurance-platform-quashed-to-offer-aia-nz-products-413042.aspx) · [NZX](https://www.nzx.com/announcements/436021) |
| Runn.io | 2021-12-14–2024-12-14 | `"Runn.io" Runn.io Series A funding equity NZ` | Investor confirms 2023 backing. Letter stage, instrument and share price remain open. [Shearwater Capital](https://www.shearwater.co/news/our-investment-in-runn-io/) |
| VidApp | 2017-09–2020-09 | `"VidApp" VidApp NZ Series A funding equity round` | Investor acknowledges later rounds without dates. The dated 2021 preference-share record falls after the window. [Enterprise Angels](https://www.enterpriseangels.co.nz/project/vidapp/) · [Young Company Finance](https://www.pwc.co.nz/assets/2022-assets/startup-april-2022/young-company-deal-data-2022.pdf) |

### Decisions

| Date | Decision | Reason | Alternative considered |
| --- | --- | --- | --- |
| 21 November 2026 | Use the contemporary, publisher-dated Idealog report for Halter's month-precision Series A. | It reports the January close. Halter's 2026 release refers to Founders Fund contributing early capital in 2017. The July report on Data Collective lacks a firm link to January. Closing day, the relationship between the reports and reported totals stay open. The supplied Press and Herald URLs could not be opened. | Use a 2018 year only or treat the Data Collective report and the January close as the same closing. |
| 21 November 2026 | Assess candidate financing against the specific outcome. | An unlabelled in-window round with unresolved terms can prevent an observed primary status. An explicitly non-lettered seed can still leave the next priced equity outcome open. | Mark both outcomes unknown for every later seed report or infer Series A from capital raised. |
| 21 November 2026 | Retain Mint Innovation's Series A as an unresolved candidate. | The reviewed reports support the round and label, with the instrument unresolved. | Count the reported round solely from the stage label. |
| 21 November 2026 | Record the date of a completed financing announcement as a reporting date when the source does not give the settlement day. | The reporting date is verifiable and can bound an in-window candidate. It does not establish the settlement day. | Assign the reporting date as the actual close. |

### Phase 0 verification and resume point

Python 3.12 ran 174 passing backend tests. The production build, smoke verification, all three SQLite migration transaction modes, generated contract check and disposable demo import verification passed. Playwright could not start the local server on either port tested because the environment denied socket binding. A stand-alone Chrome launch also exited before a page could be opened.

The Phase 0 changes are committed locally on `implementation/healthtech-pilot`. Direct Git access failed to resolve `github.com`. The remote heads were independently checked and were still `3f0905e` for the pilot and `bcca61e` for `main`. Resume by running the browser suite and inspecting the running app in an environment that allows local sockets. Then push the pilot branch, archive `origin/main` with the required tag and update `main` with the original lease from the workbench prompt. Phase 1 starts from the verified replacement `origin/main`.

## Workbench continuation · 21 November 2026

Phase 0 is published. The archive tag and new `origin/main` are visible in the checkout. The workbench branch was verified to descend from `2404f2d`.

### Decisions (continued)

| Date | Decision | Reason | Alternative considered |
| --- | --- | --- | --- |
| 21 November 2026 | Use the system font stack for the workbench. | The visual spec permits it and both font families with redistributable files were unavailable together locally. | Introduce a font download or CDN. |

### Pending local verification

| Phase | Checks run in this environment | Deferred |
| --- | --- | --- |
| 1 | pytest, production build, smoke verification, migrations, API contract | Playwright, running app inspection, branch push |
| 2 | pytest, production build, smoke verification, migrations, API contract | Playwright, running app inspection, branch push |

| 3 | pytest, production build, smoke verification, migrations, API contract | Playwright, running app inspection, branch push |

### Similarity and witness decisions

| Date | Decision | Reason | Alternative considered |
| --- | --- | --- | --- |
| 21 November 2026 | Use B0 token normalization and symmetric IDF overlap, with similarity 0.35 and coverage 0.15 as minimums. | No bundled offline embedder was available. Fixed thresholds require usable coverage across the defined feature dimensions. | Fetch a sentence encoder or use a score based on a single shared feature. |
| 21 November 2026 | Use the earliest bound for snapshot eligibility and the lower median outcome rank for even peer sets. | The witness date must hold for every possible anchor day. The lower median is reproducible and conservative. | Use the latest bound or the upper median. |
| 21 November 2026 | Keep alternate-anchor outcome ranks withheld under the current audit. | The frozen 36-month classifications were audited from seed entry. | Reuse the seed-entry classification at a different stage. |
