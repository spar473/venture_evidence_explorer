# Validation record — local release 1.0

Verified 17 November 2026 (Pacific/Auckland). Starter baseline was run in the supplied folder before implementation; both bootstrap and verification passed with 10 ventures, 7 sources, 20 observations, 7 awards, 10 connections and 50 proposed annotations.

## Engineering checks

- `python scripts/bootstrap.py` and `python scripts/verify.py`: pass before and after implementation. Standard-library bootstrap remains usable without application dependencies.
- `.venv/bin/python -m pytest -q`: 13 backend behavioural tests pass. They cover repeat ingestion/full-row equality, conflict rollback including a preceding new source, column injection/schema drift refusal, foreign-key/subject/date guards, immutable observations and reviews, distinct same-name identities, aliases, overlapping filters and same-award year matching, nulls, 404/422/503 paths, literal SQL-like query strings, deterministic ranking, subject exclusion, mode-specific source fields, proposed-annotation isolation, stage/empty/irrelevant abstention, CSV exports and blank evaluation labels.
- `npm run build`: TypeScript check and Vite production build pass. The built bundle is served locally from FastAPI without CDN dependencies.
- `npx playwright test`: seven rendered Chrome smoke tests cover browse/filter/reset, Formus evidence and unknowns, proposals, two description-query candidates, selected-subject exclusion, stage abstention, source-link destinations, real CSV download, loading/error/retry behaviour, 390px layout without page overflow, desktop capture, and stale-response invalidation.

The API provenance audit resolves all 20 observations and 7 award records to exactly the supplied source URL, publisher and dates; connection links resolve to the correct subject observation. Formus has no recorded award, and Alimetry's publication date remains 2021-04-08 even though its source URL contains 04/07. All current funding, operating and legal identity fields remain null. Synthetic overlap/identity/review fixtures are confined to temporary test databases. No accepted review events are seeded.

## Issues encountered and resolved

- Sandbox network access prevented initial dependency installation. Pinned dependencies were installed with authorised network access. Loopback binding and headless Chrome also needed execution outside the process sandbox; the application remains loopback-only.
- The first overlap fixture retained an incompatible event date; validation correctly refused it. The fixture was corrected without weakening validation, and award-year-versus-publication validation was added.
- Initial browser assertions used an ambiguous heading selector and expected an element even when abstention correctly produced none. Selectors were fixed. No browser failure remains in the final run.
- A description naming a known venture could have returned itself; named-identity detection now excludes it and refuses ambiguous identities.
- Stale comparison responses could appear after inputs changed; request invalidation prevents this, with a browser regression check.
- Import SQL constructed column names from input keys. Exact declared-column validation now rejects unexpected/missing keys before SQL construction. Source coverage no longer uses the starter's fixed 2026 cutoff. CSV files are replaced atomically one file at a time.

## Limits of verification

One non-failing third-party Starlette/AnyIO deprecation warning appears in the backend suite. Node/Playwright emits non-failing deprecation/color-environment warnings under Node 26. Browser automation checks the supplied source link destinations, not availability, full current page text or factual truth of the publisher reports. Source pages were not freshly re-researched or archived. No legal-entity validation, independent reviewer evaluation, relevance metrics, real-user pilot, time-savings measure, PostgreSQL migration execution or genuine Power BI report was performed. Only the local macOS Chrome environment was tested; other browsers/platforms remain unverified.

The six evaluation queries remain development tasks, with relevance labels null and the reviewer CSV blank. Structural correctness does not establish commercial usefulness, current company status, programme effectiveness or investment outcomes.

## Interface redesign verification

A subsequent visual pass replaces the landing-page framing and card grid with a compact directory, evidence drawer and consistent comparison/export views. TypeScript and the production build pass. Connected in-app-browser checks verified filters, empty/loading/error states, source metadata, Escape/focus return, comparison/self-exclusion, milestone abstention, analytical tables, CSV download and narrow layout. See `docs/design.md` for exact scope. The Playwright suite has been updated with a drawer keyboard regression check but was not rerun in this visual pass; the seven-test result above belongs to the initial release. Backend, database and retrieval method remain unchanged.
