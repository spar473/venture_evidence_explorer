"""Score historical entry evidence and project clock-filtered peer histories."""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Literal, cast

from .backtest_contracts import (
    BacktestComp,
    BacktestEvent,
    BacktestExclusion,
    BacktestField,
    BacktestHistory,
    BacktestNearest,
    BacktestPeerScore,
    BacktestResponse,
    BacktestReveal,
    BacktestReviewMetadata,
    BacktestSource,
    BacktestSubject,
    BacktestThresholds,
    EvidenceMode,
    PeerHistory,
    Track,
)
from .backtest_coverage import PREVIEW_LABEL, REQUIRED_FIELDS, REQUIRED_PEERS, SUBJECTS, audit_packet
from .backtest_review import DECISIONS, apply_review
from .cohort_audit import ENTRIES, FOLLOW_UP, PACK, run_audit
from .cohort_follow_up import CoverageReview, assess
from .precedent_contracts import CompOutcome, RankedPeer, WorkbenchAnchor, WorkbenchClaim, WorkbenchRow
from .precedent_similarity import MIN_PEERS, TOP_K, select_comps
from .precedent_similarity_general import (
    MIN_COVERAGE,
    MIN_PRODUCT,
    MIN_SIMILARITY,
    VERSION,
    VOCABULARY_DIGEST,
    FieldValue,
    description_idf,
    normalise,
    score,
)
from .precedents import cohort_source, comp_outcome
from .reference_pool import EventDate, PoolEvent, PoolSource, Status, Witness, plus_months
from .witnessed_snapshots import BACKTEST_FIELDS, BACKTEST_PACKET, BacktestFeature, BacktestSnapshotPacket

FROZEN_OUTCOME_DATE = '2026-11-21'
THRESHOLDS = BacktestThresholds(
    similarity=MIN_SIMILARITY,
    coverage=MIN_COVERAGE,
    product_customer=MIN_PRODUCT,
    fields=REQUIRED_FIELDS,
    peers=MIN_PEERS,
    top_k=TOP_K,
)


def date_bounds(event_date: EventDate) -> tuple[str, str]:
    start, end = event_date.bounds()
    if start is None or end is None:
        raise ValueError('Backtest requires a dated interval')
    return start, end


def elapsed(start: str, end: str) -> int:
    return (date.fromisoformat(end) - date.fromisoformat(start)).days


@dataclass(frozen=True)
class EntryEvidence:
    fields: dict[str, BacktestField]
    values: dict[str, FieldValue]
    unknown: dict[str, FieldValue]
    reviews: list[BacktestReviewMetadata]


def entry_evidence(
    features: list[BacktestFeature],
    sources: dict[str, PoolSource],
    witnesses: dict[str, Witness],
    *,
    entry_start: str,
    cutoff: str,
    mode: EvidenceMode,
    state: Literal['confirmed', 'ai_adjudicated'],
) -> EntryEvidence:
    fields, reviews = {}, []
    for feature in features:
        if feature.review_state != state or (feature.timing == 'lenient' and mode == 'strict'):
            continue
        source, witness = sources[feature.source_id], witnesses[feature.witness_id]
        public_by = max(
            witness.available_on, source.published_on or '', source.revised_on or '', feature.effective_on or ''
        )
        if public_by > cutoff:
            continue
        fields[feature.name] = BacktestField(
            name=feature.name,
            value=feature.value,
            raw_value=feature.raw_value,
            rationale=feature.rationale,
            source=BacktestSource(
                source_id=source.source_id,
                publisher=source.publisher,
                url=witness.url,
                locator=feature.locator,
                available_on=public_by,
                published_on=source.published_on,
                witness_id=witness.witness_id,
                witness_on=witness.available_on,
            ),
            review_state=state,
            second_reading_matched=feature.readings_match == 'Yes',
            delay_days=max(0, elapsed(entry_start, public_by)),
        )
        checked_by = feature.decided_by or feature.reviewer
        reviewed_on = feature.review_date or feature.reviewed_on
        if checked_by and reviewed_on:
            reviews.append(
                BacktestReviewMetadata(
                    company_id='',
                    field=feature.name,
                    reviewed_by=checked_by,
                    reviewed_on=reviewed_on,
                )
            )
    values, unknown = normalise({name: item.value for name, item in fields.items()})
    return EntryEvidence(fields, values, unknown, reviews)


@dataclass(frozen=True)
class ClockedEvent:
    event: PoolEvent
    source: BacktestSource


class History:
    def __init__(self, follow_up: dict[str, Any], entry_sources: dict[str, Any]):
        self.follow_up = follow_up
        self.sources = {
            **{key: cohort_source(key, value) for key, value in entry_sources.items()},
            **{key: PoolSource.model_validate(value) for key, value in follow_up['sources'].items()},
        }
        self.witnesses: dict[str, list[Witness]] = defaultdict(list)
        for raw in follow_up['witnesses'].values():
            witness = Witness.model_validate(raw)
            self.witnesses[witness.source_id].append(witness)

    def events(self, company_id: str, limit: str, *, allow_retrospective: bool) -> list[ClockedEvent]:
        rows = []
        for raw in self.follow_up['decisions'][company_id]['events']:
            event = PoolEvent.model_validate(raw)
            _, latest = event.date.bounds()
            if latest is None or latest > limit or event.entity_link != 'supported':
                continue
            source = self.sources[event.source_id]
            dated_versions = self.witnesses.get(event.source_id, [])
            witness = min(dated_versions, key=lambda item: (item.available_on, item.witness_id), default=None)
            if witness is None and not allow_retrospective:
                continue
            public_by = max(
                latest,
                source.published_on or '',
                source.revised_on or '',
                witness.available_on if witness else source.retrieved_on,
            )
            if public_by <= limit:
                rows.append(
                    ClockedEvent(
                        event,
                        BacktestSource(
                            source_id=source.source_id,
                            publisher=source.publisher,
                            url=witness.url if witness else source.url,
                            locator=event.passage,
                            available_on=public_by,
                            published_on=source.published_on,
                            witness_id=witness.witness_id if witness else None,
                            witness_on=witness.available_on if witness else None,
                        ),
                    )
                )
        return sorted(rows, key=lambda row: (*date_bounds(row.event.date), row.event.event_id))

    def review(self, company_id: str, limit: str) -> dict[str, Any] | None:
        review = self.follow_up['decisions'][company_id]['review']
        if review and review['searched_through'] <= review['reviewed_on'] <= limit:
            return review
        return None

    def peer(
        self,
        entry: dict[str, Any],
        entry_date: EventDate,
        cutoff: str,
        history: PeerHistory,
    ) -> tuple[BacktestHistory, CompOutcome | None]:
        limit = min(self.follow_up['as_of'], FROZEN_OUTCOME_DATE) if history == 'today' else cutoff
        start, last = date_bounds(entry_date)
        rows = [
            item
            for item in self.events(entry['company_id'], limit, allow_retrospective=history == 'today')
            if date_bounds(item.event.date)[0] > last
        ]
        review = self.review(entry['company_id'], limit)
        primary = assess(
            entry, [item.event for item in rows], CoverageReview.model_validate(review) if review else None
        )
        horizon = min(plus_months(last, 36), limit)
        records = [(item.event, event_claim(item)) for item in rows if date_bounds(item.event.date)[1] <= horizon]
        # The entry is used only for interval ordering inside the shared role selector.
        start_claim = WorkbenchClaim(
            claim_id='entry',
            field='entry',
            value='Entry',
            passage=entry['locator'],
            publisher='',
            url='',
            published_on=None,
            retrieved_on=start,
            lower_on=start,
            upper_on=last,
        )
        outcome = comp_outcome(
            WorkbenchAnchor(kind='first_institutional_round', claim=start_claim),
            records,
            review,
            horizon,
        )
        complete = primary['observed_at_36_months'] is True
        if outcome and outcome.rank in (1, 2) and not complete:
            outcome = None
        status = cast(Status, primary['status'])
        if not complete and status in ('lost_to_follow_up', 'observed_no_outcome'):
            status = 'unknown'
        return BacktestHistory(
            events=[event_payload(item, start, hindsight=item.source.available_on > cutoff) for item in rows],
            follow_up_days=elapsed(start, limit),
            status=status,
        ), outcome

    def reveal(
        self,
        subject: BacktestSubject,
        reviews: list[BacktestReviewMetadata],
    ) -> BacktestReveal:
        decision = self.follow_up['decisions'][subject.company_id]
        horizon = decision['latest_horizon']
        start, last = date_bounds(subject.entry)
        rows = [
            event_payload(item, start)
            for item in self.events(
                subject.company_id, min(self.follow_up['as_of'], FROZEN_OUTCOME_DATE), allow_retrospective=True
            )
            if date_bounds(item.event.date)[0] > last
        ]
        return BacktestReveal(
            status=decision['status'],
            through=horizon,
            evidence_reviews=reviews,
            events=[row for row in rows if date_bounds(row.date)[1] <= horizon],
            later_events=[row for row in rows if date_bounds(row.date)[0] > horizon],
        )


def event_claim(item: ClockedEvent) -> WorkbenchClaim:
    start, end = date_bounds(item.event.date)
    return WorkbenchClaim(
        claim_id=item.event.event_id,
        field=item.event.kind,
        value=item.event.kind,
        passage=item.source.locator,
        publisher=item.source.publisher,
        url=item.source.url,
        published_on=item.source.published_on,
        retrieved_on=item.source.available_on,
        date_value=item.event.date.value,
        date_precision=item.event.date.precision,
        lower_on=start,
        upper_on=end,
    )


def event_payload(item: ClockedEvent, start: str, *, hindsight: bool = False) -> BacktestEvent:
    lower, upper = date_bounds(item.event.date)
    return BacktestEvent(
        event_id=item.event.event_id,
        kind=item.event.kind,
        date=item.event.date,
        source=item.source,
        lower_days=elapsed(start, lower),
        upper_days=elapsed(start, upper),
        review_state='dated_source' if item.source.witness_id else 'source_recorded',
        hindsight=hindsight,
    )


class BacktestInputs:
    def __init__(self, path: Path = BACKTEST_PACKET, decisions: Path = DECISIONS, *, track: Track = 'preview'):
        raw = path.read_bytes()
        packet = BacktestSnapshotPacket.model_validate_json(raw)
        self.digests = {
            **packet.cohort_input_sha256,
            'packet': sha256(raw).hexdigest(),
            'vocabulary': VOCABULARY_DIGEST,
        }
        if track == 'preview':
            self.digests['decisions'] = sha256(decisions.read_bytes()).hexdigest()
            packet = apply_review(packet, decisions)
        self.cohort = cast(dict[str, Any], run_audit())
        self.audit = audit_packet(packet, self.digests['packet'], cohort=self.cohort)
        self.history = History(self.cohort['follow_up'], self.cohort['sources'])
        self.digests['follow_up'] = self.cohort['follow_up']['evidence_sha256']
        self.packet = packet
        self.entries = {
            row['company_id']: row['entry'] for row in self.cohort['decisions'] if row['status'] == 'included'
        }
        self.profiles = {profile.company_id: profile.features for profile in packet.profiles}
        self.sources = {source.source_id: source for source in packet.sources}
        self.witnesses = {witness.witness_id: witness for witness in packet.witnesses}
        self.track: Track = track

    def evidence(self, company_id: str, cutoff: str, mode: EvidenceMode) -> EntryEvidence:
        start, _ = date_bounds(EventDate.model_validate(self.entries[company_id]['date']))
        item = entry_evidence(
            self.profiles.get(company_id, []),
            self.sources,
            self.witnesses,
            entry_start=start,
            cutoff=cutoff,
            mode=mode,
            state='ai_adjudicated' if self.track == 'preview' else 'confirmed',
        )
        return EntryEvidence(
            item.fields,
            item.values,
            item.unknown,
            [row.model_copy(update={'company_id': company_id}) for row in item.reviews],
        )


@lru_cache(maxsize=4)
def load_inputs(track: Track, versions: tuple[int, ...]) -> BacktestInputs:
    return BacktestInputs(track=track)


def current_inputs(track: Track) -> BacktestInputs:
    paths = [BACKTEST_PACKET, ENTRIES, FOLLOW_UP, PACK]
    if track == 'preview':
        paths.append(DECISIONS)
    return load_inputs(track, tuple(path.stat().st_mtime_ns for path in paths))


def render_backtest(
    inputs: BacktestInputs,
    company_id: str,
    mode: EvidenceMode = 'strict',
    history: PeerHistory = 'as_of_anchor',
) -> BacktestResponse:
    record = inputs.entries[company_id]
    entry = EventDate.model_validate(record['date'])
    cutoff, _ = date_bounds(entry)
    preview = inputs.track == 'preview'
    gate = inputs.audit['gate']['passed']
    subject = BacktestSubject(company_id=company_id, display_name=record['name'], entry=entry, cutoff=cutoff, fields=[])
    result = BacktestResponse(
        track=inputs.track,
        witness_mode=mode,
        peer_history=history,
        hindsight=history == 'today',
        provisional=preview,
        label=PREVIEW_LABEL if preview else None,
        strict_gate_passed=gate,
        preview_peers=inputs.audit['preview_gate']['actual_peers'] if preview else None,
        required_peers=REQUIRED_PEERS,
        similarity_version=VERSION,
        preregistration_commit=inputs.packet.preregistration_commit,
        input_sha256=inputs.digests,
        thresholds=THRESHOLDS,
        subject=subject,
    )
    if not preview and not gate:
        result.abstention = 'strict_gate'
        return result

    left = inputs.evidence(company_id, cutoff, 'strict')
    subject.fields = list(left.fields.values())
    # An entry announcement is displayed only when the same dated source exists in the strict evidence.
    subject.entry_round_source = next(
        (
            field.source
            for field in subject.fields
            if field.source.published_on == cutoff
            and field.source.url == inputs.cohort['sources'][record['source_id']]['url']
        ),
        None,
    )
    result.reveal = inputs.history.reveal(subject, left.reviews)

    peers = {}
    for peer_id, row in inputs.entries.items():
        if peer_id == company_id:
            continue
        _, last = date_bounds(EventDate.model_validate(row['date']))
        if last >= cutoff:
            result.excluded.append(BacktestExclusion(company_id=peer_id, reason='entry_not_before_cutoff'))
            continue
        peers[peer_id] = inputs.evidence(peer_id, cutoff, mode)
    result.eligible_peer_ids = list(peers)
    covered = {key: item for key, item in peers.items() if len(item.values) >= REQUIRED_FIELDS}
    result.covered_peer_ids = list(covered)
    result.unknown_tokens = {key: item.unknown for key, item in {company_id: left, **peers}.items() if item.unknown}
    if not left.values:
        result.abstention = 'no_subject_evidence'
        return result

    corpus = {company_id: left.values, **{key: item.values for key, item in covered.items()}}
    result.corpus_ids = list(corpus)
    result.corpus_sha256 = sha256(json.dumps(corpus, sort_keys=True).encode()).hexdigest()
    idf = description_idf(list(corpus.values()))
    candidates = []
    for peer_id, item in peers.items():
        if not item.values:
            continue
        pair = score(left.values, item.values, idf)
        if not pair.fields:
            continue
        candidates.append(
            BacktestPeerScore(
                company_id=peer_id,
                display_name=inputs.entries[peer_id]['name'],
                entry=EventDate.model_validate(inputs.entries[peer_id]['date']),
                similarity=pair.similarity,
                coverage=pair.coverage,
                dimensions=pair.dimensions,
                field_scores=pair.fields,
                fields=[item.fields[field] for field in pair.fields],
                failed_bars=pair.failed_bars(len(left.values), len(item.values), REQUIRED_FIELDS),
                missing_on_peer=[
                    field for field in BACKTEST_FIELDS if field in left.values and field not in item.values
                ],
                missing_on_subject=[field for field in BACKTEST_FIELDS if field not in left.values],
            )
        )
    candidates.sort(key=lambda peer: (-peer.similarity, peer.company_id))
    qualifying = [peer for peer in candidates if not peer.failed_bars]
    result.qualifying_count = len(qualifying)
    selected_pool = qualifying[:TOP_K]
    result.ranked_ids = [peer.company_id for peer in selected_pool]

    if len(left.values) < REQUIRED_FIELDS:
        result.abstention = 'too_few_subject_fields'
    elif len(qualifying) < MIN_PEERS:
        result.abstention = 'too_few_peers'
    else:
        add_comps(result, inputs, selected_pool, cutoff, history)

    if result.abstention:
        explained = sorted(
            (peer for peer in candidates if peer.failed_bars),
            key=lambda peer: (-peer.coverage * peer.similarity, -peer.coverage, peer.company_id),
        )
        result.nearest_candidates = explained[:3]
        if preview:
            for peer in candidates[:3]:
                record = inputs.entries[peer.company_id]
                path, _ = inputs.history.peer(record, peer.entry, cutoff, history)
                result.nearest_available.append(BacktestNearest(**peer.model_dump(), history=path))
    if result.reveal:
        displayed = {peer.company_id for peer in [*result.nearest_available, *result.nearest_candidates, *result.comps]}
        result.reveal.evidence_reviews.extend(row for key in sorted(displayed) for row in peers[key].reviews)
    return result


def add_comps(
    result: BacktestResponse,
    inputs: BacktestInputs,
    pool: list[BacktestPeerScore],
    cutoff: str,
    history: PeerHistory,
) -> None:
    scores, histories, ranked = {}, {}, []
    for peer in pool:
        path, outcome = inputs.history.peer(inputs.entries[peer.company_id], peer.entry, cutoff, history)
        scores[peer.company_id], histories[peer.company_id] = peer, path
        row = WorkbenchRow(
            company_id=peer.company_id,
            display_name=peer.display_name,
            kind='company',
            sector=None,
            anchor=None,
            points=[],
            snapshot=[],
            claims=[],
            milestones=[],
            gaps=[],
            status=path.status,
            outcome_rank=outcome.rank if outcome else None,
            outcome_label=outcome.label if outcome else None,
            comp_outcome=outcome,
            not_alignable=None,
        )
        ranked.append(
            RankedPeer(row=row, similarity=peer.similarity, coverage=peer.coverage, dimensions=peer.dimensions)
        )
    comps, _, _ = select_comps(ranked)
    if not comps:
        result.abstention = 'no_outcomes'
    for comp in comps:
        company_id = comp.peer.row.company_id
        result.comps.append(
            BacktestComp(
                **scores[company_id].model_dump(),
                history=histories[company_id],
                role=comp.role,
            )
        )


def registered_subject(company_id: str) -> bool:
    return company_id in SUBJECTS
