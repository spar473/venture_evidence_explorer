"""Apply the provisional field decisions to the immutable proposal packet."""

import csv
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, StringConstraints

from .witnessed_snapshots import BACKTEST_PACKET, BacktestFeature, BacktestSnapshotPacket

DECISIONS = BACKTEST_PACKET.with_name('backtest-review-decisions.csv')
NonEmpty = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class Decision(BaseModel):
    key: NonEmpty
    company_id: NonEmpty
    field: NonEmpty
    proposed_value: str
    decision: Literal['Accept', 'Correct', 'Reject', 'Unsure']
    final_value: str
    decided_by: NonEmpty
    review_date: NonEmpty
    second_reading_value: str
    readings_match: NonEmpty
    review_kind: Literal['ai_adjudicated']
    human_confirmed: Literal['no']


def apply_review(packet: BacktestSnapshotPacket, decisions: Path = DECISIONS) -> BacktestSnapshotPacket:
    with decisions.open(encoding='utf-8', newline='') as stream:
        rows = [Decision.model_validate(row) for row in csv.DictReader(stream)]
    by_key = {row.key: row for row in rows}
    expected = {f'{profile.company_id}:{feature.name}' for profile in packet.profiles for feature in profile.features}
    if len(by_key) != len(rows) or expected != by_key.keys():
        raise ValueError(
            f'Review keys must cover each field once (missing: {sorted(expected - by_key.keys())}, '
            f'unexpected: {sorted(by_key.keys() - expected)})'
        )
    profiles = []
    for profile in packet.profiles:
        features = [
            apply_decision(feature, by_key[f'{profile.company_id}:{feature.name}'], profile.company_id)
            for feature in profile.features
        ]
        profiles.append(profile.model_copy(update={'features': features}))
    # Revalidate the graph after corrections, including source clocks and dates.
    return BacktestSnapshotPacket.model_validate(packet.model_copy(update={'profiles': profiles}).model_dump())


def apply_decision(feature: BacktestFeature, row: Decision, company_id: str) -> BacktestFeature:
    proposal = feature.proposed_value if feature.proposed_value is not None else feature.value
    if (row.company_id, row.field, row.proposed_value) != (company_id, feature.name, str(proposal)):
        raise ValueError(f'Review row does not match its proposal: {row.key}')
    if feature.review_state in ('confirmed', 'disputed') or feature.reviewer is not None:
        raise ValueError(f'AI review cannot overwrite human review: {row.key}')
    value = proposal
    if row.decision == 'Correct':
        value = int(row.final_value) if isinstance(proposal, int) else row.final_value
        if not row.final_value.strip() or value == proposal:
            raise ValueError(f'Correction needs a different final value: {row.key}')
    elif row.decision == 'Accept' and row.final_value != str(proposal):
        raise ValueError(f'Acceptance must keep the proposal: {row.key}')
    return BacktestFeature.model_validate(
        {
            **feature.model_dump(),
            'value': value,
            'proposed_value': proposal if row.decision == 'Correct' else None,
            'review_state': {
                'Accept': 'ai_adjudicated',
                'Correct': 'ai_adjudicated',
                'Reject': 'rejected',
                'Unsure': 'proposed',
            }[row.decision],
            'decided_by': row.decided_by,
            'review_date': row.review_date,
            'second_reading_value': row.second_reading_value,
            'readings_match': row.readings_match,
            'human_confirmed': False,
        }
    )
