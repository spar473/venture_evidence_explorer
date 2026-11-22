import csv
import subprocess
import sys

import pytest

from backend.backtest_coverage import PREVIEW_LABEL, audit_coverage
from backend.backtest import BacktestInputs, render_backtest
from backend.backtest_review import DECISIONS, apply_review
from backend.witnessed_snapshots import BACKTEST_PACKET, BacktestSnapshotPacket


def review_rows():
    with DECISIONS.open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_rows(path, fieldnames, rows):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def fields(packet):
    return {(profile.company_id, feature.name): feature for profile in packet.profiles for feature in profile.features}


def test_review_idempotent_and_keeps_proposals():
    packet = BacktestSnapshotPacket.model_validate_json(BACKTEST_PACKET.read_bytes())
    result = apply_review(packet)
    assert apply_review(result).model_dump_json() == result.model_dump_json()
    before = fields(packet)
    after = fields(result)
    assert len(before) == len(after) == 72
    _, rows = review_rows()
    for row in rows:
        key = (row['company_id'], row['field'])
        feature = after[key]
        assert feature.human_confirmed is False
        if row['decision'] == 'Correct':
            assert feature.proposed_value == before[key].value
            assert str(feature.value) == row['final_value']
        else:
            assert feature.value == before[key].value


@pytest.mark.parametrize('mutation', ['missing', 'duplicate', 'unexpected', 'misidentified'])
def test_review_requires_bijective_proposal_keys(tmp_path, mutation):
    packet = BacktestSnapshotPacket.model_validate_json(BACKTEST_PACKET.read_bytes())
    fieldnames, rows = review_rows()
    if mutation == 'missing':
        rows.pop()
    elif mutation == 'duplicate':
        rows.append(rows[0])
    elif mutation == 'unexpected':
        rows[0]['key'] = 'unexpected:key'
    else:
        rows[0]['field'] = 'buyer'
    path = tmp_path / 'decisions.csv'
    write_rows(path, fieldnames, rows)
    with pytest.raises(ValueError, match='Review (keys|row)'):
        apply_review(packet, path)


def test_preview_audit_excludes_rejected_unsure_and_strict_ignores_ai():
    original = audit_coverage()
    reviewed = audit_coverage(decisions=DECISIONS)
    assert original['gate'] == reviewed['gate']
    assert not reviewed['gate']['passed']
    assert reviewed['preview_gate']['actual_peers'] == 9
    assert reviewed['preview_gate']['label'] == PREVIEW_LABEL
    for subject in reviewed['subjects'].values():
        for row in [subject['subject'], *subject['peers']]:
            assert not set(row['preview_fields']) & set(
                row['rejected_or_disputed_fields'] + row['strict_proposed_fields']
            )
    run = subprocess.run(
        [sys.executable, 'scripts/audit_backtest_coverage.py', '--require-gate'], capture_output=True, text=True
    )
    assert run.returncode == 1
    assert PREVIEW_LABEL in run.stdout


def test_one_csv_edit_changes_only_one_packet_field_and_the_audit(tmp_path):
    packet = BacktestSnapshotPacket.model_validate_json(BACKTEST_PACKET.read_bytes())
    before = fields(apply_review(packet))
    fieldnames, rows = review_rows()
    row = next(row for row in rows if row['key'] == 'public_supie:buyer')
    row.update(decision='Correct', corrected_value='consumer', final_value='consumer')
    decisions = tmp_path / DECISIONS.name
    write_rows(decisions, fieldnames, rows)
    after = fields(apply_review(packet, decisions))
    assert [key for key in before if before[key] != after[key]] == [('public_supie', 'buyer')]
    assert after['public_supie', 'buyer'].proposed_value == 'household'
    old = audit_coverage(decisions=DECISIONS)
    new = audit_coverage(decisions=decisions)
    assert old['gate'] == new['gate']
    assert old['subjects']['public_supie']['subject']['preview_fields']['buyer'] == 'household'
    assert new['subjects']['public_supie']['subject']['preview_fields']['buyer'] == 'consumer'
    original = render_backtest(BacktestInputs(), 'public_supie')
    updated = render_backtest(BacktestInputs(decisions=decisions), 'public_supie')
    assert [
        field.name for field, changed in zip(original.subject.fields, updated.subject.fields) if field != changed
    ] == ['buyer']
    assert updated.input_sha256['decisions'] != original.input_sha256['decisions']
    assert next(field.value for field in updated.subject.fields if field.name == 'buyer') == 'consumer'


def test_ingest_cli_keeps_input_and_is_byte_identical_on_rerun(tmp_path):
    raw = BACKTEST_PACKET.read_bytes()
    source = tmp_path / 'proposals.json'
    source.write_bytes(raw)
    destination = tmp_path / 'reviewed.json'
    command = [sys.executable, 'scripts/ingest_backtest_review.py', '--input', str(source), '--output']
    subprocess.run([*command, str(destination)], check=True, capture_output=True)
    first = destination.read_bytes()
    subprocess.run([*command, str(destination)], check=True, capture_output=True)
    assert destination.read_bytes() == first
    assert source.read_bytes() == raw
    refusal = subprocess.run([*command, str(source)], capture_output=True, text=True)
    assert refusal.returncode == 2
    assert 'separate output path' in refusal.stderr
    assert source.read_bytes() == raw
