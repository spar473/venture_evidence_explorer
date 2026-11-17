# First implementation handover

Implement inside a new local project named venture-evidence-explorer. This is separate from mcda-studio; do not modify that repository.

## Already concrete
The seed is a public-source, historical, ten-venture workflow sample. It contains seven sources, 20 observations, seven award events, ten university relationships and 50 explicitly proposed annotations. No final relevance labels exist.

## First implementation task
Run bootstrap and verification, inspect schema and seed, then produce a small local browse/filter view:
1. Venture list: display name, selection reason, relationship types and historical source dates.
2. Venture detail: observations with links and dates, awards and university relations.
3. Separate proposed annotations panel.
4. Filters by programme event/year and connection type.
5. A visible notice that current operating status and funding stage are unverified.
6. A simple keyword baseline using sourced product observations, with explicit no-results behaviour.

Deliver the smallest complete vertical slice before AI, graph views or cloud deployment. Reuse the data contract; migrate it explicitly if changed. SQLite is the current portable slice, PostgreSQL the application target. Do not add Docker or orchestration solely for appearance.

## Preserve these invariants
No invented incorporation, funding, investor, revenue, exit or closure information.
Awards, founders' alumni history, research origin and programme participation must not be conflated.
Do not assign one venture's founder's previous company award to the present venture. For example, the Formus article discusses an IMeasureU award; it is not a Formus award.
Do not merge similar names or abbreviations without evidence. Preserve project-to-company history.
Unknown differs from no. Source-derived descriptions differ from verified efficacy.
The seed's annotations are proposed and must not silently populate accepted model inputs.
No private Velocity entries, judges' feedback, email, student contact details or committee files are authorised by this brief.
Do not use external LLM APIs until a concrete integration and credential handling have been agreed. No API integration is necessary for the first slice.

## Acceptance
Run documented commands from a clean directory. Demonstrate filters on the ten supplied records, source resolution, duplicate prevention, atomic refusal of conflicting records and unknown handling.
Do not claim retrieval quality from the six development queries without independent relevance judgments.
Record completed versus planned functionality in the README.
Do not create a public repository, publish, deploy or contact people as part of this handover.

## After this slice
Have Kevin review identities and select a few voluntary reviewers. Next expand evidence, then implement and evaluate comparison modes. Power BI consumes curated exports or PostgreSQL views, not a second hand-maintained company spreadsheet.

