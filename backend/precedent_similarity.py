"""Versioned mixed-feature similarity over witnessed, same-stage snapshots."""
import math
from types import MappingProxyType

from .precedent_contracts import DimensionScore, RankedPeer, SelectedComp
from .retrieval import tokens

VERSION = 'witnessed-gower-b0:1'
TOP_K = 12
MIN_SIMILARITY = .35
MIN_COVERAGE = .15
MIN_PEERS = 3
DIMENSIONS = MappingProxyType({
    'Clinical workflow': (.25, ('modality', 'clinical_user', 'output_type', 'description')),
    'Buyer and sales path': (.20, ('buyer', 'procurement_path', 'business_model')),
    'Regulatory path': (.15, ('regulatory_class', 'jurisdiction', 'regulatory_decision')),
    'Stage evidence': (.25, ('stage', 'prototype', 'provider_study', 'submission', 'paid_pilot', 'full_time_team')),
    'Funding context': (.15, ('months_since_founding', 'round_size_band', 'lead_investor_type')),
})
NUMERIC_RANGES = MappingProxyType({'months_since_founding': 120, 'regulatory_class': 2})
MILESTONES = {
    'prototype': 'What dated record establishes a working prototype?',
    'provider_study': 'Which provider or clinical study was carried out, and when?',
    'submission': 'What dated record establishes a regulatory submission?',
    'paid_pilot': 'What dated evidence establishes a paid customer or pilot?',
    'full_time_team': 'Which dated source establishes a full-time team?',
}


def features(row):
    values = {claim.field: claim.value for claim in row.snapshot}
    values.update({item.milestone: item.value for item in row.milestones if item.value != 'unknown'})
    return values


def corpus_idf(snapshots):
    documents = [tokens(str(snapshot.get('description', ''))) for snapshot in snapshots
                 if snapshot.get('description')]
    vocabulary = set().union(*documents)
    return {term: 1 + math.log((len(documents) + 1) / (1 + sum(term in doc for doc in documents)))
            for term in vocabulary}


def feature_similarity(key, left, right, idf):
    if key == 'description':
        a, b = tokens(str(left)), tokens(str(right))
        total = sum(idf[term] for term in sorted(a | b))
        return sum(idf[term] for term in sorted(a & b)) / total if total else None
    if key in NUMERIC_RANGES and isinstance(left, int) and isinstance(right, int):
        return max(0., 1 - abs(left - right) / NUMERIC_RANGES[key])
    return float(str(left).strip().casefold() == str(right).strip().casefold())


def score(left, right, idf):
    dimensions = []
    weighted_sum = 0.
    available_weight = 0.
    weighted_coverage = 0.
    for dimension, (weight, fields) in DIMENSIONS.items():
        scores = {key: feature_similarity(key, left[key], right[key], idf)
                  for key in fields if key in left and key in right}
        scores = {key: value for key, value in scores.items() if value is not None}
        coverage = len(scores) / len(fields)
        similarity = sum(scores.values()) / len(scores) if scores else None
        weighted_coverage += weight * coverage
        if similarity is not None:
            weighted_sum += weight * similarity
            available_weight += weight
        dimensions.append(DimensionScore(dimension=dimension, similarity=similarity, coverage=coverage,
            matched_fields=[key for key, value in scores.items() if value > 0],
            different_fields=[key for key, value in scores.items() if value < 1]))
    return weighted_sum / available_weight if available_weight else 0., weighted_coverage, dimensions


def rank_peers(subject, eligible_rows):
    left = features(subject)
    peer_features = [(row, features(row)) for row in eligible_rows]
    idf = corpus_idf([left, *(snapshot for _, snapshot in peer_features)])
    peers = []
    for row, values in peer_features:
        similarity, coverage, dimensions = score(left, values, idf)
        if similarity >= MIN_SIMILARITY and coverage >= MIN_COVERAGE:
            peers.append(RankedPeer(row=row, similarity=similarity, coverage=coverage, dimensions=dimensions))
    return sorted(peers, key=lambda peer: (-peer.similarity, peer.row.company_id))[:TOP_K]


def select_comps(peers):
    peers = sorted(peers, key=lambda peer: (-peer.similarity, peer.row.company_id))[:TOP_K]
    no_closure = not any(peer.row.status == 'closed_before_outcome' for peer in peers)
    if len(peers) < MIN_PEERS:
        return [], no_closure, f'Fewer than {MIN_PEERS} peers meet the similarity and evidence coverage requirements.'
    resolved = [peer for peer in peers if peer.row.outcome_rank is not None and peer.row.status != 'unknown']
    if not resolved:
        return [], no_closure, 'Outcome evidence is unresolved for all qualifying peers.'
    # For an even set, use the lower median outcome rank. The closest peer
    # represents each selected rank, even when several peers share it.
    ranks = sorted(peer.row.outcome_rank for peer in resolved)
    best_by_rank = {}
    for peer in resolved:
        best_by_rank.setdefault(peer.row.outcome_rank, peer)
    ceiling = best_by_rank[ranks[-1]]
    typical = best_by_rank[ranks[(len(ranks) - 1) // 2]]
    comps = [
        SelectedComp(role='ceiling', peer=ceiling, reason='Highest outcome rank among the closest peers.'),
        SelectedComp(role='typical', peer=typical, reason='Median outcome rank among the closest peers with a classified outcome.'),
    ]
    floor_pool = [peer for peer in resolved if (peer.row.status != 'lost_to_follow_up' if no_closure
                  else peer.row.status == 'closed_before_outcome')]
    if floor_pool:
        floor = min(floor_pool, key=lambda peer: peer.row.outcome_rank)
        comps.append(SelectedComp(role='floor', peer=floor, reason=(
            'Lowest observed outcome among the closest peers.' if no_closure
            else 'Closest peer with verified closure before the outcome.')))
    return comps, no_closure, None
