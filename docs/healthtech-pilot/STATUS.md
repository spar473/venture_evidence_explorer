# NZ healthtech comparison checkpoint · 19 November 2026

Branch `implementation/healthtech-pilot`, implementation commit `64013b2915167bdc94c631862442784f17585def`. This local checkout builds on the initial pilot checkpoint at `ee071a6`. The status note follows in a documentation commit.

## What works

**Research dossiers** shows **8 project–venture comparisons using 5 distinct reference ventures**. Four of the five university projects have evidence for at least one comparison. The counts come from the same eligible results the dossiers display at the pilot’s research cutoff. Opening a project shows the reason for each match, its limits and the original claims across imported packets.

| University project | Reference ventures |
|---|---|
| Automated Breast MRI Reporting | Volpara, Formus Labs, Wellumio |
| Neurofanos | Formus Labs, Wellumio |
| IVF Decision Support Tool | Formus Labs, Alimetry |
| VistaVision | Toku Eyes / Toku Inc. (entity mapping open) |
| PulseMap PAD Detector | No supported match. Its measurement method and provider evaluation are insufficiently documented. |

All ten named university and reference cases are integrated. The three healthtech packets contain 18 distinct sources and 52 distinct observations. The original packet adds RosterLab, an abstaining contrast, and QuickMas, outside the pilot. Legal mappings and independently verified same-stage peers remain open. Clinical studies supply evaluation methods and outcomes. Provider admission criteria and first paid deployments remain unknown. [Source and identity log](SOURCE_LOG.md)

## Reproduce

From the checkout with frontend dependencies installed, build once and create a fresh demo.

```sh
npm --prefix frontend run build
../.venv/bin/python scripts/healthtech_demo.py --serve --evaluate --port 8003
```

Use `python` for a different activated environment. Omit `--serve` to run the four disposable imports only, and omit `--evaluate` to skip producing blank review materials. A local demo was opened on [port 8002](http://127.0.0.1:8002). Choose **Research dossiers → Automated Breast MRI Reporting → Wellumio → Later reports and milestones** to inspect the hospital study. The directory coverage API is `GET /api/research/healthtech/coverage`.

## Executed verification

- Full backend suite, `python -m pytest -q` — **141 passed, 2 skipped**. The skips require Python 3.12 SQLite autocommit support. This run used Python 3.10.
- Full Playwright suite with local Chrome and a disposable server — **37 passed**. All five healthtech browser tests also passed against the final comparison code. The directory totals were separately opened and checked in the running demo.
- `python scripts/verify.py`, `python scripts/check_migrations.py`, `python scripts/export_contract.py --check`, frontend production build and staged diff checks — **passed**.
- `python scripts/verify_research.py --as-of 2026-11-19` — **passed** for the original packet and with each healthtech packet supplied via `--packet`.
- `python scripts/healthtech_demo.py --evaluate` — **passed**. Every dry run preserved the database bytes and rows, and repeat imports preserved all rows. The six development tasks produced ten blank research-review rows.
- The coverage regression checks an empty database, partial and reversed imports, repeat imports, single-packet comparisons and a disputed shared claim. Withholding the Wellumio result removes two pairs and one distinct reference.

**Next task:** have an analyst review the three MRI precedents against the provider-evaluation question. For PulseMap, seek a dated source naming the measurement method, reference test and intended clinical setting before selecting a peer. Historical replay still requires an archive-availability witness. Human relevance judgments, scenarios and forecasting remain follow-on work.
