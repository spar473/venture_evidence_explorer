# Public data limits for the NZ entry cohort

**Audit date 20 November 2026.** The frozen rule covers the first publicly reported institutional pre-seed or seed of a NZ-founded or NZ-headquartered company in 2012–2022. The audit reviewed **453 named candidate records** and confirmed **55 entries**. Of the rest, **397** remain unresolved and **1** falls outside the window. Public follow-up covered the original **50** entries, with enough dated evidence for formal coverage reviews on **30**. The five later additions still await bounded follow-up. [Entry evidence](../../research/healthtech-pilot/cohort-entry-evidence.json) · [Follow-up ledger](../../research/healthtech-pilot/cohort-follow-up.json)

| 36-month status across 55 entries | Series A or later | Next priced equity round |
| --- | ---: | ---: |
| Reached outcome | 1 | 1 |
| Verified closure first | 1 | 1 |
| Acquisition or IPO first | 0 | 0 |
| Observed without a confirmed outcome | 17 | 14 |
| Lost to follow-up | 10 | 6 |
| Unknown | 26 | 33 |
| **Unknown plus lost** | **36** | **39** |
| Verified still observed at 36 months | 21 | 17 |
| Observation at 36 months unresolved | 27 | 34 |

| Field missing or incomplete in public evidence | What permissioned data would resolve it |
| --- | --- |
| **First institutional investment and closing date.** All 365 staged portfolio listings lack investment dates. Nectar’s issuer reports a September 2017 angel round before the December deal-table Seed, with the earlier investors and stage unresolved. | Fund and angel network deal registers with legal company ID, first cheque and closing dates, round label, instrument, syndicate and any preceding transaction. |
| **Pricing, new equity and round sequence.** Partly’s 2021 pre-Series A report omits share price and instrument terms. Its 2022 Series A establishes that a priced round occurred between **8 October 2020 and 16 December 2022**. | Dated signed closing records or cap-table transaction extracts with round ID, price or valuation, new money to the company, and flags for tranches, conversions and secondary transfers. |
| **Issuer identity and closing dates near the cutoff.** Foundry Lab’s November 2021 Series A report leaves the link to the NZ entry company and its exact November 2018 entry date unresolved. | NZ company number and foreign issuer IDs, dates of any restructuring, and the linked subscription and settlement dates. |
| **Continuous follow-up and competing events.** Supie’s liquidation is dated inside its window. Tiro’s later liquidation leaves the preceding 36-month financing history unresolved. | A complete follow-on ledger through month 36, dated portfolio monitoring or last verified activity, and effective closure, acquisition or IPO dates where applicable. |

Both release gates remain closed. Each requires at least 150 eligible entries, 30 qualifying events for that outcome, measured 36-month follow-up and fewer than 25% unknown or lost. Run `python scripts/audit_reference_cohort.py --include-decisions` to inspect the case-level counts, dates and evidence. [Outcome rules](NEXT_PHASE_PLAN.md#outcome-rules-freeze-before-building-any-curve)
