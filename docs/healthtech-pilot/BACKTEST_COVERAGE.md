# Time Machine coverage checkpoint

22 November 2026. This is the Phase 1 data audit, **not a backtest result**. The [preregistration](../design/BACKTEST_PREREG.md) was committed as `d0c7c27a7bbd58069ddaa1b72e79791470f5b385` before any Time Machine scoring run.

**Gate: stop before scoring.** No Partly-eligible peer has five human-confirmed strict entry fields; the requirement remains 15. Two peers could clear the field bar if their current proposals were confirmed. This pass has not exhausted historical research for the eligible population.

| Subject | Earlier peers | Peers with ≥5 confirmed fields | Peers that could clear after review | Subject confirmed / proposed fields |
|---|---:|---:|---:|---:|
| Partly | 32 | 0 | 2 | 0 / 0 |
| Supie | 39 | 0 | 2 | 0 / 6 |
| Halter | 8 | 0 | 0 | 0 / 0 |

## Evidence captured in this pass

All 20 extracted fields below remain proposals. A proposal is not an accepted fact, an owner review or a scored feature. The source link, paraphrase, raw value, locator, normalisation rationale and witness are retained in [the packet](../../research/healthtech-pilot/backtest-snapshots.json).

| Company | Proposed fields | Dated source |
|---|---|---|
| CodeLingo Limited | description, product_type, sector_normalised, prototype, round_size_band | [Right Click Capital, 2018-01-24](https://www.rightclickcapital.com/2018/01/24/dunedin-startup-codelingo-raises-nz540000-from-reinventure-and-right-click-capital/) |
| Social Club | description, product_type, buyer, sector_normalised, market_focus, prototype | [Idealog, 2016-12-15](https://idealog.co.nz/venture/2016/12/social-club-talks-rise-influencer-marketing-new-zealand) |
| Supie | description, product_type, buyer, sector_normalised, market_focus, prototype | [Supermarket News, 2021-11-09](https://supermarketnews.co.nz/news/supie-puts-2-5m-towards-growth/) |
| Narrative | description, product_type, sector_normalised | [NBR, 2019-05-21](https://www.nbr.co.nz/investment/peter-thiel-led-fund-backs-local-creative-tech-startup-narrative/) |

## Source limitations

- Partly’s current NZ Entrepreneur article shows both its 2020 publication and a 2021 update. Its present text is excluded from the strict entry snapshot. Direct Scoop access and the archive query were unavailable in this environment; no archived version was inspected. This does not establish that no usable source exists.
- No qualifying Halter source before its conservative 1 December 2016 cutoff was found in the targeted searches in this pass. Later founder biographies are not entry evidence.
- Narrative’s public lead supports only three proposed fields. The paywalled body was not used.
- Missing buyer, payment, full-time team and founding-age evidence stays missing. A working product does not by itself establish revenue.
- Sector normalisation records all 33 raw cohort labels and their company/source/locator references: 31 editorial grouping proposals, with `Foodtech` and `Software & Services` unresolved. These mappings add no historical features and do not change existing packets.

## Partly research queue

All 32 date-eligible companies are listed, including those not researched in this pass. Eligibility uses the latest peer entry bound strictly before 8 October 2020; evidence uses each peer’s earliest entry bound. Existing profiles in other scopes are not automatically accepted.

| Peer | Entry date (original precision) | Confirmed fields | Proposed fields |
|---|---|---:|---:|
| Aplenty (`discovery_aplenty`) | 2017-11 | 0 | 0 |
| Dawn Aerospace (`discovery_dawnaerospace`) | 2018-12 | 0 | 0 |
| Formus Labs (`discovery_formuslabs`) | 2019 | 0 | 0 |
| Foundry Lab (`discovery_foundrylab`) | 2018-11 | 0 | 0 |
| Halter (`discovery_halter`) | 2016-12 | 0 | 0 |
| Inhibit Coatings (`discovery_inhibitcoatings`) | 2019-12 | 0 | 0 |
| Marama Labs (`discovery_maramalabs`) | 2019-02 | 0 | 0 |
| Mint Innovation (`discovery_mintinnovation`) | 2017-03 | 0 | 0 |
| Opum Technology (`discovery_opumtechnology`) | 2019-05 | 0 | 0 |
| Sharesies (`discovery_sharesies`) | 2017-05 | 0 | 0 |
| StretchSense (`discovery_stretchsense`) | 2014-11 | 0 | 0 |
| TDRI (`discovery_tdri`) | 2018-11 | 0 | 0 |
| The Insides Company (`discovery_theinsidescompany`) | 2019-08 | 0 | 0 |
| Vortex Power Systems (`discovery_vortexpowersystems`) | 2019-05 | 0 | 0 |
| 1Centre (`public_1centre`) | 2017-Q2 | 0 | 0 |
| AuramerBio (`public_auramerbio`) | 2016-02 | 0 | 0 |
| Avalia Immunotherapies Ltd (`public_avaliaimmunotherapiesltd`) | 2015-09 | 0 | 0 |
| CodeLingo Limited (`public_codelingolimited`) | 2018-01-24 | 0 | 5 |
| First AML (`public_firstaml`) | 2019-03 | 0 | 0 |
| Firstcheck Ltd (`public_firstcheckltd`) | 2017-05 | 0 | 0 |
| Fluent Scientific Ltd (`public_fluentscientificltd`) | 2015-04 | 0 | 0 |
| Hi-Aspect (`public_hiaspect`) | 2016-04 | 0 | 0 |
| Jasper (`public_jasper`) | 2019-04 | 0 | 0 |
| Koti Technologies (`public_kotitechnologies`) | 2012-06 | 0 | 0 |
| Myovolt Limited (`public_myovoltlimited`) | 2019-12 | 0 | 0 |
| Narrative (`public_narrative`) | 2019-05-21 | 0 | 3 |
| Parcelport (`public_parcelport`) | 2017-12 | 0 | 0 |
| Photonic Innovations Ltd (`public_photonicinnovationsltd`) | 2013-12 | 0 | 0 |
| Rocos (`public_rocos`) | 2017-11 | 0 | 0 |
| Social Club (`public_socialclub`) | 2017-03 | 0 | 6 |
| Tiro Lifesciences Ltd (`public_tirolifesciencesltd`) | 2014-08 | 0 | 0 |
| VidApp (`public_vidapp`) | 2017-09 | 0 | 0 |

## Reproduce

```sh
.venv/bin/python scripts/audit_backtest_coverage.py --output outputs/backtest-coverage.json
# Expected exit 1 until the unchanged gate passes:
.venv/bin/python scripts/audit_backtest_coverage.py --require-gate
```

The default command validates the packet and mapping and reports the shortfall without failing CI. `--require-gate` provides a nonzero process gate for the implementation phase. It does not compute similarity, select comps or evaluate backtest outcomes.

Frozen cohort inputs:

- `discovery`: `98cfe2fa99d3cc67e42e2660f895a58e0f2024e08bd1523f0c48a4319503f8fa`
- `entry_evidence`: `3849a6c3ce5c636ffd111ce31d0bdb0e25307b974afb125d76eb73901a3fa803`

Packet SHA-256: `e01a7405cde5fe7c1eb4aa22db583e6b0c949a213c748c540edf0607545c7945`.

Next evidence work: obtain an inspectable original Partly source; research at least thirteen additional Partly-eligible peers to five proposed fields; obtain explicit human confirmation for at least fifteen sufficiently covered peers. Re-run this audit before implementing the general scorer, endpoint or UI.
