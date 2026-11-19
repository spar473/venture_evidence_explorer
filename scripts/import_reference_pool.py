#!/usr/bin/env python3
"""Dry-run or explicitly import the NZ reference pool fixture."""
import argparse
import json
from pathlib import Path
import sqlite3
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.reference_pool import FIXTURE, import_pool


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=FIXTURE)
    parser.add_argument('--db', type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        result = import_pool(args.input,args.db,apply=args.apply)
    except (ValueError,OSError,sqlite3.Error) as error:
        parser.error(str(error))
    print(json.dumps(result,indent=2,ensure_ascii=False))


if __name__ == '__main__':
    main()
