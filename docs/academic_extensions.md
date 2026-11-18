# Academic extensions and evidence limits

This is an engineering implementation, not a claim about Kevin's course enrollment or a relevance study. Course connections in the review are recommendations. No private course material, transcript, success labels, inferred company facts or reviewer decisions are added.

| Module | Status | Runnable work | Prerequisites for research claims |
|---|---|---|---|
| E1 missing evidence | Scaffolded; synthetic unit fixtures only | `backend/experiments/robustness.py` implements stable seeded field masking on explicitly reviewed snapshots and refuses unreviewed input. Source loss is distinct from contradiction. | Frozen reviewed corpus; declared fields, rates and mechanisms; retrieval adapter and grouped perturbation experiment; real labels for relevance effects. Repeated draws do not create human labels. Wording perturbations are deferred. |
| E2 budget allocation | Implemented algorithm; synthetic-only demonstration | `python scripts/academic_demo.py` compares exact enumeration and greedy, with declared hypothetical costs/utilities, precedence and coverage constraints. Enumeration limited to 20 tasks. No solver needed. | Actual evidence-gathering tasks and defensible costs/utilities; user validation. Proxy utility is investigation priority, never investment attractiveness. |
| E3 structured similarity | Scaffolded | `backend/experiments/structured.py` validates dimension/weight/units/scale configuration; scoring stays disabled. No threshold is recommended. | Accepted sourced fields, justified units/scales and development relevance labels to examine sparse-pair inflation, coverage policies and sensitivity. |
| E4 technical diligence | Deferred | No mechanics, CFD/FEM, differential equations or generic physical score added. | A concrete deep-tech diligence case with sourced units and feasibility questions. |
| Sequential/DP research selection | Deferred | No states, transition probabilities or expected information values invented. | Defensible sequential task model and observed costs/outcomes. |

## Core evaluation infrastructure

`python scripts/evaluate.py --db outputs/venture_evidence.sqlite --output outputs/development-evaluation.json` runs the six original development queries and exports deterministic comparisons and operational abstention counts. `evaluation/queries.json` and `evaluation/judgments.csv` remain unchanged. Blank judgments produce null relevance metrics and the explicit status `pending_human_judgments`.

Supplied labels must use integer grades 0–3, real reviewer IDs, rationale, ISO review dates and subject-correct source observation IDs (semicolon separated). Duplicate reviewer/query/venture entries and unknown IDs are refused. Independent reviewers' explicit grades are averaged, transparently, without inventing adjudication. Precision uses grade >=1 and is computed only when every returned item is judged; its denominator is the number returned, so it is named `precision_at_returned`. nDCG@3 uses gain 2^grade−1 and requires every eligible corpus candidate judged. Unjudged candidates are never treated as irrelevant. Abstentions receive no relevance score. No confidence intervals, paired significance tests, reviewer agreement, usefulness or time savings are claimed from the current blank labels. These remain pending real paired outcomes and an agreed review protocol.

Operational timings and SQL counts verify implementation efficiency, not analyst relevance or programme effectiveness. The 274-candidate external research inventory is neither imported nor treated as a deduplicated population.
