#!/usr/bin/env python3
"""Reproduce the Time Machine's data gate without running a backtest."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.backtest_coverage import audit_coverage, audit_sector_mapping
from backend.witnessed_snapshots import BACKTEST_PACKET


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=BACKTEST_PACKET)
    parser.add_argument('--output', type=Path)
    parser.add_argument(
        '--require-gate', action='store_true', help='Exit 1 when the validated packet misses the fixed gate'
    )
    args = parser.parse_args()
    report = audit_coverage(args.input)
    report['sector_normalisation'] = audit_sector_mapping()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    for company_id, subject in report['subjects'].items():
        print(
            f"{company_id}: {subject['confirmed_peers_at_field_bar']} of {subject['eligible_peer_count']} eligible peers have 5 confirmed strict fields; {subject['potential_peers_after_review']} could clear after review"
        )
    print('PASS: evidence graph and cohort anchors are valid')
    print(
        'PASS: Phase 1 gate'
        if report['gate']['passed']
        else 'STOP: Phase 1 requires 15 covered Partly peers; do not run a backtest'
    )
    return 1 if args.require_gate and not report['gate']['passed'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
