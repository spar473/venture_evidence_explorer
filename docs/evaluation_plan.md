# Evaluation plan

## Current state
No model, relevance judgments, reviewer agreement, speed improvement or investor usefulness has been measured. Six queries are development tasks only. Blank judgments are intentional.

## First research question
Does challenge-aware structured matching retrieve more useful precedents than keyword search for an analyst's explicit investigation?

## Methods
B0: filters plus keyword search; retain query fields and ranking explanation.
B1: weighted structured similarity on reviewed dimensions; explicitly handle missing fields.
B2: semantic text retrieval on eligible source observations.
B3: a hybrid only if B0–B2 show a concrete need.

Never give awards, university prestige or number of press articles default relevance weight. Do not use the proposed comparison_angle or example_diligence_question to train and evaluate the same task: that creates circular labels. Separate human-reviewed query labels from retrieval features.

A possible structured score is weighted similarity over comparable fields. Report comparable-weight coverage separately. Do not silently reward missingness by normalizing a single weak match to a perfect score. Compare a coverage penalty and a minimum-coverage abstention rule; parameters must be tuned on development data only.

## Rubric for each query–candidate pair
0: irrelevant to the stated investigation.
1: a limited analogy, with substantial differences.
2: useful precedent on at least one important dimension.
3: strong precedent with multiple relevant dimensions and interpretable differences.
Blank: not reviewed. Not 0.

Require a written reason and supporting observation IDs. Distinguish product similarity from commercialisation relevance. A cross-sector company can score highly for a pathway question and poorly for product similarity. Exclude self-matches when the query names an existing venture.

## Review and splits
Use two independent reviewers if available; obtain their actual permission and judgments. Retain disagreements and report agreement before adjudication. Do not invent reviewer identities.
The six supplied queries are development examples. Reserve new queries and, where practical, a held-out venture group before tuning. With ten ventures this is a feasibility study, not evidence of generalisation.
When the corpus expands, hold out venture identities and avoid near-duplicate/rephrased queries crossing splits. Deduplicate source text before splits. Keep final labels sealed during tuning.

## Metrics
- nDCG@3 with gains 2^grade-1, over judged candidates. If ideal gain is zero, report undefined/no-relevant-case separately.
- Precision@3 using grade >=2 as relevant; define the handling of fewer than three returned items before evaluation.
- Coverage: queries receiving any eligible result; field/source coverage per result.
- Abstention: no appropriate comparison, accompanied by a reason.
- Grounding: supported factual assertions / audited factual assertions; report numerator and denominator.
- Extraction accuracy: reviewed field-level precision and recall on separately annotated passages.
- Utility: meeting-preparation time and user ratings measured in a voluntary pilot. No causal improvement claim from a tiny uncontrolled before/after exercise.
- Engineering: integrity failures, repeat-import behaviour, runtime, update errors and, only after API integration, actual model-call costs.

Do not present unknown/unjudged results as irrelevant. If judgments cover only pooled top results, disclose incomplete judgments; do not claim exhaustive Recall@K.

## Factual versus proposed brief content
Every factual statement needs an eligible observation. Each comparison explanation identifies dimensions and differences. Questions are labelled suggestions, not facts about company weaknesses.
Medical efficacy, regulatory status, revenue, funding and customer claims need their own dated evidence; award descriptions do not establish them.

