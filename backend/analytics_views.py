"""Provisional analytics over the frozen entry snapshots and cohort audit."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
import json
from random import Random
from typing import Any, cast

from .backtest import (
    THRESHOLDS,
    BacktestInputs,
    EntryEvidence,
    current_inputs,
    date_bounds,
    elapsed,
    event_payload,
)
from .backtest_contracts import BacktestEvent, BacktestSource
from .backtest_coverage import PREVIEW_LABEL, REQUIRED_FIELDS, SUBJECTS
from .cohort_follow_up import CoverageReview, assess
from .outcome_library import HEALTHTECH_SECTORS
from .precedent_similarity import MIN_PEERS, TOP_K
from .precedent_similarity_general import (
    DIMENSIONS,
    MIN_COVERAGE,
    MIN_PRODUCT,
    MIN_SIMILARITY,
    ROUND_BANDS,
    VERSION,
    VOCABULARY,
    FieldValue,
    PairScore,
    description_idf,
    normalise,
    score,
)
from .reference_pool import EventDate, PoolEvent, Status, plus_months
from .retrieval import INFLECTIONS, STOP, tokens
from .witnessed_snapshots import BACKTEST_FIELDS, BACKTEST_MILESTONES
from .workbench_gates import gate_progress

PRESETS: dict[str, tuple[str, dict[str, FieldValue]]] = {
    'recorded': ('Recorded', {}),
    'business': ('Business buyer', {'buyer': 'business'}),
    'subscription': ('Business + subscription', {'buyer': 'business', 'business_model': 'subscription'}),
    'software': ('Software', {'product_type': 'software'}),
    'software_business': ('Software + business', {'product_type': 'software', 'buyer': 'business'}),
    'revenue': ('Revenue', {'paid_pilot_or_revenue': 'yes'}),
}
LABEL = {'provisional': True, 'label': PREVIEW_LABEL}
WEIGHTS = tuple(weight for weight, _ in DIMENSIONS.values())
DELTA = 0.05


def dump_json(payload: Any) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode()


def json_record(model: Any) -> dict[str, Any]:
    return model.model_dump(mode='json')


@dataclass(frozen=True)
class PeerInput:
    evidence: EntryEvidence
    rank: int | None


@dataclass(frozen=True)
class Comparison:
    company_id: str
    cutoff: str
    subject: EntryEvidence
    eligible: dict[str, PeerInput]


@lru_cache(maxsize=12)
def comparison(inputs: BacktestInputs, company_id: str) -> Comparison:
    if company_id not in SUBJECTS:
        raise KeyError(company_id)
    cutoff, _ = date_bounds(EventDate.model_validate(inputs.entries[company_id]['date']))
    peers: dict[str, PeerInput] = {}
    for key, entry in inputs.entries.items():
        when = EventDate.model_validate(entry['date'])
        if key == company_id or date_bounds(when)[1] >= cutoff:
            continue
        evidence = inputs.evidence(key, cutoff, 'strict')
        _, outcome = inputs.history.peer(entry, when, cutoff, 'as_of_anchor')
        peers[key] = PeerInput(evidence, outcome.rank if outcome else None)
    return Comparison(company_id, cutoff, inputs.evidence(company_id, cutoff, 'strict'), peers)


def override_options() -> dict[str, list[str]]:
    return {
        **{field: sorted(tree.nodes()) for field, tree in VOCABULARY.fields.items()},
        **{field: ['yes', 'no'] for field in BACKTEST_MILESTONES},
        'round_size_band': list(ROUND_BANDS),
    }


def validate_overrides(overrides: dict[str, FieldValue]) -> dict[str, FieldValue]:
    options = override_options()
    for field, value in overrides.items():
        if field == 'months_since_founding' and type(value) is int and value >= 0:
            continue
        if field == 'description' and isinstance(value, str) and len(value) <= 2000 and tokens(value):
            continue
        if field in options and isinstance(value, str):
            normalized, _ = normalise({field: value})
            if normalized.get(field) in options[field]:
                continue
        raise ValueError(f'Invalid scenario value for {field}')
    return normalise(overrides)[0]


def pair_scores(frame: Comparison, values: dict[str, FieldValue]) -> dict[str, PairScore]:
    if not values:
        return {}
    idf = description_idf(
        [
            values,
            *(peer.evidence.values for peer in frame.eligible.values() if len(peer.evidence.values) >= REQUIRED_FIELDS),
        ]
    )
    result = {}
    for key, peer in frame.eligible.items():
        if peer.evidence.values:
            pair = score(values, peer.evidence.values, idf)
            if pair.fields:
                result[key] = pair
    return result


def score_key(value: float) -> float:
    return round(value, 12)


def tie_groups(scores: dict[str, float]) -> list[list[str]]:
    groups: dict[float, list[str]] = defaultdict(list)
    for key, value in scores.items():
        groups[score_key(value)].append(key)
    return [sorted(groups[value]) for value in sorted(groups, reverse=True)]


def roles(frame: Comparison, admitted: dict[str, float]) -> dict[str, list[str]]:
    """Return role possibilities at equal ranks/scores, within the frozen top-k boundary."""
    if len(admitted) < MIN_PEERS:
        return {}
    pool = sorted(admitted, key=lambda key: (-admitted[key], key))[:TOP_K]
    resolved = {key: rank for key in pool if (rank := frame.eligible[key].rank) is not None}
    if not resolved:
        return {}
    ranks = sorted(resolved.values())

    def best(keys: list[str]) -> list[str]:
        return tie_groups({key: admitted[key] for key in keys})[0]

    if ranks[0] == ranks[-1]:
        return {'representative': best(list(resolved))}
    ceiling = best([key for key, rank in resolved.items() if rank == ranks[-1]])
    floor = best([key for key, rank in resolved.items() if rank == ranks[0]])
    typical: set[str] = set()
    median = ranks[(len(ranks) - 1) // 2]
    for high in ceiling:
        for low in floor:
            remaining = {key: abs(rank - median) for key, rank in resolved.items() if key not in (high, low)}
            if remaining:
                typical.update(
                    best([key for key, distance in remaining.items() if distance == min(remaining.values())])
                )
    return {'ceiling': ceiling, 'floor': floor, **({'typical': sorted(typical)} if typical else {})}


def admitted_scores(frame: Comparison, values: dict[str, FieldValue], pairs: dict[str, PairScore]) -> dict[str, float]:
    return {
        key: pair.similarity
        for key, pair in pairs.items()
        if not pair.failed_bars(len(values), len(frame.eligible[key].evidence.values), REQUIRED_FIELDS)
    }


def scenario_result(frame: Comparison, overrides: dict[str, FieldValue], *, hypothetical: bool) -> dict[str, Any]:
    values = {**frame.subject.values, **overrides}
    pairs = pair_scores(frame, values)
    admitted = admitted_scores(frame, values, pairs)
    baseline = pair_scores(frame, frame.subject.values) if overrides else pairs
    baseline_roles = roles(frame, admitted_scores(frame, frame.subject.values, baseline))
    selected_roles = roles(frame, admitted)
    peers = []
    for key, peer in frame.eligible.items():
        pair = pairs.get(key)
        peers.append(
            {
                'company_id': key,
                'similarity': pair.similarity if pair else None,
                'coverage': pair.coverage if pair else 0,
                'product_customer': pair.dimensions[0].similarity if pair else None,
                'shared_fields': len(pair.fields) if pair else 0,
                'field_scores': pair.fields if pair else {},
                'dimensions': [json_record(dim) for dim in pair.dimensions] if pair else [],
                'qualifies': key in admitted,
                'failed_bars': pair.failed_bars(len(values), len(peer.evidence.values), REQUIRED_FIELDS)
                if pair
                else ['no_shared_evidence'],
            }
        )
    return {
        **LABEL,
        'scenario': hypothetical,
        'company_id': frame.company_id,
        'cutoff': frame.cutoff,
        'similarity_version': VERSION,
        'thresholds': json_record(THRESHOLDS),
        'overrides': overrides,
        'qualifying_count': len(admitted),
        'peers': peers,
        'roles': selected_roles,
        'changed_roles': {
            role: {'recorded': baseline_roles.get(role, []), 'scenario': selected_roles.get(role, [])}
            for role in sorted(baseline_roles.keys() | selected_roles.keys())
            if baseline_roles.get(role) != selected_roles.get(role)
        },
    }


def reweight(pair: PairScore, weights: tuple[float, ...]) -> tuple[float, float]:
    active = [(w, d.similarity) for w, d in zip(weights, pair.dimensions) if d.similarity is not None]
    return (
        sum(w * s for w, s in active) / sum(w for w, _ in active),
        sum(w * d.coverage for w, d in zip(weights, pair.dimensions)),
    )


@lru_cache(maxsize=64)
def robustness(inputs: BacktestInputs, company_id: str, draws: int, seed: int) -> dict[str, Any]:
    frame = comparison(inputs, company_id)
    pairs = pair_scores(frame, frame.subject.values)
    baseline = tie_groups({key: pair.similarity for key, pair in pairs.items()})
    baseline_roles = roles(frame, admitted_scores(frame, frame.subject.values, pairs))
    members: Counter[str] = Counter()
    boundary_ties: Counter[tuple[str, ...]] = Counter()
    ranges: dict[str, dict[str, list[float]]] = {key: {} for key in pairs}
    perturbations = []

    def rank(weights: tuple[float, ...]) -> tuple[dict[str, float], list[list[str]], dict[str, list[str]]]:
        scores = {}
        admitted = {}
        for key, pair in pairs.items():
            similarity, coverage = reweight(pair, weights)
            scores[key] = similarity
            if (
                similarity >= MIN_SIMILARITY
                and coverage >= MIN_COVERAGE
                and (pair.dimensions[0].similarity or 0) >= MIN_PRODUCT
                and min(len(frame.subject.values), len(frame.eligible[key].evidence.values)) >= REQUIRED_FIELDS
            ):
                admitted[key] = similarity
        return scores, tie_groups(scores), roles(frame, admitted)

    for i, name in enumerate(DIMENSIONS):
        ends = []
        for delta in (-DELTA, DELTA):
            weights = tuple(
                base + delta if j == i else base * (1 - WEIGHTS[i] - delta) / (1 - WEIGHTS[i])
                for j, base in enumerate(WEIGHTS)
            )
            scores, groups, role_map = rank(weights)
            ends.append(scores)
            perturbations.append(
                {
                    'dimension': name,
                    'delta': delta,
                    'weights': dict(zip(DIMENSIONS, weights)),
                    'ranks': groups,
                    'roles': role_map,
                    'changed_roles': [
                        role
                        for role in sorted(role_map.keys() | baseline_roles.keys())
                        if role_map.get(role) != baseline_roles.get(role)
                    ],
                }
            )
        for key in pairs:
            ranges[key][name] = sorted([ends[0][key], ends[1][key]])
    rng = Random(seed)
    for _ in range(draws):
        varied = tuple(w + rng.uniform(-DELTA, DELTA) for w in WEIGHTS)
        total = sum(varied)
        _, groups, _ = rank(tuple(w / total for w in varied))
        rank_start = 0
        for group in groups:
            if rank_start >= 3:
                break
            members.update(group)
            if rank_start + len(group) > 3:
                boundary_ties[tuple(group)] += 1
            rank_start += len(group)
    return {
        **LABEL,
        'company_id': company_id,
        'cutoff': frame.cutoff,
        'similarity_version': VERSION,
        'input_sha256': inputs.digests,
        'draws': draws,
        'seed': seed,
        'baseline_ranks': baseline,
        'membership': dict(members),
        'ranges': ranges,
        'perturbations': perturbations,
        'boundary_ties': [{'companies': keys, 'draws': count} for keys, count in sorted(boundary_ties.items())],
    }


def entry_event(inputs: BacktestInputs, row: dict[str, Any]) -> BacktestEvent:
    entry = EventDate.model_validate(row['date'])
    start, end = date_bounds(entry)
    source = inputs.history.sources[row['source_id']]
    witnesses = inputs.history.witnesses[source.source_id]
    witness = min(witnesses, key=lambda item: (item.available_on, item.witness_id), default=None)
    return BacktestEvent(
        event_id='entry:' + row['company_id'],
        kind='seed',
        date=entry,
        source=BacktestSource(
            source_id=source.source_id,
            publisher=source.publisher,
            url=witness.url if witness else source.url,
            locator=row['locator'],
            available_on=max(
                end,
                source.published_on or '',
                source.revised_on or '',
                witness.available_on if witness else source.retrieved_on,
            ),
            published_on=source.published_on,
            witness_id=witness.witness_id if witness else None,
            witness_on=witness.available_on if witness else None,
        ),
        lower_days=0,
        upper_days=elapsed(start, end),
        review_state='dated_source' if witness else 'source_recorded',
    )


def status_clock(
    row: dict[str, Any],
    events: list[PoolEvent],
    clocks: dict[str, str],
    review: CoverageReview | None,
    end: str,
) -> list[tuple[str, Status, str | None]]:
    """Materialize transitions at evidence dates for offline historical counts."""
    dates = {end, *clocks.values()}
    if review:
        dates.add(review.reviewed_on)
    clock: list[tuple[str, Status, str | None]] = []
    for cutoff in sorted(date for date in dates if date <= end):
        known = [event for event in events if clocks[event.event_id] <= cutoff]
        result = assess(row, known, review if review and review.reviewed_on <= cutoff else None)
        state = (cast(Status, result['status']), cast(str | None, result['outcome_event_id']))
        if not clock or clock[-1][1:] != state:
            clock.append((cutoff, *state))
    return clock


@lru_cache(maxsize=4)
def cohort_payload(inputs: BacktestInputs) -> dict[str, Any]:
    follow = inputs.cohort['follow_up']
    companies = []
    details = {}
    for company_id, row in inputs.entries.items():
        entry = entry_event(inputs, row)
        start, end = date_bounds(entry.date)
        checked = inputs.history.events(company_id, follow['as_of'], allow_retrospective=True)
        decision = follow['decisions'][company_id]
        review = CoverageReview.model_validate(decision['review']) if decision['review'] else None
        events = [event_payload(event, start) for event in checked]
        companies.append(
            {
                'company_id': company_id,
                'name': row['name'],
                'sector': row['sector'],
                'sector_group': 'Healthtech'
                if row['sector'].casefold() in HEALTHTECH_SECTORS or 'medtech' in row['sector'].casefold()
                else 'Other sectors',
                'entry': json_record(entry),
                'start': start,
                'end': end,
                'year': int(start[:4]),
                'horizon': plus_months(end, 36),
            }
        )
        fields = {}
        for item in inputs.profiles.get(company_id, []):
            source = inputs.sources[item.source_id]
            witness = inputs.witnesses[item.witness_id]
            fields[item.name] = {
                'name': item.name,
                'value': item.value,
                'review_state': item.review_state,
                'second_reading_matched': item.readings_match == 'Yes',
                'reviewed_by': item.decided_by or item.reviewer,
                'reviewed_on': item.review_date or item.reviewed_on,
                'source': json_record(
                    BacktestSource(
                        source_id=source.source_id,
                        url=witness.url,
                        publisher=source.publisher,
                        locator=item.locator,
                        available_on=max(
                            witness.available_on,
                            source.published_on or '',
                            source.revised_on or '',
                            item.effective_on or '',
                        ),
                        published_on=source.published_on,
                        witness_id=witness.witness_id,
                        witness_on=witness.available_on,
                    )
                ),
            }
        details[company_id] = {
            'events': [json_record(event) for event in events],
            'fields': fields,
            'status_clock': status_clock(
                row,
                [item.event for item in checked],
                {item.event.event_id: item.source.available_on for item in checked},
                review,
                follow['as_of'],
            ),
            'status': decision['status'],
            'outcome_event_id': decision['outcome_event_id'],
        }
    return {
        **LABEL,
        'audit_date': follow['as_of'],
        'candidate_records': inputs.cohort['candidate_records'],
        'fields': list(BACKTEST_FIELDS),
        'subjects': list(SUBJECTS),
        'companies': companies,
        'reveal': details,
        'gates': json_record(gate_progress(inputs.cohort)),
        'preview_peers': inputs.audit['preview_gate']['actual_peers'],
        'strict_gate_passed': inputs.audit['gate']['passed'],
        'input_sha256': inputs.digests,
    }


@lru_cache(maxsize=12)
def profile_payload(inputs: BacktestInputs, company_id: str) -> dict[str, Any]:
    frame = comparison(inputs, company_id)
    return {
        **LABEL,
        'company_id': company_id,
        'cutoff': frame.cutoff,
        'input_sha256': inputs.digests,
        'fields': [json_record(field) for field in frame.subject.fields.values()],
        'reveal': {
            'evidence_reviews': [
                json_record(review)
                for evidence in (frame.subject, *(peer.evidence for peer in frame.eligible.values()))
                for review in evidence.reviews
            ]
        },
        'covered_peer_ids': [
            key for key, peer in frame.eligible.items() if len(peer.evidence.values) >= REQUIRED_FIELDS
        ],
        'peer_facts': {
            key: [json_record(field) for field in peer.evidence.fields.values()]
            for key, peer in frame.eligible.items()
            if peer.evidence.values
        },
        'recorded': scenario_result(frame, {}, hypothetical=False),
        'presets': [
            {'id': key, 'name': name, 'result': scenario_result(frame, values, hypothetical=True)}
            for key, (name, values) in PRESETS.items()
        ],
        'scorer': {
            'dimensions': [
                {'name': key, 'weight': weight, 'fields': fields} for key, (weight, fields) in DIMENSIONS.items()
            ],
            'vocabulary': {
                key: {'nodes': value.nodes(), 'flat': value.flat, 'aliases': value.aliases}
                for key, value in VOCABULARY.fields.items()
            },
            'bands': ROUND_BANDS,
            'stop': sorted(STOP),
            'inflections': INFLECTIONS,
            'options': override_options(),
            'subject': frame.subject.values,
            'peers': {key: {'values': peer.evidence.values, 'rank': peer.rank} for key, peer in frame.eligible.items()},
        },
    }


def live_inputs() -> BacktestInputs:
    return current_inputs('preview')
