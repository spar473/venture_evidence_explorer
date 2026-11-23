#!/usr/bin/env python3
"""Reproduce the registered historical cases on the separate provisional track."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.backtest import BacktestInputs, render_backtest
from backend.backtest_coverage import PREVIEW_LABEL, SUBJECTS
from backend.backtest_review import DECISIONS
from backend.witnessed_snapshots import BACKTEST_PACKET


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', default=BACKTEST_PACKET, type=Path)
    parser.add_argument('--decisions', default=DECISIONS, type=Path)
    parser.add_argument('--output-dir', default=ROOT / 'outputs/preview', type=Path)
    args = parser.parse_args()
    inputs = BacktestInputs(args.input, args.decisions)
    environment = {
        'preregistration_commit': inputs.packet.preregistration_commit,
        'input_sha256': inputs.digests,
        'python': platform.python_version(),
        'platform': platform.platform(),
    }
    metadata = json.dumps(environment, indent=2, sort_keys=True) + '\n'
    metadata_hash = sha256(metadata.encode()).hexdigest()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / f'environment-{metadata_hash}.json').write_text(metadata, encoding='utf-8')
    cases = [render_backtest(inputs, company).model_dump(mode='json') for company in SUBJECTS]
    document = {'provisional': True, 'label': PREVIEW_LABEL, 'cases': cases}
    data = (json.dumps(document, indent=2, ensure_ascii=False, sort_keys=True) + '\n').encode()
    digest = sha256(data).hexdigest()
    # Content-addressed runs preserve each earlier decision set.
    run = args.output_dir / f'backtest-{digest}.json'
    run.write_bytes(data)
    print(f'{PREVIEW_LABEL}\n{digest}  {run}\nExecution environment: environment-{metadata_hash}.json')


if __name__ == '__main__':
    main()
