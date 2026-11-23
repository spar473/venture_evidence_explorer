#!/usr/bin/env python3
"""Create synthetic-only cohort and method figures with the locked estimator."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.synthetic_method import TODAY_REFERENCE_N, method_lab, synthetic_cohort


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=7)
    parser.add_argument('--today-n', type=int, default=TODAY_REFERENCE_N)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'outputs/method-lab')
    args = parser.parse_args()
    payloads = {'cohort': synthetic_cohort(args.seed), 'figures': method_lab(args.seed, args.today_n)}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for slug, payload in payloads.items():
        contents = (json.dumps(payload, sort_keys=True, separators=(',', ':')) + '\n').encode()
        path = args.output_dir / f'{slug}.json'
        path.write_bytes(contents)
        print(f'{sha256(contents).hexdigest()}  {path}')


if __name__ == '__main__':
    main()
