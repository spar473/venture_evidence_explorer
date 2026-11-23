[**Open the live demo**](https://spar473.github.io/venture_evidence_explorer/)

# Venture Evidence Explorer

**Sourced comparisons for early New Zealand ventures.**

Compare a company at its first institutional round with earlier ventures, inspect the sources behind each match, and replay what happened next. Built for seed investors, university commercialisation teams, and researchers who want to see both the evidence and its gaps.

[![Engineering checks](https://github.com/spar473/venture_evidence_explorer/actions/workflows/checks.yml/badge.svg?branch=main)](https://github.com/spar473/venture_evidence_explorer/actions/workflows/checks.yml) [![GitHub Pages](https://github.com/spar473/venture_evidence_explorer/actions/workflows/pages.yml/badge.svg?branch=main)](https://github.com/spar473/venture_evidence_explorer/actions/workflows/pages.yml)

[![Supie at its first round, showing the peer map and labelled development curves](docs/analytics-screenshots/profile-1440.png)](https://spar473.github.io/venture_evidence_explorer/?view=profile&company=public_supie&asof=2021-11-09)

<a id="3-minute-demo"></a>

## Explore the demo

| View | What to try |
| --- | --- |
| [Company profile](https://spar473.github.io/venture_evidence_explorer/?view=profile&company=public_supie&asof=2021-11-09) | Start with Supie’s first round. Select Social Club on the peer map to see why it misses the comparison checks. Advance **Playback date** to see Supie’s later events and open a source. |
| [Cohort explorer](https://spar473.github.io/venture_evidence_explorer/?view=cohort) | Select a vintage bar to see the companies behind the count. Sort the event strip by outcome or use **View as table** to inspect the evidence heatmap. |
| [Scenario lab](https://spar473.github.io/venture_evidence_explorer/?view=scenario&company=public_supie) | Try the hypothetical **Business buyer** preset. Supie goes from zero to four qualifying peers. Add **Subscription** to see the count move to five. |
| [Method lab](https://spar473.github.io/venture_evidence_explorer/?view=method) | Compare the real cohort audit with the synthetic charts that demonstrate how the estimator behaves. |

[Desktop and mobile screenshots for all four views](docs/ANALYTICS_EVALUATION.md#screenshots)

<a id="method-and-limits"></a>

## Read the evidence

**Provisional research preview.** Entry facts used for the comparison preview have been AI-checked and are pending human review. The strict evidence gate remains locked. Supie has zero qualifying peers on its recorded facts, and Partly and Halter lack enough dated entry evidence to score. Scenario overrides are hypothetical and use the same entry cutoff and comparison rules.

The 21 November 2026 cohort audit records **55 confirmed entries**, **2 verified Series A or later rounds within 36 months**, **33 unknown outcomes**, and **10 companies lost to follow-up**. The real cohort views show counts. Rate and calibration charts in Method lab use a labelled synthetic dataset.

| Documentation | What it covers |
| --- | --- |
| [Historical comparison protocol](docs/design/BACKTEST_PREREG.md) | Entry dates, source availability, scoring weights and the strict evidence gate |
| [Cohort and outcome definitions](docs/healthtech-pilot/NEXT_PHASE_PLAN.md) | Inclusion rules, follow-up status, outcome windows and release criteria |
| [Analytics evaluation](docs/ANALYTICS_EVALUATION.md) | Worked score checks, scenario results, reproducibility hashes and browser verification |
| [Data status](STATUS.md) · [Changelog](docs/CHANGELOG.md) | Evidence coverage, open data decisions and project history |

<a id="run-it"></a>

## Run locally

Requires Python 3.10–3.13 and Node.js 22.12 or later.

```sh
git clone https://github.com/spar473/venture_evidence_explorer.git
cd venture_evidence_explorer
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
npm ci --prefix frontend
npm run build --prefix frontend
.venv/bin/python scripts/healthtech_demo.py --serve --port 8000
```

Open [localhost:8000](http://127.0.0.1:8000). The launcher creates a fresh demo database and binds to loopback. The built demo runs without API keys or external services. Source links open the original publications or archived copies.

The [contributor guide](CONTRIBUTING.md) covers the static build, validation commands, legacy workspaces, and how to reproduce the evidence checks.

## Contribute

Found a bug or a sourced correction? [Choose an issue template](https://github.com/spar473/venture_evidence_explorer/issues/new/choose) or read the [contributor guide](CONTRIBUTING.md).

The original software and documentation use the [MIT licence](LICENSE). Curated evidence and third-party sources carry separate terms. [Data use and corrections](DATA_USE.md)
