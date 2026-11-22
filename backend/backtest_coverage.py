"""Audit preregistered entry coverage; never scores peers or consults their outcomes."""

import hashlib
from pathlib import Path
from typing import Any, cast

from .cohort_audit import run_audit
from .precedent_similarity_general import normalise
from .reference_pool import EventDate
from .research_validation import decode_packet
from .witnessed_snapshots import BACKTEST_FIELDS, BACKTEST_PACKET, BacktestSnapshotPacket

SECTOR_MAPPING = BACKTEST_PACKET.with_name('sector-normalisation.json')
PREVIEW_LABEL = 'Provisional preview: AI-adjudicated evidence, not human-confirmed; strict evidence gate not passed.'
SECTORS = {
    'enterprise_software',
    'fintech',
    'retail_ecommerce',
    'media',
    'healthtech',
    'biotech',
    'agritech',
    'cleantech',
    'advanced_materials',
    'manufacturing',
    'aerospace',
    'energy',
    'food_beverage',
    'consumer_products',
}

SUBJECTS = {
    'public_partly': ('2020-10-08', 'day'),
    'public_supie': ('2021-11-09', 'day'),
    'discovery_halter': ('2016-12', 'month'),
}
REQUIRED_PEERS = 15
REQUIRED_FIELDS = 5


def audit_sector_mapping(path: Path = SECTOR_MAPPING, *, cohort=None):
    cohort = cast(dict[str, Any], run_audit()) if cohort is None else cohort
    mapping = decode_packet(Path(path).read_bytes())
    if mapping['cohort_input_sha256'] != cohort['input_sha256']:
        raise ValueError('Sector mapping references changed cohort inputs')
    entries = {r['company_id']: r['entry'] for r in cohort['decisions'] if r['status'] == 'included'}
    labels = {entry['sector'] for entry in entries.values()}
    rows = mapping['mappings']
    if {row['raw_label'] for row in rows} != labels or len(rows) != len(labels):
        raise ValueError('Sector mappings must cover every raw label exactly once')
    for row in rows:
        if row['normalised'] is not None and row['normalised'] not in SECTORS:
            raise ValueError('Sector mapping uses an unregistered category')
        expected = {
            (company_id, entry['source_id'], entry['locator'])
            for company_id, entry in entries.items()
            if entry['sector'] == row['raw_label']
        }
        actual = [(ref['company_id'], ref['source_id'], ref['locator']) for ref in row['source_records']]
        if set(actual) != expected or len(actual) != len(expected):
            raise ValueError('Sector mapping must retain each raw label source and locator')
        expected_state = 'proposed' if row['normalised'] is not None else 'unmapped'
        if row['review_state'] != expected_state:
            raise ValueError('Editorial mappings are proposals, not confirmed historical evidence')
    return dict(
        raw_labels=len(rows),
        proposed_mappings=sum(row['normalised'] is not None for row in rows),
        unmapped_labels=[row['raw_label'] for row in rows if row['normalised'] is None],
        note='Mappings preserve raw labels and provenance; they add no confirmed backtest fields.',
    )


def audit_coverage(path: Path = BACKTEST_PACKET, *, cohort=None, decisions: Path | None = None):
    raw = Path(path).read_bytes()
    packet = BacktestSnapshotPacket.model_validate(decode_packet(raw))
    if decisions is not None:
        from .backtest_review import apply_review

        packet = apply_review(packet, decisions)
    return audit_packet(packet, hashlib.sha256(raw).hexdigest(), cohort=cohort)


def audit_packet(packet: BacktestSnapshotPacket, packet_sha256: str, *, cohort=None) -> dict[str, Any]:
    cohort = cast(dict[str, Any], run_audit()) if cohort is None else cohort
    if packet.cohort_input_sha256 != cohort['input_sha256']:
        raise ValueError('Cohort inputs changed from the registered snapshot; review before proceeding')
    entries = {row['company_id']: row for row in cohort['decisions'] if row['status'] == 'included'}
    profiles = {profile.company_id: profile for profile in packet.profiles}
    for company_id, profile in profiles.items():
        entry = entries.get(company_id, {}).get('entry')
        if entry is None or (
            profile.entry_date.model_dump() != EventDate.model_validate(entry['date']).model_dump()
            or profile.anchor_source_id != entry['source_id']
            or profile.anchor_locator != entry['locator']
        ):
            raise ValueError('Backtest profile must match its accepted cohort identity and anchor: ' + company_id)
    for investigation in packet.investigations:
        if investigation.company_id not in entries:
            raise ValueError('Investigation references a company outside the accepted cohort')
    witnesses = {item.witness_id: item for item in packet.witnesses}
    sources = {item.source_id: item for item in packet.sources}

    def known_by(feature, cutoff):
        source = sources[feature.source_id]
        return all(
            value is None or value <= cutoff
            for value in (
                witnesses[feature.witness_id].available_on,
                source.published_on,
                source.revised_on,
                feature.effective_on,
            )
        )

    def coverage(company_id, historical_cutoff):
        profile = profiles.get(company_id)
        features = profile.features if profile else []
        # The common calendar cap applies even in lenient mode. Review dates are
        # present-day extraction metadata, not historical availability dates.
        available = [f for f in features if known_by(f, historical_cutoff)]
        confirmed = sorted(f.name for f in available if f.timing == 'strict' and f.review_state == 'confirmed')
        proposed = sorted(f.name for f in available if f.timing == 'strict' and f.review_state == 'proposed')
        adjudicated = {
            f.name: f.value for f in available if f.timing == 'strict' and f.review_state == 'ai_adjudicated'
        }
        recognised, unknown = normalise(adjudicated)
        return dict(
            company_id=company_id,
            name=entries[company_id]['name'],
            entry=entries[company_id]['entry']['date'],
            strict_confirmed_fields=confirmed,
            strict_proposed_fields=proposed,
            preview_fields={name: adjudicated[name] for name in recognised},
            preview_unknown_fields=unknown,
            lenient_confirmed_fields=sorted(
                f.name for f in available if f.timing == 'lenient' and f.review_state == 'confirmed'
            ),
            excluded_after_subject_cutoff=sorted(f.name for f in features if f not in available),
            rejected_or_disputed_fields=sorted(f.name for f in features if f.review_state in ('rejected', 'disputed')),
            missing_confirmed_fields=[name for name in BACKTEST_FIELDS if name not in confirmed],
            clears_field_bar=len(confirmed) >= REQUIRED_FIELDS,
            would_clear_if_proposals_confirmed=len(confirmed) + len(proposed) + len(recognised) >= REQUIRED_FIELDS,
        )

    subjects = {}
    for company_id, (value, precision) in SUBJECTS.items():
        entry = entries.get(company_id, {}).get('entry')
        if not entry or entry['date'] != {'value': value, 'precision': precision}:
            raise ValueError('Registered subject anchor changed: ' + company_id)
        cutoff = EventDate.model_validate(entry['date']).bounds()[0]
        assert cutoff is not None  # The registered subjects have known entry intervals.
        peers = []
        excluded = []
        for peer_id, row in entries.items():
            _, latest = EventDate.model_validate(row['entry']['date']).bounds()
            assert latest is not None  # The accepted cohort rule requires known entry intervals.
            if peer_id == company_id:
                continue
            if latest >= cutoff:
                excluded.append(
                    {'company_id': peer_id, 'reason': 'Entry interval is not strictly before subject cutoff'}
                )
                continue
            peers.append(coverage(peer_id, cutoff))
        subjects[company_id] = dict(
            historical_cutoff=cutoff,
            subject=coverage(company_id, cutoff),
            eligible_peer_count=len(peers),
            confirmed_peers_at_field_bar=sum(peer['clears_field_bar'] for peer in peers),
            preview_peers_at_field_bar=sum(len(peer['preview_fields']) >= REQUIRED_FIELDS for peer in peers),
            potential_peers_after_review=sum(peer['would_clear_if_proposals_confirmed'] for peer in peers),
            peers=peers,
            excluded=excluded,
        )
    partly = subjects['public_partly']
    return dict(
        audit_version='backtest-coverage:1',
        compiled_on=packet.compiled_on,
        preregistration_commit=packet.preregistration_commit,
        packet_sha256=packet_sha256,
        cohort_input_sha256=packet.cohort_input_sha256,
        included_companies=len(entries),
        subjects=subjects,
        preview_gate=dict(
            provisional=True,
            label=PREVIEW_LABEL,
            actual_peers=partly['preview_peers_at_field_bar'],
            required_peers=REQUIRED_PEERS,
            required_fields=REQUIRED_FIELDS,
            shortfall=max(0, REQUIRED_PEERS - partly['preview_peers_at_field_bar']),
        ),
        gate=dict(
            passed=partly['confirmed_peers_at_field_bar'] >= REQUIRED_PEERS,
            required_peers=REQUIRED_PEERS,
            required_fields=REQUIRED_FIELDS,
            actual_peers=partly['confirmed_peers_at_field_bar'],
            shortfall=max(0, REQUIRED_PEERS - partly['confirmed_peers_at_field_bar']),
            next_phase='eligible_for_implementation'
            if partly['confirmed_peers_at_field_bar'] >= REQUIRED_PEERS
            else 'stop_before_scoring',
        ),
        limitations=[
            'Coverage of the current research packet, not proof that no other historical sources exist.',
            'Proposed extractions and existing profiles from other scopes are not human confirmations.',
            'No similarity scoring, comp selection or backtest evaluation is performed by this audit.',
        ],
    )
