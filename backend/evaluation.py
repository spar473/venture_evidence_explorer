"""Relevance metrics require explicit human grades; unjudged items stay unknown."""

import csv
import math
from collections import defaultdict
from datetime import date


def read_judgments(path, query_ids, venture_ids):
    judgments = defaultdict(dict)
    with open(path, newline='', encoding='utf-8') as stream:
        for line, row in enumerate(csv.DictReader(stream), 2):
            grade = (row.get('relevance_grade') or '').strip()
            if not grade:
                continue
            location = f'{path}:{line}'
            if row.get('query_id') not in query_ids or row.get('venture_id') not in venture_ids:
                raise ValueError(location + ': unknown query or venture')
            if grade not in ('0', '1', '2', '3'):
                raise ValueError(location + ': relevance_grade must be 0, 1, 2 or 3')
            for field in ('reviewer_id', 'rationale', 'supporting_observation_ids', 'reviewed_at'):
                if not (row.get(field) or '').strip():
                    raise ValueError(location + ': missing ' + field)
            date.fromisoformat(row['reviewed_at'])
            key = (row['query_id'], row['venture_id'])
            reviewer = row['reviewer_id']
            if reviewer in judgments[key]:
                raise ValueError(location + ': duplicate reviewer/query/venture judgment')
            judgments[key][reviewer] = int(grade)
    return judgments


def relevance_report(rankings, judgments, k=3):
    """Mean explicit grades across reviewers. Require complete result and corpus labels.

    Precision uses grade >= 1. nDCG uses gain 2**grade-1. Missing judgments
    are never converted to zero; nDCG requires all eligible candidates judged.
    """
    reports = []
    for ranking in rankings:
        query_id = ranking['query_id']
        returned = ranking['ranked_ids'][:k]
        eligible = ranking['eligible_ids']
        grades = {
            vid: sum(values.values()) / len(values) for (qid, vid), values in judgments.items() if qid == query_id
        }
        complete_results = bool(returned) and all(vid in grades for vid in returned)
        complete_corpus = bool(eligible) and all(vid in grades for vid in eligible)
        item = {
            'query_id': query_id,
            'returned': len(returned),
            'judged_returned': sum(vid in grades for vid in returned),
            'eligible': len(eligible),
            'judged_eligible': sum(vid in grades for vid in eligible),
            'precision_at_returned': None,
            'ndcg_at_3': None,
        }
        if complete_results:
            item['precision_at_returned'] = sum(grades[vid] >= 1 for vid in returned) / len(returned)
        if complete_results and complete_corpus:
            dcg = lambda values: sum((2**grade - 1) / math.log2(i + 2) for i, grade in enumerate(values))
            ideal = dcg(sorted((grades[vid] for vid in eligible), reverse=True)[:k])
            item['ndcg_at_3'] = dcg([grades[vid] for vid in returned]) / ideal if ideal else None
        item['status'] = 'measured' if item['ndcg_at_3'] is not None else 'pending_human_judgments'
        reports.append(item)
    return {
        'status': 'pending_human_judgments' if not judgments else 'partial_or_complete_human_judgments',
        'judgment_pairs': len(judgments),
        'queries': reports,
        'policy': 'No unjudged=irrelevant assumption. Grades 0–3; mean of supplied reviewers; precision denominator is returned items, not fixed k. nDCG requires complete eligible-corpus judgments. Abstentions have no relevance metric.',
    }
