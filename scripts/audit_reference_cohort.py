#!/usr/bin/env python3
"""Apply the public NZ entry rule and emit a reproducible coverage audit."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.cohort_audit import ENTRIES, FOLLOW_UP, PACK, run_audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--discovery', type=Path, default=PACK)
    parser.add_argument('--evidence', type=Path, default=ENTRIES)
    parser.add_argument('--follow-up', type=Path, default=FOLLOW_UP)
    output = parser.add_mutually_exclusive_group()
    output.add_argument('--include-decisions', action='store_true', help='Include every decision and its source reports.')
    output.add_argument('--company-id', help='Show one decision and the sources cited by its financing reports.')
    args = parser.parse_args()
    try:
        audit = run_audit(args.discovery, args.evidence, args.follow_up)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if args.company_id:
        decision = next((row for row in audit['decisions'] if row['company_id'] == args.company_id), None)
        if decision is None:
            parser.error('Unknown company ID')
        cited = {source_id for report in decision['source_reports']
                 for source_id in [report['source_id'], *report['corroborating_source_ids']]}
        follow = audit['follow_up']['decisions'].get(args.company_id)
        follow_sources = set(follow['review']['source_ids']) if follow and follow['review'] else set()
        if follow:
            follow_sources.update(event['source_id'] for event in follow['events'])
        sources = {**audit['sources'], **audit['follow_up']['sources']}
        audit = {'decision':decision, 'follow_up':follow,
                 'sources':{key:sources[key] for key in sorted(cited | follow_sources)}}
    elif not args.include_decisions:
        del audit['decisions']
        del audit['follow_up']['decisions']
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
