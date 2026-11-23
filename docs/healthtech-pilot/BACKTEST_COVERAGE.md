# Time Machine coverage checkpoint

22 November 2026. This is the Phase 1 data audit, **not a backtest result**. The [preregistration](../design/BACKTEST_PREREG.md) was committed as `d0c7c27a7bbd58069ddaa1b72e79791470f5b385` before any Time Machine scoring run.

**Gate: stop before scoring.** No Partly-eligible peer has five human-confirmed strict entry fields; the requirement remains 15. Nine peers could clear the field bar if their proposals were confirmed, up from two in the first checkpoint. At least six additional peers still need sufficient evidence even if every current proposal is accepted. Historical research is not exhausted.

| Subject | Earlier peers | Peers with ≥5 confirmed fields | Peers that could clear after review | Subject confirmed / proposed fields |
|---|---:|---:|---:|---:|
| Partly | 32 | 0 | 9 | 0 / 0 |
| Supie | 39 | 0 | 9 | 0 / 6 |
| Halter | 8 | 0 | 1 | 0 / 0 |

## Evidence captured

All 72 extracted fields remain proposals (69 strict, 3 lenient-only). The [field review](BACKTEST_REVIEW.md) presents every value with its source version, witness date and evidence paraphrase. The [packet](../../research/healthtech-pilot/backtest-snapshots.json) retains raw values, field locators and normalisation rationale. No source PDFs or full article bodies are redistributed.

| Company | Strict proposals | Lenient-only proposals | Five-field peer candidate? |
|---|---:|---:|---|
| 1Centre | 0 | 3 | No |
| CodeLingo Limited | 5 | 0 | Yes |
| First AML | 6 | 0 | Yes |
| Firstcheck Ltd | 5 | 0 | Yes |
| Formus Labs | 3 | 0 | No |
| Inhibit Coatings | 3 | 0 | No |
| Marama Labs | 4 | 0 | No |
| Myovolt Limited | 5 | 0 | Yes |
| Narrative | 6 | 0 | Yes |
| Parcelport | 7 | 0 | Yes |
| Social Club | 6 | 0 | Yes |
| StretchSense | 6 | 0 | Yes |
| Supie | 6 | 0 | Subject |
| VidApp | 7 | 0 | Yes |

## Source limitations

- Partly remains empty. Its current NZ Entrepreneur article has a 2021 update. Archive availability checks returned captures on 22 October (NZ Entrepreneur) and 11 October 2020 (Scoop), both after 8 October; these listings supply no feature evidence and do not establish that no earlier capture exists. The Blackbird note is dated 13 October, also too late. Direct Scoop access returns an access challenge.
- Actual pre-entry capture bodies were inspected for Narrative, Parcelport, Vidapp, Myovolt, Marama Labs and First AML. Timestamps and body hashes are retained in the packet. Historical Wix pages for Inhibit and Formus exposed only titles and application loaders; unavailable body text supplies no features.
- First AML’s January 2019 page describes an outsourced professional service supported by software. Present-day self-service descriptions are not backfilled.
- StretchSense and Myovolt use product articles in fixed university periodicals. Printed issue dates and conservative PDF revision dates are recorded. These are proposed publisher-dated witnesses, not archive captures; their dates and classifications await reviewer acceptance.
- 1Centre’s April source falls two days after its conservative 1 April cutoff. Its three descriptor proposals are lenient-only and cannot count toward the gate.
- Marama has four strict proposals, Formus and Inhibit three each. Missing buyer, payment, full-time team and founding-age evidence stays missing. A working product or listed price alone does not establish revenue.
- No qualifying Halter source before its conservative 1 December 2016 cutoff was found. Later biographies cannot fill its snapshot.
- Sector normalisation retains 33 raw labels: 31 editorial proposals and two unresolved labels (`Foodtech`, `Software & Services`). These mappings add no historical features.

## Partly research queue

All 32 date-eligible peers are listed. Strict evidence uses each peer’s earliest entry bound and the subject cutoff. Existing profiles in other scopes are not automatically accepted.

| Peer | Entry date (original precision) | Confirmed fields | Strict proposals | Lenient-only proposals |
|---|---|---:|---:|---:|
| Aplenty (`discovery_aplenty`) | 2017-11 | 0 | 0 | 0 |
| Dawn Aerospace (`discovery_dawnaerospace`) | 2018-12 | 0 | 0 | 0 |
| Formus Labs (`discovery_formuslabs`) | 2019 | 0 | 3 | 0 |
| Foundry Lab (`discovery_foundrylab`) | 2018-11 | 0 | 0 | 0 |
| Halter (`discovery_halter`) | 2016-12 | 0 | 0 | 0 |
| Inhibit Coatings (`discovery_inhibitcoatings`) | 2019-12 | 0 | 3 | 0 |
| Marama Labs (`discovery_maramalabs`) | 2019-02 | 0 | 4 | 0 |
| Mint Innovation (`discovery_mintinnovation`) | 2017-03 | 0 | 0 | 0 |
| Opum Technology (`discovery_opumtechnology`) | 2019-05 | 0 | 0 | 0 |
| Sharesies (`discovery_sharesies`) | 2017-05 | 0 | 0 | 0 |
| StretchSense (`discovery_stretchsense`) | 2014-11 | 0 | 6 | 0 |
| TDRI (`discovery_tdri`) | 2018-11 | 0 | 0 | 0 |
| The Insides Company (`discovery_theinsidescompany`) | 2019-08 | 0 | 0 | 0 |
| Vortex Power Systems (`discovery_vortexpowersystems`) | 2019-05 | 0 | 0 | 0 |
| 1Centre (`public_1centre`) | 2017-Q2 | 0 | 0 | 3 |
| AuramerBio (`public_auramerbio`) | 2016-02 | 0 | 0 | 0 |
| Avalia Immunotherapies Ltd (`public_avaliaimmunotherapiesltd`) | 2015-09 | 0 | 0 | 0 |
| CodeLingo Limited (`public_codelingolimited`) | 2018-01-24 | 0 | 5 | 0 |
| First AML (`public_firstaml`) | 2019-03 | 0 | 6 | 0 |
| Firstcheck Ltd (`public_firstcheckltd`) | 2017-05 | 0 | 5 | 0 |
| Fluent Scientific Ltd (`public_fluentscientificltd`) | 2015-04 | 0 | 0 | 0 |
| Hi-Aspect (`public_hiaspect`) | 2016-04 | 0 | 0 | 0 |
| Jasper (`public_jasper`) | 2019-04 | 0 | 0 | 0 |
| Koti Technologies (`public_kotitechnologies`) | 2012-06 | 0 | 0 | 0 |
| Myovolt Limited (`public_myovoltlimited`) | 2019-12 | 0 | 5 | 0 |
| Narrative (`public_narrative`) | 2019-05-21 | 0 | 6 | 0 |
| Parcelport (`public_parcelport`) | 2017-12 | 0 | 7 | 0 |
| Photonic Innovations Ltd (`public_photonicinnovationsltd`) | 2013-12 | 0 | 0 | 0 |
| Rocos (`public_rocos`) | 2017-11 | 0 | 0 | 0 |
| Social Club (`public_socialclub`) | 2017-03 | 0 | 6 | 0 |
| Tiro Lifesciences Ltd (`public_tirolifesciencesltd`) | 2014-08 | 0 | 0 | 0 |
| VidApp (`public_vidapp`) | 2017-09 | 0 | 7 | 0 |

## Reproduce

```sh
.venv/bin/python scripts/audit_backtest_coverage.py --output outputs/backtest-coverage.json
# Expected exit 1 until the unchanged gate passes:
.venv/bin/python scripts/audit_backtest_coverage.py --require-gate
```

The default command validates the packet and mapping and reports the shortfall without failing CI. `--require-gate` provides a nonzero process gate for implementation. It does not compute similarity, select comps or evaluate outcomes.

Frozen cohort inputs:

- `discovery`: `98cfe2fa99d3cc67e42e2660f895a58e0f2024e08bd1523f0c48a4319503f8fa`
- `entry_evidence`: `3849a6c3ce5c636ffd111ce31d0bdb0e25307b974afb125d76eb73901a3fa803`

Packet SHA-256: `380d9c5217434639db0f466aeed69ed5652ecbd5a6c59de2fe79ff493d0f6bbf`.

Next evidence work: obtain an inspectable original Partly source; research at least six additional Partly-eligible peers to five proposed fields; obtain explicit human confirmation for at least fifteen sufficiently covered peers. Re-run this audit before implementing the general scorer, endpoint or UI.
