# NZ healthtech comparison checkpoint · 19 November 2026

Branch `implementation/healthtech-pilot`. Implementation commit `97397a56a443c2be99814047777628ccc434ec8d`. This status note is the following documentation commit. The branch is local.

**Research dossiers** shows eight comparisons across five distinct reference ventures. Four of the five university projects have supported pathway precedents. The four healthtech packets contain ten cases, 23 distinct sources and 62 distinct observations. The original packet adds RosterLab as a contrast and QuickMas outside the pilot.

| University project | Reference ventures |
|---|---|
| Automated Breast MRI Reporting | Volpara, Formus Labs, Wellumio |
| Neurofanos | Formus Labs, Wellumio |
| IVF Decision Support Tool | Formus Labs, Alimetry |
| VistaVision | Toku Eyes / Toku Inc. (mapping open) |
| PulseMap PAD Detector | Abstains. Two public descriptions leave the measurement method, comparator and clinical evaluation open. |

All named cases were integrated. Under the MRI comparison, **Compare elapsed time** shows the dates of documents, reported events or prospective targets relative to each reference document. **Provider studies and follow-up records** covers Volpara v1.5 use in DENSE and Formus’s original 2023 announcement and separate planned Australian study. The FDA decision, original Formus release and company page headed May 2026 remain individually inspectable. The VistaVision comparison includes the THEIA v1 study. Dates of first paid use, specific provider admission criteria, several product mappings and historical availability remain unresolved. [Sources and locators](SOURCE_LOG.md)

## Reproduce

From the checkout with locked Python and frontend dependencies installed, build and start the disposable demo.

```sh
npm --prefix frontend run build
python scripts/healthtech_demo.py --serve --evaluate --port 8005
```

Open **Research dossiers → Automated Breast MRI Reporting → Compare elapsed time**. The verified [demo on port 8004](http://127.0.0.1:8004) uses a fresh temporary database. Omit `--serve` to prepare and verify the five imports without starting a server.

The six-task review kit contains frozen results and 18 blank task/method rows. The cash prototype compares explicit evaluation, implementation and payment assumptions, and exports a Venture Frame measurement draft. The forecast feasibility check found 140 candidate registry records. The denominator of eligible products and their 24-month deployment outcomes remain unestablished. [Review kit](REVIEW.md) · [Scenarios](SCENARIOS.md) · [Forecast feasibility](FORECAST_FEASIBILITY.md)

## Executed verification

- `python -m pytest -q` in a fresh locked Python 3.12.15 environment — **146 passed**, including the SQLite autocommit cases. Starlette emitted one dependency deprecation warning.
- Full Playwright suite with local Chrome and a disposable database — **38 passed**. All six affected healthtech browser tests passed again after claims were grouped by timeline date. The directory and elapsed-time view were also opened in the running demo.
- Production frontend build, `scripts/verify.py`, `scripts/check_migrations.py` (three transaction modes), `scripts/export_contract.py --check` and staged diff checks — **passed**.
- `scripts/verify_research.py --as-of 2026-11-19` — **passed** for the original packet and each healthtech packet through `--packet`. The combined demo verified unchanged dry-run bytes and identical rows after reimport. Existing brand/project proposals retained their original evidence pointers.
- `scripts/healthtech_demo.py --evaluate` and the task-review CLI with blank inputs — **passed**. The report shows six development tasks, zero completed human reviews and a pending held-out slot.
- Scenario replay produced identical JSON. Venture Frame at `cf1068a8ff2f25436af5fd53759a8d0798369f81` imported and reopened a draft with three cases and eleven measurements in a temporary library.

**Next task:** run the six prompts with independent analysts and reviewers. For historical replay, collect dated source-version evidence for both sides of a pair. For forecasting, assemble a separate product-family cohort and establish routine provider use or documented absence through the full 24-month follow-up window.
