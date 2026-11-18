# Venture Evidence Explorer — local release 1.0

An independent project for analysts and student founders investigating venture precedents. Browse historical public reports, inspect provenance and compare sourced wording. This selected sample is not the complete University of Auckland ecosystem, and the project has no official endorsement.

## Run locally

Python 3.10+ and Node 22.12+ (tested on Python 3.10.10 and Node 26.12.1), with npm. Package installation needs internet; the built application needs no network, credentials or paid APIs. External source links require internet when opened.

From the project directory:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python scripts/bootstrap.py
.venv/bin/python scripts/verify.py
cd frontend
npm ci --ignore-scripts
npm run build
cd ..
.venv/bin/python scripts/serve.py
```

Open http://127.0.0.1:8000. The launcher binds only to loopback. Once dependencies and the frontend are built, restart with `.venv/bin/python scripts/serve.py`. Use `--port 8001` if 8000 is in use. `VEE_DB=/absolute/path.sqlite` selects an existing migrated database. The app never silently replaces or reimports a database on startup. API requests use read-only SQLite connections.

The original standard-library workflow remains supported: `python scripts/bootstrap.py` and `python scripts/verify.py`. Bootstrap imports into `outputs/venture_evidence.sqlite`, applies checksummed migrations and exports database tables/analyses. Do not hand-edit CSVs as a source of truth. `data/seed.json` is the preserved input fixture; the application reads database records only.

Development: run the service, then `cd frontend && npm run dev`. Vite proxies `/api` to loopback port 8000. The normal release serves its built JS/CSS from FastAPI on one origin. No CDN assets, analytics or external fonts are used.

## Implemented

- Search names, aliases and sourced product wording; intersect programme, award year and connection filters. Programme/year must match the same award row. Clear reset, loading, empty and recoverable error states.
- Venture profiles with historical product and relationship observations, recorded awards, source URLs, publishers, publication/retrieval dates, effective/event dates, passage locators and review status. Source spellings are not legal identities. Unknown legal identity, operating status and funding stay null and display as unverified.
- Separate, visibly proposed analyst annotations with links to their evidence basis. No reviewer decisions are invented.
- Select a venture or describe an investigation. Product/customer mode uses product observations; commercialisation mode additionally uses sourced university-origin wording. Explainable B0 lexical ranking returns zero to three candidates, excludes the subject, shows matching terms/fields, source passages, wording differences, unknown evidence and five generic suggested diligence questions.
- Stage/milestone mode explicitly abstains: eligible commercial milestone data is absent. Deterministic/template briefs make no claim to LLM reasoning.
- Three analytical SQL views and CSV exports: recorded recognition by programme/year; overlapping connection types; source publication age and evidence coverage. Raw observations and proposed annotations have separate downloads. Empty CSV cells mean unknown/not recorded.
- Repeatable parameterised imports, immutable-record conflict refusal, rollback, strict imported-column validation, FK/subject checks, database immutability triggers, append-only review-event structure and atomic replacement of each CSV file.

## Demo path

1. Explore ventures → choose Velocity Ideas Challenge and 2026: two recorded ventures. Reset.
2. Search `FormusLabs`, inspect Formus Labs. Its profile has no recorded award; the founder's IMeasureU award has not been transferred. Inspect the dated source, unknown identity/status fields and separate proposals.
3. Find comparisons → description `clinical images software surgical planning` → product/customer. Inspect the two lexical candidates, fields, sources and unknowns. These are development examples, not relevance judgments.
4. Select Formus Labs as subject and compare. Self is excluded. Switch to stage/milestone to see explicit insufficient evidence.
5. Data & exports → download each CSV. Counts name awards, ventures, relationships, observations or sources. Source age carries its UTC `as_of_date`.

## Method and boundaries

`b0-token-overlap-1.0`: lowercase alphanumeric tokens, fixed stopwords and a published morphology map in `backend/retrieval.py` (e.g. images/imaging→image and surgical→surgery). Tokens shorter than three characters are excluded. Each venture contributes a set of eligible sourced tokens; repeated observations do not multiply a token's weight. For token t, IDF = 1 + ln((N+1)/(df(t)+1)), computed on all ventures. Score = matched query IDF sum / all query IDF sum. A candidate must match at least two distinct informative query tokens and cover at least 15% of query tokens. Return up to three, sorted by score then stable venture ID. Filters restrict candidates, not corpus IDFs. The corpus is part of the method input; expanding evidence can change rankings.

Selecting a subject, or entering its exact name/alias, derives the query from its eligible observations. A description naming one known venture preserves the description and excludes that venture. Ambiguous identities require selecting a subject. Candidate filters are explicit and visible under comparison settings; browse text search is not a comparison filter.

This heuristic is intentionally conservative and unvalidated. Shared wording is not demonstrated relevance; no match does not establish irrelevance. Pathway mode can compare origin wording, not verified market access, regulatory progress or deployment. Wording differences do not assert feature absence or company weaknesses. There are no accepted structured features, semantic retrieval, investment ranking or confidence probabilities. Awards, prestige, press volume and all proposed annotations are excluded from ranking. No experimental proposal matching is exposed.

Ten venture/project identities, seven sources, 20 observations, seven awards, ten connections and 50 proposals remain the supplied baseline. These are historical publisher reports, not independent validation or current profiles. All legal names, registrations, operating status and funding stages remain unverified. Publication dates differ from retrieval and event dates; 2026 retrieval does not establish past source availability. Source pages are not archived and may change. No success rate, programme effectiveness or return can be inferred from this selected sample.

## Verification

```sh
.venv/bin/python scripts/bootstrap.py
.venv/bin/python scripts/verify.py
.venv/bin/python -m pytest -q
cd frontend
npm run build
npx playwright test
```

For browser tests, keep the built service running. The default executable is macOS Google Chrome, using an isolated temporary profile. Set `CHROME_PATH` to a compatible Chromium binary on another system, and `VEE_URL` if using another loopback port. Browser tests cover actual rendered flows, CSV downloads, API failure recovery, loading and narrow layout. See `VALIDATION.md` for observed results and limits. Backend tests use temporary databases; synthetic reviews/overlaps never enter the release database.

`evaluation/queries.json` contains six development tasks and `evaluation/judgments.csv` remains blank. No precision, nDCG, reviewer agreement, usefulness or time savings is claimed.

## Handover

See `docs/architecture.md` for data flow and PostgreSQL migration path; `docs/decisions.md` for tradeoffs; `NEXT_STEPS.md` for priority extensions. Original specifications and research notes remain as historical starter documents; their future-tense roadmap is not a claim of implemented functionality. `SHA256SUMS.txt` is the original starter manifest, retained for provenance; it does not describe the modified release. See `RELEASE_SHA256SUMS.txt` for this release's code/docs/input checksums.

No remote repository, deployment, private submissions, contact records or external model integration is included. Power BI-ready CSVs are delivered, not a `.pbix` report. MCDA Studio has not been modified.

## Interface refinement

The directory now uses aligned record columns, a compact filter toolbar and a keyboard-accessible evidence drawer. Comparison and analytical screens share a neutral token system and readable labels. See `docs/design.md` for the design references and current browser verification. No new component libraries or external fonts are required.
