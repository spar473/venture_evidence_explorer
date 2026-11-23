#!/usr/bin/env python3
"""Build a reproducible reviewed packet without modifying the original proposals."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.backtest_review import DECISIONS, apply_review
from backend.witnessed_snapshots import BACKTEST_PACKET, BacktestSnapshotPacket

REVIEWED_PACKET = ROOT / 'outputs/preview/backtest-snapshots-reviewed.json'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=BACKTEST_PACKET)
    parser.add_argument('--decisions', type=Path, default=DECISIONS)
    parser.add_argument('--output', type=Path, default=REVIEWED_PACKET)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve() or args.output.resolve() == BACKTEST_PACKET.resolve():
        parser.error('Write the reviewed packet to a separate output path')
    packet = apply_review(BacktestSnapshotPacket.model_validate_json(args.input.read_bytes()), args.decisions)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(packet.model_dump_json(indent=2) + '\n', encoding='utf-8')
    print(f'Wrote reviewed packet to {args.output}')


if __name__ == '__main__':
    main()
