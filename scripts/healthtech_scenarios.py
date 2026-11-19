#!/usr/bin/env python3
"""Calculate conditional cash cases and optionally export a Venture Frame draft."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.healthtech_scenarios import ProviderScenarios, scenario_report, venture_frame_project
from backend.research_validation import decode_packet


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('assumptions', type=Path)
    parser.add_argument('--venture-frame', type=Path, help='New destination for a Venture Frame measurement draft')
    args = parser.parse_args()
    try:
        model = ProviderScenarios.model_validate(decode_packet(args.assumptions.read_bytes()))
        report = scenario_report(model)
        if args.venture_frame:
            with args.venture_frame.open('x') as file:
                json.dump(venture_frame_project(report), file, indent=2)
                file.write('\n')
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(report, indent=2))
