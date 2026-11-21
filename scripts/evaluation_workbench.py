#!/usr/bin/env python3
"""Freeze inputs, export blank human-review materials, run label-gated evaluation."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.evaluation_protocol import freeze, review_materials, run, compare_reports


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    f = sub.add_parser('freeze')
    f.add_argument('--db', type=Path, required=True)
    f.add_argument('--output-dir', type=Path, required=True)
    f.add_argument('--tasks', type=Path, default=ROOT / 'evaluation/protocol-v1/tasks.json')
    f.add_argument('--policy', choices=['exploration', 'accepted'], default='exploration')
    f.add_argument('--as-of', default='2026-11-18')
    m = sub.add_parser('review-materials')
    m.add_argument('--bundle', type=Path, required=True)
    m.add_argument('--output-dir', type=Path, required=True)
    r = sub.add_parser('run')
    r.add_argument('--bundle', type=Path, required=True)
    r.add_argument('--judgments', type=Path)
    r.add_argument('--reviewers', type=Path)
    r.add_argument('--factual-audit', type=Path)
    r.add_argument('--split', choices=['development', 'held_out'], default='development')
    r.add_argument('--as-of', default='2026-11-18')
    r.add_argument('--repeats', type=int, default=3)
    r.add_argument('--output', type=Path, required=True)
    c = sub.add_parser('compare')
    c.add_argument('--left', type=Path, required=True)
    c.add_argument('--right', type=Path, required=True)
    c.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.command == 'freeze':
        result = freeze(a.db, a.output_dir, a.tasks, a.policy, a.as_of)
    elif a.command == 'review-materials':
        result = review_materials(a.bundle, a.output_dir)
    elif a.command == 'run':
        result = run(a.bundle, a.judgments, a.reviewers, a.split, a.as_of, a.repeats, a.factual_audit)
    else:
        result = compare_reports(json.loads(a.left.read_text()), json.loads(a.right.read_text()))
    if a.command in ('run', 'compare'):
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(
        json.dumps(
            {
                k: v
                for k, v in result.items()
                if k
                in (
                    'manifest_id',
                    'status',
                    'reason',
                    'coverage',
                    'tasks_pending',
                    'review_rows',
                    'held_out_pending',
                    'mean_difference',
                    'uncertainty',
                )
            },
            indent=2,
        )
    )


if __name__ == '__main__':
    main()
