"""Source and date projections for same-stage comparisons."""
from collections import defaultdict
from datetime import date
import json

from .precedent_contracts import MilestoneValue, WorkbenchAnchor, WorkbenchClaim, WorkbenchPoint
from .precedent_similarity import MILESTONES
from .reference_pool import EventDate
from .research_adapter import research_time_interval

POOL_ANCHORS = {
    'first_provider_or_clinical_study': {'provider_deployment', 'clinical_study'},
    'first_regulatory_decision': {'regulatory_clearance', 'regulatory_decision'},
    'first_paid_customer': {'first_paid_customer'},
}
RESEARCH_ANCHORS = {
    'obs_ht_formus_reg23': 'regulatory_clearance',
    'obs_ht_volpara_reg10': 'regulatory_clearance',
    'obs_ht_formus_tr_reg': 'clinical_study',
}
RESEARCH_FIELDS = {
    'solution': 'description', 'technology': 'modality', 'intended_user': 'clinical_user',
    'documented_user': 'commercial_use', 'distribution_channel': 'procurement_path',
    'business_model': 'business_model', 'prototype_testing': 'prototype',
    'financing_amount': 'funding', 'regulatory_record': 'regulatory',
    'outcome': 'clinical_evidence', 'validation_requirement': 'validation_requirement',
}


def pool_claim(claim_id, field, value, passage, source, witnesses, *, when=None, basis=None, as_of):
    eligible = [w for w in witnesses if w.available_on <= as_of]
    witness = min(eligible, key=lambda w: (w.available_on, w.witness_id), default=None)
    if source.published_on and source.published_on > as_of:
        return None
    if source.retrieved_on > as_of and witness is None:
        return None
    lower, upper = when.bounds() if when else (None, None)
    if lower and lower > as_of:
        return None
    return WorkbenchClaim(claim_id=claim_id, field=field, value=value, passage=passage,
        publisher=source.publisher, url=source.url, published_on=source.published_on,
        retrieved_on=source.retrieved_on, witness=witness, lower_on=lower, upper_on=upper,
        date_value=when.value if when else None, date_precision=when.precision if when else None,
        date_basis=basis)


def research_claims(graph, subject_id, as_of):
    if not graph:
        return []
    packet = graph['packet']
    sources = {source['source_id']: source for source in packet['sources']}
    decisions = defaultdict(list)
    for review in packet['review_events']:
        if review['reviewed_on'] <= as_of:
            decisions[review['target_id']].append(review)
    claims = []
    for observation in packet['observations']:
        if observation['subject_id'] != subject_id or observation['field'] not in RESEARCH_FIELDS:
            continue
        source = sources[observation['source_id']]
        published = research_time_interval(source['published_time'])['upper_bound']
        if source['retrieved_on'] > as_of or (published and published > as_of):
            continue
        effective = observation['effective_time']
        bounds = research_time_interval(effective)
        if bounds['lower_bound'] and bounds['lower_bound'] > as_of:
            continue
        claim_id = observation['observation_id']
        state = observation['review']['state']
        reviews = decisions[claim_id]
        if reviews:
            latest_day = max(review['reviewed_on'] for review in reviews)
            if any(review['decision'] != 'accepted' for review in reviews if review['reviewed_on'] == latest_day):
                state = 'disputed'
        claims.append(WorkbenchClaim(claim_id=claim_id,
            field=RESEARCH_ANCHORS.get(claim_id, RESEARCH_FIELDS[observation['field']]),
            value=observation['paraphrase'], passage=observation['locator'],
            publisher=source['publisher'], url=source['url'], published_on=published,
            retrieved_on=source['retrieved_on'], date_value=effective['value'],
            date_precision=effective['precision'], lower_on=bounds['lower_bound'], upper_on=bounds['upper_bound'],
            date_basis=effective['basis'], review_state=state))
    return claims


def select_anchor(kind, claims, entry_claim_id, as_of):
    eligible = [claim for claim in claims if claim.upper_on and claim.upper_on <= as_of and
                claim.review_state != 'disputed' and (claim.claim_id == entry_claim_id
                if kind == 'first_institutional_round' else claim.field in POOL_ANCHORS[kind])]
    if not eligible:
        return None
    earliest = min(eligible, key=lambda c: (c.lower_on, c.upper_on, c.claim_id))
    # Overlapping intervals for different events cannot prove which came first.
    if any(c.lower_on <= earliest.upper_on
           and (c.lower_on, c.upper_on) != (earliest.lower_on, earliest.upper_on)
           for c in eligible if c.claim_id != earliest.claim_id):
        return None
    return WorkbenchAnchor(kind=kind, claim=earliest)


def points_for(anchor, events, as_of):
    if not anchor:
        return []
    start = date.fromisoformat(anchor.claim.lower_on)
    end = date.fromisoformat(anchor.claim.upper_on)
    points = []
    for claim in sorted(events, key=lambda c: (c.lower_on or '9999', c.claim_id)):
        if not claim.upper_on or claim.upper_on > as_of or claim.review_state == 'disputed':
            continue
        is_anchor = claim.claim_id == anchor.claim.claim_id
        lower = 0 if is_anchor else (date.fromisoformat(claim.lower_on) - end).days
        upper = (date.fromisoformat(claim.upper_on) - start).days
        points.append(WorkbenchPoint(claim=claim, lower_days=lower, upper_days=upper, is_anchor=is_anchor))
    return points


def snapshot_at(anchor, claims):
    # Requiring the earliest possible anchor date prevents look-ahead for partial dates.
    return snapshot_by(anchor.claim.lower_on, claims) if anchor else []


def snapshot_by(cutoff, claims):
    candidates = [claim for claim in claims if claim.witness and claim.witness.available_on <= cutoff
        and (claim.published_on is None or claim.published_on <= cutoff)
        and (claim.upper_on is None or claim.upper_on <= cutoff)
        and claim.review_state != 'disputed']
    return candidates


def checklist(snapshot):
    result = []
    for milestone in MILESTONES:
        by_value = {value: [item.claim_id for item in snapshot if item.field == milestone
                            and item.value == value and item.upper_on]
                    for value in ('yes', 'no')}
        supported = [value for value, ids in by_value.items() if ids]
        value = supported[0] if len(supported) == 1 else 'unknown'
        result.append(MilestoneValue(milestone=milestone, value=value,
            claim_ids=sorted({claim_id for ids in by_value.values() for claim_id in ids})))
    return result


def fixture_feature_claims(conn, digest, packet, company_id, as_of):
    if not packet:
        return []
    sources = {source.source_id: source for source in packet.sources}
    witnesses = {w.witness_id: w for w in packet.witnesses}
    rows = conn.execute("""
        SELECT f.*, s.as_of AS snapshot_day
        FROM pool_snapshot_features f JOIN pool_snapshots s USING (packet_sha256, snapshot_id)
        JOIN pool_witnesses w USING (packet_sha256, witness_id, source_id)
        WHERE s.packet_sha256=? AND s.company_id=? AND w.available_on<=s.as_of
        ORDER BY s.as_of, f.snapshot_id, f.feature
        """, (digest, company_id))
    return [claim for row in rows if (claim := pool_claim(
        f"{row['snapshot_id']}:{row['feature']}", row['feature'], json.loads(row['value_json']),
        row['passage'], sources[row['source_id']], [witnesses[row['witness_id']]],
        when=EventDate(value=row['snapshot_day'], precision='day'), basis='Source-backed snapshot', as_of=as_of))]
