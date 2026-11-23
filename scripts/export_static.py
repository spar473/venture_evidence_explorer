#!/usr/bin/env python3
"""Export the analytics API's public, read-only data for the Pages build."""

import argparse
from hashlib import sha256
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.analytics_views import cohort_payload, dump_json, live_inputs, profile_payload, robustness
from backend.backtest_coverage import SUBJECTS
from backend.synthetic_method import method_lab


def export(destination: Path) -> None:
    inputs = live_inputs()
    digests = {}

    def write(path: str, value: dict[str, Any]) -> None:
        output = destination / (path + '.json')
        output.parent.mkdir(parents=True, exist_ok=True)
        data = dump_json(value)
        output.write_bytes(data)
        digests[path] = sha256(data).hexdigest()

    # Entry and current-date playback share the same clocked event payload. The
    # client applies the selected date without fetching or refitting snapshots.
    write('views/cohort', cohort_payload(inputs))
    write('views/method', method_lab(7))
    for company in SUBJECTS:
        profile = profile_payload(inputs, company)
        write(f'views/profile/{company}', profile)
        # Profile playback needs the recorded scores and sources. Keep scenario presets and
        # their offline scorer inputs out of the initial download.
        write(
            f'views/overview/{company}',
            {key: value for key, value in profile.items() if key not in ('presets', 'scorer')},
        )
        write(f'robustness/{company}', robustness(inputs, company, 2000, 7))
    write('manifest', {'sha256': digests})
    (destination / 'method.txt').write_bytes((ROOT / 'docs/design/BACKTEST_PREREG.md').read_bytes())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'frontend/public/analytics-data')
    export(parser.parse_args().output_dir)


if __name__ == '__main__':
    main()
