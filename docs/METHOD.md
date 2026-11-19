# Methods and evidence boundaries

## Lexical comparison

`b0-token-overlap-1.0`: lowercase alphanumeric tokens, fixed stopwords and a published morphology map in `backend/retrieval.py` (e.g. images/imaging→image and surgical→surgery). Tokens shorter than three characters are excluded. Each venture contributes a set of eligible sourced tokens; repeated observations do not multiply a token's weight. For token t, IDF = 1 + ln((N+1)/(df(t)+1)), computed on all ventures. Score = matched query IDF sum / all query IDF sum. A candidate must match at least two distinct informative query tokens and cover at least 15% of query tokens. Return up to three, sorted by score then stable venture ID. Filters restrict candidates, not corpus IDFs. The corpus is part of the method input; expanding evidence can change rankings.

Selecting a subject, or entering its exact name/alias, derives the query from its eligible observations. A description naming one known venture preserves the description and excludes that venture. Ambiguous identities require selecting a subject. Candidate filters are explicit and visible under comparison settings; browse text search is not a comparison filter.

This heuristic is intentionally conservative and unvalidated. Shared wording is not demonstrated relevance; no match does not establish irrelevance. Pathway mode can compare origin wording, not verified market access, regulatory progress or deployment. Wording differences do not assert feature absence or company weaknesses. There are no accepted structured features, semantic retrieval, investment ranking or confidence probabilities. Awards, prestige, press volume and all proposed annotations are excluded from ranking. No experimental proposal matching is exposed.

Ten venture/project identities, seven sources, 20 observations, seven awards, ten connections and 50 proposals remain the supplied baseline. These are historical publisher reports, not independent validation or current profiles. All legal names, registrations, operating status and funding stages remain unverified. Publication dates differ from retrieval and event dates; 2026 retrieval does not establish past source availability. Source pages are not archived and may change. No success rate, programme effectiveness or return can be inferred from this selected sample.


## NZ healthtech and the reference pool

The healthtech dossier links scoped pathway precedents to published claims, their passage locators and unresolved questions. Reference-document dates anchor the elapsed-time view. Historical comparison requires evidence that the cited version was available by the cutoff. The separate [next-phase plan](healthtech-pilot/NEXT_PHASE_PLAN.md) specifies a hand-picked import and trajectory fixture, followed by an outcome-blind inclusion run. Any later rates depend on the rule-based cohort, follow-up quality and the published analysis gates.
