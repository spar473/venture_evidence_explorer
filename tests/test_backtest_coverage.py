"""Synthetic leakage and review regressions for the pre-scoring data gate."""

from copy import deepcopy
import json

import pytest
from pydantic import ValidationError

from backend.backtest_coverage import SUBJECTS, audit_coverage, audit_sector_mapping
from backend.witnessed_snapshots import BACKTEST_PACKET, BacktestSnapshotPacket


@pytest.fixture
def evidence():
    digests = {'discovery': 'a' * 64, 'entry_evidence': 'b' * 64}
    source = dict(
        source_id='source',
        title='Synthetic dated release',
        publisher='Synthetic',
        url='https://example.org/release',
        kind='press_release',
        published_on='2018-01-01',
        retrieved_on='2026-11-22',
    )
    witness = dict(
        witness_id='witness',
        source_id='source',
        kind='publisher_dated',
        available_on='2018-01-01',
        url=source['url'],
        locator='Synthetic dateline',
    )
    fields = dict(
        description='Synthetic workflow product',
        product_type='workflow',
        buyer='business',
        prototype='yes',
        round_size_band='0.5m_to_lt2m',
    )
    features = [
        dict(
            name=name,
            value=value,
            raw_value=value,
            derivation='stated',
            rationale='Synthetic fixture',
            source_id='source',
            witness_id='witness',
            passage='Synthetic passage',
            locator='Synthetic paragraph',
        )
        for name, value in fields.items()
    ]
    packet = dict(
        format_version='backtest-snapshots:1',
        compiled_on='2026-11-22',
        preregistration_commit='c' * 40,
        cohort_input_sha256=digests,
        sources=[source],
        witnesses=[witness],
        profiles=[],
    )
    cohort = dict(input_sha256=digests, decisions=[])
    for company_id, (value, precision) in {
        **SUBJECTS,
        **{f'peer_{i}': ('2018-01-01', 'day') for i in range(15)},
    }.items():
        entry = dict(
            date=dict(value=value, precision=precision),
            source_id='anchor',
            locator='Synthetic anchor',
            sector='Synthetic sector',
        )
        cohort['decisions'].append(dict(company_id=company_id, name=company_id, status='included', entry=entry))
        if company_id.startswith('peer_'):
            packet['profiles'].append(
                dict(
                    company_id=company_id,
                    scope='backtest_entry',
                    entry_date=entry['date'],
                    anchor_source_id='anchor',
                    anchor_locator=entry['locator'],
                    features=deepcopy(features),
                )
            )
    return packet, cohort


def write_packet(tmp_path, packet):
    path = tmp_path / 'packet.json'
    path.write_text(json.dumps(packet))
    return path


def confirm(packet):
    for profile in packet['profiles']:
        for feature in profile['features']:
            feature.update(
                review_state='confirmed',
                reviewer='Synthetic reviewer',
                reviewed_on='2026-11-22',
                review_reference='Synthetic confirmation fixture, not a real review',
            )


def test_proposals_never_pass_gate_and_outcomes_do_not_affect_coverage(evidence, tmp_path):
    packet, cohort = evidence
    path = write_packet(tmp_path, packet)
    result = audit_coverage(path, cohort=cohort)
    assert not result['gate']['passed'] and result['gate']['actual_peers'] == 0
    assert result['subjects']['public_partly']['potential_peers_after_review'] == 15
    cohort['follow_up'] = {'fake_future_outcome': 'reached'}
    assert result == audit_coverage(path, cohort=cohort)


def test_gate_counts_distinct_confirmed_peers_not_citations_or_proposals(evidence, tmp_path):
    packet, cohort = evidence
    confirm(packet)
    assert audit_coverage(write_packet(tmp_path, packet), cohort=cohort)['gate']['passed']
    packet['profiles'][0]['features'].pop()
    report = audit_coverage(write_packet(tmp_path, packet), cohort=cohort)
    assert report['gate']['actual_peers'] == 14 and report['gate']['shortfall'] == 1


@pytest.mark.parametrize(
    'mutation,match',
    [
        ('late_witness', 'entry evidence cutoff'),
        ('late_publication', 'entry evidence cutoff'),
        ('late_effective', 'entry evidence cutoff'),
        ('mutable_old_date', 'dated version'),
        ('duplicate_field', 'Duplicate name'),
        ('duplicate_profile', 'Duplicate company_id'),
        ('missing_source', 'matching source-version witness'),
        ('missing_review', 'require reviewer'),
        ('future_review', 'precede compilation'),
        ('review_before_retrieval', 'follow source retrieval'),
        ('inferred_negative', 'explicit yes or no'),
        ('unregistered_category', 'registered vocabulary'),
        ('partial_month', 'entry evidence cutoff'),
    ],
)
def test_refuses_leakage_unsupported_review_and_ambiguous_entry_dates(evidence, mutation, match):
    packet, _ = evidence
    feature = packet['profiles'][0]['features'][0]
    if mutation == 'late_witness':
        packet['witnesses'][0].update(
            kind='archived_capture',
            available_on='2018-01-02',
            captured_at='2018-01-02T00:00:00Z',
            url='https://archive.example.org/capture',
        )
    elif mutation == 'late_publication':
        packet['sources'][0]['published_on'] = '2018-01-02'
        packet['witnesses'][0].update(
            kind='archived_capture', captured_at='2018-01-01T00:00:00Z', url='https://archive.example.org/capture'
        )
    elif mutation == 'late_effective':
        feature['effective_on'] = '2018-01-02'
    elif mutation == 'mutable_old_date':
        packet['sources'][0]['kind'] = 'company_page'
    elif mutation == 'duplicate_field':
        packet['profiles'][0]['features'].append(deepcopy(feature))
    elif mutation == 'duplicate_profile':
        packet['profiles'].append(deepcopy(packet['profiles'][0]))
    elif mutation == 'missing_source':
        feature['source_id'] = 'different_source'
    elif mutation == 'missing_review':
        feature['review_state'] = 'confirmed'
    elif mutation in ('future_review', 'review_before_retrieval'):
        confirm(packet)
        feature['reviewed_on'] = '2026-11-23' if mutation == 'future_review' else '2026-11-21'
    elif mutation == 'inferred_negative':
        feature.update(name='paid_pilot_or_revenue', value='unknown')
    elif mutation == 'unregistered_category':
        feature.update(name='product_type', value='unregistered_value')
    elif mutation == 'partial_month':
        packet['profiles'][0]['entry_date'] = dict(value='2017-12', precision='month')
    with pytest.raises(ValidationError, match=match):
        BacktestSnapshotPacket.model_validate(packet)


@pytest.mark.parametrize('target', ['anchor_source_id', 'anchor_locator'])
def test_requires_the_accepted_cohort_anchor(evidence, tmp_path, target):
    packet, cohort = evidence
    packet['profiles'][0][target] = 'different'
    with pytest.raises(ValueError, match='accepted cohort identity and anchor'):
        audit_coverage(write_packet(tmp_path, packet), cohort=cohort)


def test_cohort_input_change_requires_review(evidence, tmp_path):
    packet, cohort = evidence
    cohort = deepcopy(cohort)
    cohort['input_sha256']['entry_evidence'] = 'd' * 64
    with pytest.raises(ValueError, match='Cohort inputs changed'):
        audit_coverage(write_packet(tmp_path, packet), cohort=cohort)


def test_lenient_cannot_fill_strict_gate_and_is_capped_at_subject_date(evidence, tmp_path):
    packet, cohort = evidence
    confirm(packet)
    # This peer entered before Partly, but its descriptor was public afterwards.
    peer = packet['profiles'][0]
    peer['entry_date'] = dict(value='2020-09-20', precision='day')
    next(row for row in cohort['decisions'] if row['company_id'] == peer['company_id'])['entry']['date'] = peer[
        'entry_date'
    ]
    packet['sources'].append(
        {**packet['sources'][0], 'source_id': 'later', 'url': 'https://example.org/later', 'published_on': '2020-11-01'}
    )
    packet['witnesses'].append(
        {
            **packet['witnesses'][0],
            'witness_id': 'later_w',
            'source_id': 'later',
            'url': 'https://example.org/later',
            'available_on': '2020-11-01',
        }
    )
    peer['features'][0].update(source_id='later', witness_id='later_w', timing='lenient')
    report = audit_coverage(write_packet(tmp_path, packet), cohort=cohort)
    partly = report['subjects']['public_partly']
    row = next(row for row in partly['peers'] if row['company_id'] == peer['company_id'])
    assert row['excluded_after_subject_cutoff'] == ['description']
    assert len(row['strict_confirmed_fields']) == 4 and not row['clears_field_bar']
    assert not report['gate']['passed']
    supie = next(row for row in report['subjects']['public_supie']['peers'] if row['company_id'] == peer['company_id'])
    assert supie['lenient_confirmed_fields'] == ['description'] and not supie['clears_field_bar']


def test_peer_entry_interval_must_end_before_subject_cutoff(evidence, tmp_path):
    packet, cohort = evidence
    before = audit_coverage(write_packet(tmp_path, packet), cohort=cohort)['subjects']['public_partly'][
        'eligible_peer_count'
    ]
    peer = packet['profiles'][0]
    peer['entry_date'] = dict(value='2020-10', precision='month')
    next(row for row in cohort['decisions'] if row['company_id'] == peer['company_id'])['entry']['date'] = peer[
        'entry_date'
    ]
    report = audit_coverage(write_packet(tmp_path, packet), cohort=cohort)
    assert report['subjects']['public_partly']['eligible_peer_count'] == before - 1
    assert peer['company_id'] in {row['company_id'] for row in report['subjects']['public_partly']['excluded']}


def test_current_research_packet_and_sector_mapping_retain_provenance():
    # Data integrity check, not acceptance of the proposed extracted facts.
    report = audit_coverage(BACKTEST_PACKET)
    assert report['included_companies'] == 55
    sectors = audit_sector_mapping()
    assert sectors['raw_labels'] == 33
    assert set(sectors['unmapped_labels']) == {'Foodtech', 'Software & Services'}
