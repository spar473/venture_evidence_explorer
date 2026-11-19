#!/usr/bin/env python3
"""Validate completed analyst worksheets and report the task outcomes."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.healthtech_review import report_task_review


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('review_directory', type=Path)
    parser.add_argument('--runs', type=Path, required=True)
    parser.add_argument('--reviewers', type=Path, required=True)
    parser.add_argument('--as-of', required=True, help='Last admissible review date')
    args = parser.parse_args()
    try:
        report = report_task_review(args.review_directory, args.runs, args.reviewers, args.as_of)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(report, indent=2))
