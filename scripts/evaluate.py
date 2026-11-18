#!/usr/bin/env python3
"""Export deterministic development comparison runs and label-gated metrics."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.database import connect
from backend.evaluation import read_judgments, relevance_report
from backend.retrieval import compare


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, required=True)
    parser.add_argument('--queries', type=Path, default=ROOT/'evaluation/queries.json')
    parser.add_argument('--judgments', type=Path, default=ROOT/'evaluation/judgments.csv')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    queries = json.loads(args.queries.read_text())
    if len({q['query_id'] for q in queries}) != len(queries):
        raise ValueError('Duplicate query IDs')
    runs, rankings = [], []
    with connect(args.db) as conn:
        ids = [row[0] for row in conn.execute('SELECT venture_id FROM ventures ORDER BY venture_id')]
        observations = {row[0]: row[1] for row in conn.execute('SELECT observation_id,venture_id FROM observations')}
        for query in queries:
            response = compare(conn, query=query['query_text'], mode=query['mode'])
            runs.append({'query_id': query['query_id'], 'split': query['split'], 'comparison': response})
            rankings.append({'query_id': query['query_id'], 'ranked_ids': [r['venture']['venture_id'] for r in response['results']], 'eligible_ids': ids})
    judgments = read_judgments(args.judgments, {q['query_id'] for q in queries}, set(ids))
    # Validate source IDs and subject linkage for every supplied nonblank judgment.
    import csv
    with args.judgments.open(newline='') as stream:
        for row in csv.DictReader(stream):
            if not (row.get('relevance_grade') or '').strip():
                continue
            evidence = [v.strip() for v in row['supporting_observation_ids'].split(';') if v.strip()]
            if not evidence or any(observations.get(oid) != row['venture_id'] for oid in evidence):
                raise ValueError('Judgment evidence must resolve to that venture; separate IDs with semicolons')
    report = {'schema_version': 1, 'dataset_scope': 'Supplied development queries; no research relevance claims without human labels',
              'operational': {'queries': len(runs), 'abstentions': sum(not r['comparison']['results'] for r in runs)},
              'relevance': relevance_report(rankings, judgments), 'runs': runs}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'output': str(args.output), 'operational': report['operational'], 'relevance_status': report['relevance']['status']}))


if __name__ == '__main__':
    main()
