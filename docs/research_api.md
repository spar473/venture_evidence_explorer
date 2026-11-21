# Two-dossier research API

This pilot reads the supplied research interchange 0.2.1 packet from immutable, namespaced SQLite research tables. Research subjects remain distinct from existing application venture IDs. The original ten-record corpus, its sources and B0 ranking fields are not populated from these dossiers. Source-checked research is not accepted factual evidence or an independent relevance judgment.

## Contracts and reads

All JSON responses have typed Pydantic contracts. Raw graph models are constructed locally from the bundled authoritative JSON Schema, preserving every declared field, null and enum. This response serialization layer does not replace the adapter's complete structural/semantic validator. Extra fields are refused rather than discarded. `python scripts/export_contract.py --check` checks the exported OpenAPI and generated frontend TypeScript against those models.

- `GET /api/research/subjects` returns paginated summaries with filtered `total`, all-subject `total_subjects`, `limit` and `offset`. Optional `q` searches display names literally; `review_state` filters recorded extraction/review state. Counts are explicitly observations, event candidates, unknowns and open cases. They are not completed milestones, distinct financing rounds or accepted companies.
- `GET /api/research/subjects/{subject_id}` returns the exact subject row, a linked `packet` graph, the latest recorded `identity_mapping`, raw-packet anchor `packet_digest`, all contributing `source_packet_sha256s`, a canonical `graph_sha256`, explicit `date_intervals`, graph-record `counts` and limitations.
- `GET /api/research/packets/{packet_sha256}.json` returns the exact original imported bytes. Its SHA-256 is the path/anchor digest. No reformatting, rewriting of metadata or inferred records occur.
- `GET /api/research/exports/{name}.csv` returns an analytical export. Optional `subject_id` selects the subject's linked graph. Optional `packet_sha256` scopes records to one imported packet. Namespace is explicitly `research:0.2.1`; unknown namespaces return HTTP 422.

Unknown subjects/packet hashes/export names return HTTP 404 where an individual resource is requested. A list query selecting an absent packet returns an empty list. All SQL values are parameterized, export names use a fixed allowlist and every graph read runs within one SQLite snapshot. Reads never migrate, import, accept or duplicate records.

## Graph closure and counts

The graph starts with the selected subject's observations, event candidates/reports, unknowns, question assessments, proposals, cases and access gaps. It then follows exact stable-ID references to shared sources/parties and counterpart evidence. A cross-subject question retains both subjects and all supporting observations, unknowns and conclusions. Adding a referenced counterpart identity does not silently import every unrelated record for that counterpart.

The `packet` field is a scoped reference-closure view, explicitly labelled `packet_view_kind: subject_reference_closure` and `is_standalone_import_packet: false`. It is not advertised as a separately validated or importable research interchange packet. Download the original whole packet through the packet endpoint for interchange or revalidation.

The `packet` metadata is preserved from the root subject's recorded import; it describes that original packet and its stated research actions. It is not rewritten into a claim about the later application's modification state. The full graph fingerprint and contributing import hashes distinguish a linked view from the raw source document. Graph `counts` count linked rows and can include counterpart context; they are not per-subject prevalence estimates. The directory's subject-specific counts remain separate.

`identity_mapping` exposes the actual stored proposal/decision provenance. In the supplied pilot both links are `proposed` with brand/project-only scope, no decision actor/date and unresolved legal identity. A display-name match is not an accepted mapping, legal entity, registration, contracting party or continuity finding. A later genuinely supplied decision can be shown with its document hash/history without changing the original subject record.

## Precision and evidence boundaries

Raw dates retain their supplied value, precision, basis and unknown reason. `date_intervals` adds validated calendar bounds for queries/display. For a year such as the QuickMas 2025 launch target, January 1 and December 31 are interval bounds; the raw value remains `2025`, and the occurrence date stays unknown. Context/publication/retrieval, effective and target dates remain separate. Passing a target year does not establish completion. Research-as-of cutoffs do not prove historical web availability.

Money remains a scoped source statement with currency value or explicit null/reason, billing interval, qualifier and unit. Advertised prices, round totals and investor cheques are not converted, combined or treated as contract prices. The two possibly duplicate RosterLab financing candidates stay separate with the open reconciliation case and `aggregation_allowed: false`. No monetary total, distinct-round count or investment score is exposed.

Speaker responsibility and publisher hosting are preserved independently. Regulator hosting does not turn applicant claims into regulator validation. Advertised integration does not establish completed implementation; named adoption does not establish payment or procurement budget authority. Supported readiness conclusions remain attributed/source-checked and scoped to their basis observations. Stronger requested conclusions remain withheld, including partial questions where only one subject has enough evidence. Unknowns keep null values, reason codes, source inspection scope and access gaps; unavailable sources are not evidence that a fact is false.

## CSV grains and preservation

Export names are `subjects`, `parties`, `sources`, `observations`, `events`, `event_reports`, `unknowns`, `proposed_annotations`, `readiness`, `reconciliation_cases`, `access_gaps`, `review_events`, `requirements`, `conclusions`, `identity_mappings` and `date_intervals`.

Each collection export has one row per stable record ID. Raw collection rows are preserved in `record_json`, alongside nested JSON cells and convenient flattened provenance, review and time columns. Original packet bytes are available through the packet endpoint. Observation/report exports include their exact source URL, publisher-role/relationship fields, speaker context, assertion nature, source IDs and source-check disposition. Time columns include raw value, precision, basis, unknown reason and calendar bounds. Nested money/currency preserves null currency explicitly. CSV empty cells mean unknown/not applicable where the original contains null, never a manufactured numeric zero. Formula-leading text is escaped for spreadsheet safety while `record_json` retains its unescaped JSON content.

A subject-filtered export includes linked counterpart records necessary to inspect a cross-subject question. `scope_subject_id` marks the requested subject, while each record's own `subject_id`/`subject_ids` retains its real attribution. Sources are shared, not duplicated per observation. Requirement and conclusion exports retain their parent readiness ID. Empty accepted-review exports stay empty; no acceptance or reviewer decision is synthesized to fill a table.

## Verification scope

API regressions use the supplied two-dossier packet, not invented factual records. They check exact model round-trip preservation, proposed identity/unknown legal fields, source/report lineage, cross-subject readiness closure, null currency, target-versus-occurrence dates, open financing cases, CSV row equality/no duplication, exact original-byte download, filtering and read-only behavior. These verify software behavior. They do not establish passage accuracy, event occurrence, relevance, investment merit, usefulness or time savings; those require actual source/human review and separate task evaluation.

## Curated healthtech comparison view

`GET /api/research/subjects/{subject_id}/comparisons?as_of=2026-11-19&view=research` returns the typed `HealthtechComparison` view. `as_of` is required and calendar-validated. `view` is `research` or `historical`; optional `packet_sha256` scopes the comparison to a single imported packet. The directory opens the combined subject graph so later research packets can extend existing comparisons. CSV exports use the same graph and each contributing original packet is downloadable. Unknown subjects return 404; invalid dates/views return 422. Reads share one SQLite snapshot and never import or write.

The strict `healthtech-comparisons:1` selection manifest references imported readiness, subject and observation IDs. Self/duplicate peers and more than three peers are refused. A possible shared proposed application identity is withheld without resolving that identity. Missing, mis-scoped, disputed, future or date-ineligible support withholds the comparison rather than silently weakening the rationale. Partial dates must have their entire validated interval at or before the cutoff; targets remain prospective. Research publication dates may be unknown when the actual source was read by the research cutoff, but that never qualifies historical availability.

Research mode returns at most three explicitly curated `pathway_precedent` records, readiness conclusions and their basis, sourced reference-document and later evidence, unknowns and open cases. `early_stage_anchor` remains null and `same_stage_assessment` is `abstain`. The response includes policy/selection/graph hashes and contributing original packet hashes. Current curation is not an automated relevance score, independent judgment or adoption forecast. Subjects with no assembled analogy abstain, including the sparse PAD case and RosterLab contrast.

Historical mode returns no peer claims or subject evidence: research 0.2.1 cannot carry the dated source-availability witness required to qualify an early snapshot. Even a present-day source containing an old document date cannot bypass that boundary. The full dossier endpoint remains an unfiltered audit view; the UI labels that distinction beside the comparison controls.


`GET /api/research/healthtech/coverage` returns the research cutoff, imported university project count, projects with at least one eligible peer, distinct reference subject count, directed project–venture pair count and the peer list per project. The endpoint evaluates the same comparisons as the dossier from one database snapshot at the manifest preparation date. Partial imports and applicable review disputes affect the counts. Directory text filters do not change this pilot-wide total. Reference counts use stable research subject IDs and carry no legal-entity or historical-stage determination.

The comparison response includes `follow_up` assessments from eligible imported research records. Individual follow-up assessments can be withheld without removing an eligible core comparison. `elapsed_evidence` exposes the date role, raw precision, observation ID and inclusive lower and upper day offsets from the named reference document. Unknown occurrence dates have null offsets. Planned dates are presented separately from occurrences. The original observation/source pair retains publication and retrieval dates.

## NZ reference fixture

The read-only routes below use the latest imported fixture. The directory returns an empty list and null coverage until a fixture is imported.

- `GET /api/reference-pool` returns the packet digest, named companies and coverage counts across all six status categories and three witness categories.
- `GET /api/reference-pool/companies/{company_id}` returns the publisher-attributed events, elapsed-day intervals for supported anchors, censor and closure markers, and witnessed stage snapshots. Events with proposed company links retain their claims without elapsed-day coordinates.
- `GET /api/reference-pool/analogy/{subject_id}` applies the existing B0 lexical comparison and joins eligible fixture identities. Where B0 yields no linked fixture company, it uses the dossier's curated pathway precedents if available. The response identifies the method or abstention. Elapsed-day coordinates describe peers only.

The fixture routes expose counts and individual histories. Rate, curve and prediction routes are outside this contract.

## Precedent workbench

`GET /api/precedents/{subject_id}?anchor=first_institutional_round&as_of=2026-11-21` returns the selected subject, curated pathways, the ranked seed-entry cohort peers, and the closest peer set’s ceiling, typical and floor. `GET /api/precedents/{subject_id}/checklist` returns the same dated subject checklist. The anchor selector supports first institutional round, first provider or clinical study evidence, first regulatory decision and first paid customer. A study registration is identified as registration in its source claim. Dated events retain exact or bounded elapsed days. Proposed identity links and ambiguous first anchors cannot establish a timeline position.

The workbench reuses imported, trigger-backed fixture features and checks their exact witness against the earliest possible anchor day. Research 0.2.1 observations remain source-attributed current evidence. They can date a documented event without proving retrospective source availability. Unwitnessed claims cannot contribute same-stage features or a Yes/No checklist value. The source-covered cohort determines seed-entry outcome classifications. Alternate anchors can use positive dated events within their own 36-month window. Missing or incomplete alternate-anchor follow-up does not inherit seed-entry censoring.

Similarity version `witnessed-gower-b0:3` sets k to 12 with minimum overall similarity 0.35, weighted evidence coverage 0.15, and clinical workflow similarity 0.25. Numeric ranges are 120 months for months since founding and two class steps for numeric regulatory classes. Text uses the B0 token normalizer and IDF-weighted intersection over union. Unknown values are excluded pairwise and reduce coverage. Company IDs break similarity ties. Fewer than three qualifying peers withholds comp cards. Cards use distinct companies or one representative when every resolved peer shares the same outcome rank.

For a university project, `subject.snapshot` and the checklist use witnessed evidence at `as_of`. Company subjects and all peer snapshots use the selected anchor. The legacy row `status`, `outcome_rank`, and `outcome_label` retain their window interpretation. `comp_outcome` carries the current ladder rank, label, status date with its precision, and supporting claim. A null `comp_outcome` leaves a ranked peer ineligible for a card.

The default `witness_mode=strict` applies the original witness cutoff. `witness_mode=contemporaneous` fills missing peer clinical workflow and buyer fields with eligible witnesses up to 90 days after the earliest anchor bound and by `as_of`. `peer_witness_delay_days` identifies late claims. `late_witness_peers` exposes eligible snapshots for inspection even when the peers fail ranking thresholds. The selected mode does not affect the subject, checklist, outcome ledger, gates or estimator. The screening-note export accepts the same parameter and records the selected mode.

`GET /api/workbench/gates` reads live release counts from the deterministic public audit and reports validation as pending. `GET /api/workbench/outcomes` returns seed-entry audit data with optional exact sector and vintage filters, primary/secondary outcome selection, and paginated company timelines. Summary and vintage counts share the selected denominator. The two-sector comparison applies the chosen vintage across the whole cohort. Benchmark Young Company Finance rows count deals. Plot annotations identify timing bounds and post-window closures. `GET /api/workbench/cohort-companies` lists eligible IDs and names for the venture picker.

`POST /api/precedents/{subject_id}/disputes` appends a local analyst dispute for a claim ID available to that row. The supplied request ID makes an identical retry idempotent. Conflicting reuse returns 409. Cross-origin browser writes return 403. Disputes retain the original source and timing, appear in the workbench claim review history, and exclude the claim from stage alignment and similarity. The frozen cohort audit remains a separate source record. The browser receives no Outlook estimates.

`GET /api/precedents/{subject_id}/screening-note` downloads a Venture Frame schema v1 JSON measurement draft with the same subject, anchor and as-of query as the workbench. Alternative metadata preserves roles, snapshot basis, dated comp outcomes, evidence-backed checklist values and claim IDs, and the similarity method and breakdown. The draft includes raw dimension similarities only where comparable evidence supports them. It has no supplied weights or screening score.

The [witnessed snapshot packet](../research/healthtech-pilot/witnessed-snapshots.json) adds evidence from publisher-dated sources. Entry features must match the existing institutional anchor claim and its earliest possible date. Dated university project profiles supply analogy features as of the selected cutoff. Round context for curated references with a missing or inapplicable anchor is visible in current Evidence. The [witnessed snapshot audit](healthtech-pilot/WITNESSED_SNAPSHOT_AUDIT.md) and [method v2 audit](healthtech-pilot/COMPS_V2_AUDIT.md) record prior results.
