# API and reproducible comparison runs

The API still opens SQLite in read-only mode. Bootstrap or the migration command must explicitly prepare a database before serving; API startup never imports or replaces evidence. A comparison runs inside one explicit read transaction so its ranking, profile hydration and corpus digest see the same snapshot. A caller's existing transaction is retained without committing or rolling it back.

## Directory and profile contracts

`GET /api/ventures?limit=25&offset=0` returns `items`, `total`, `limit` and `offset`. `total` is the filtered count before pagination. The compatibility fields `filtered_ventures` and `total_ventures` mean the filtered total and all identities respectively. Limit is 1–100; offset is nonnegative. Ordering is display name then stable venture ID, so disjoint pages do not repeat identities on a fixed corpus.

Items contain identity fields plus `product_excerpt`, `recognitions` (award ID, programme and year), `award_count`, `connection_types`, `source_count` and `publication_dates`. These are historical directory summaries. They do not contain observations, full awards, connection evidence or proposals. `GET /api/ventures/{venture_id}` returns all original evidence and proposed annotations, including rejected/superseded statements with review state and correction links. Unknown publication dates are null. Explicit intervals retain unknown/day/month/year precision with calendar bounds; bounds are not assertions of an exact event day.

Same-award-row programme/year filters and overlapping relationship filters remain SQL `EXISTS` predicates; multiple relationships do not duplicate identities. Directory summaries use five SELECT statements for a nonempty page. Comparison uses batched lightweight documents, then hydrates at most three shortlisted results plus an optional subject in one batch. Corpus digests add constant query overhead. This improves query scaling, not a claim that every small-corpus comparison is faster.

## Typed contracts

Every JSON endpoint declares a Pydantic response model. CSV endpoints remain streamed CSV-format responses. Run:

```sh
python scripts/export_contract.py
python scripts/export_contract.py --check
```

The first command generates `schema/openapi.json` and `frontend/src/api-schema.ts` from the live API models. The second compares both files with regenerated content and fails on drift. Frontend domain types import the generated definitions. No network service or schema-generation dependency is needed.

## Baseline and eligibility

The published `b0-token-overlap-1.0` token normalization, IDF denominator, thresholds, tie-breaks and top-three limit are preserved. Ten historical regression cases record exact result order, six-decimal scores, coverage, matching terms and abstention wording; these are code-verification fixtures, not human relevance judgments. Summation order is deterministic across hash seeds.

`POST /api/compare` additionally accepts `policy` (`exploration`, default; or `accepted`) and optional `cutoff` (calendar day). Returned `evidence_policy` discloses the policy/version and availability restriction. Exploration admits source-checked publisher reports awaiting owner review; accepted retrieval requires actual acceptance review provenance. Rejected, needs-review and superseded observations are excluded. Raw historical profiles retain them for inspection. Proposal annotations do not influence ranking.

A historical cutoff requires a dated availability witness with evidence locator for each contributing source, and reviews/corrections are selected as of that cutoff. Publication dates alone are insufficient. Award and relationship candidate filters also require source availability by the cutoff. The original seed has no availability witnesses, so historical cutoff runs abstain. Present-day full profiles in the response remain exploratory raw evidence; only selected matching evidence and the run manifest are cutoff-qualified.

## Export and replay

Each comparison includes a portable `run` object containing:

- Run schema, lexical method and evidence-policy versions.
- Canonical SHA-256 corpus digest, full effective request/configuration and stable run ID.
- Every observation selected for that mode's corpus, with effective review status, including evidence used to compute corpus IDFs.
- Result signatures (subject/result IDs, scores, token coverage, terms, contributing observation IDs and abstention reason).

The digest hashes all user tables, including import hashes/original bytes and historical/review metadata. Review append order is included because it resolves same-day review ties. A changed import conservatively invalidates replay even when rankings happen to be unchanged. It does not hash SQLite file pages or filesystem modification times. The run ID hashes the canonical record; no wall-clock timestamp or random ID changes a repeated run.

Export the `run` object as JSON. Replay it with `POST /api/comparison-runs/replay`, sending that object as the JSON body. The endpoint checks the record checksum, supported versions and current corpus digest, reruns the request, and verifies the entire run manifest. Tampering, changed evidence/reviews, unsupported versions or result drift return HTTP 409. Invalid request shape returns HTTP 422. Runtime replay writes nothing.

To reproduce an old run after new evidence is imported, use a separate copy of the original corpus snapshot and matching code/configuration. A run manifest cannot reconstruct missing evidence by itself. Back up the database and exported input documents before migration/import; never edit applied migration files or erase review history to force a digest match.

## Actual regression evidence

Backend tests cover fixed-corpus deterministic export/replay, checksum tampering, changed-review refusal, exploration versus accepted/cutoff abstention, explicit snapshot ownership, pagination/counts and exact historical B0 parity. A temporary 1,010-identity synthetic fixture verifies that directory remains five SELECTs and comparison remains 33 SELECTs as the corpus grows from ten identities; only the three shortlisted profiles are hydrated. This is a query-count regression, not a production scalability or usefulness validation.
