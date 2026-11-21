"""Build stage-aligned views from the audited cohort and curated fixture."""

from collections import defaultdict
from contextlib import closing

from fastapi import HTTPException, Query, Response

from .cohort_audit import run_audit
from .database import connect
from .healthtech import compare_healthtech, load_selections
from .ingestion import day
from .precedent_contracts import (
    AnchorKind,
    ChecklistResponse,
    CompOutcome,
    PrecedentResponse,
    UnalignedPeer,
    WitnessMode,
    WorkbenchRow,
)
from .precedent_evidence import (
    POOL_ANCHORS,
    checklist,
    contemporaneous_snapshot,
    fixture_feature_claims,
    points_for,
    pool_claim,
    research_claims,
    select_anchor,
    snapshot_at,
    snapshot_by,
)
from .precedent_similarity import MILESTONES, THRESHOLDS, VERSION, nearest_candidates, rank_peers, select_comps
from .reference_pool import CLOSURES, OUTCOMES, EventDate, PoolEvent, PoolSource, Witness, plus_months
from .reference_pool_api import latest_fixture
from .research_repository import dossier, read_consistently
from .screening_note import ScreeningDraft, screening_draft
from .witnessed_snapshots import WitnessedSnapshots
from .workbench_reviews import claim_reviews

# Read-side links between existing case records and known fixture brands.
# Fixture claims retain their own source and stable ID. They do not amend entry
# decisions or create legal-entity mappings.
FIXTURE_TO_COHORT = {
    'formus': 'discovery_formuslabs',
    'halter': 'discovery_halter',
    'sharesies': 'discovery_sharesies',
    'cleanery': 'discovery_cleanery',
    'heartlab': 'discovery_heartlab',
    'vidapp': 'public_vidapp',
    'firstaml': 'public_firstaml',
    'safestack': 'public_safestack',
    'partly': 'public_partly',
    'supie': 'public_supie',
    'quashed': 'public_quashed',
    'carepatron': 'public_carepatron',
    'runn': 'public_runnio',
    'excellent': 'public_excellent',
    'immersve': 'public_immersve',
}
STAGE_RANK = {'series_a': 3, 'series_b': 4, 'series_c_plus': 4, 'acquired': 5, 'ipo': 5}
RANK_LABEL = {
    0: 'Verified closure first',
    1: 'Lost to follow-up',
    2: 'Observed without a qualifying outcome',
    3: 'Series A',
    4: 'Series B or later',
    5: 'Acquisition or IPO',
}
STATUS_RANK = {
    'closed_before_outcome': 0,
    'lost_to_follow_up': 1,
    'observed_no_outcome': 2,
    'reached_outcome': 3,
    'acquired_or_ipo_before_outcome': 5,
}
COMP_LABELS = {
    0: 'Verified closure',
    1: 'Lost or quiet',
    2: 'Operating on seed',
    3: 'Series A',
    4: 'Series B+',
    5: 'Exit or IPO',
}
ACTIVITY = {
    'last_verified_activity',
    'clinical_study',
    'provider_deployment',
    'first_paid_customer',
    'regulatory_clearance',
    'regulatory_decision',
}
EVENT_FEATURES = {
    'clinical_study': 'provider_study',
    'provider_deployment': 'provider_study',
    'first_paid_customer': 'paid_pilot',
    'regulatory_clearance': 'submission',
    'pre_seed': 'stage',
    'seed': 'stage',
    'series_a': 'stage',
    'series_b': 'stage',
    'series_c_plus': 'stage',
}
PLOT_FIELDS = set().union(*POOL_ANCHORS.values())


def witnesses_by_source(witnesses):
    groups = defaultdict(list)
    for witness in witnesses:
        groups[witness.source_id].append(witness)
    return groups


def event_claim(event, source, witnesses, as_of):
    return pool_claim(
        event.event_id,
        event.kind,
        event.claim,
        event.passage,
        source,
        witnesses,
        when=event.date,
        basis=event.date_basis,
        as_of=as_of,
    )


def cohort_source(source_id, raw):
    publication = EventDate.model_validate(raw['publication'])
    _, published_upper = publication.bounds()
    return PoolSource(
        source_id=source_id,
        title=raw['scope'],
        publisher=raw['publisher'],
        url=raw['url'],
        kind='dated_report',
        published_on=published_upper,
        retrieved_on=raw['retrieved_on'],
    )


def comp_outcome(entry_anchor, records, review, as_of):
    if not entry_anchor:
        return None
    dated = [
        (event, claim)
        for event, claim in records
        if event.entity_link == 'supported'
        and claim.review_state != 'disputed'
        and claim.lower_on
        and claim.upper_on
        and entry_anchor.claim.upper_on <= claim.lower_on <= claim.upper_on <= as_of
    ]

    def latest(candidates):
        return max(candidates, key=lambda claim: (claim.upper_on, claim.lower_on, claim.claim_id), default=None)

    def status(rank, claim, *, searched_on=None):
        return CompOutcome(
            rank=rank,
            label=COMP_LABELS[rank],
            claim=claim,
            date_value=searched_on or claim.date_value,
            date_precision='day' if searched_on else claim.date_precision,
        )

    closure = latest(claim for event, claim in dated if event.kind in CLOSURES)
    exit_event = latest(claim for event, claim in dated if event.kind in ('acquired', 'ipo'))
    if closure and exit_event:
        if closure.lower_on > exit_event.upper_on:
            return status(0, closure)
        if exit_event.lower_on > closure.upper_on:
            return status(5, exit_event)
        return None
    if closure:
        return status(0, closure)
    if exit_event:
        return status(5, exit_event)

    for rank in (4, 3):
        financing = latest(
            claim
            for event, claim in dated
            if event.kind in OUTCOMES and event.instrument == 'priced_equity' and STAGE_RANK[event.kind] == rank
        )
        if financing:
            return status(rank, financing)

    reviewed_id = review['activity_event_id'] if review and review['reviewed_on'] <= as_of else None
    activity = latest(claim for event, claim in dated if event.kind in ACTIVITY or event.event_id == reviewed_id)
    if activity:
        if (
            reviewed_id
            and any(event.event_id == reviewed_id for event, _ in dated)
            and plus_months(activity.upper_on, 18) <= review['searched_through']
        ):
            return status(1, activity, searched_on=review['searched_through'])
        return status(2, activity)
    return None


class SubjectNotFound(LookupError):
    pass


class PrecedentCatalog:
    def __init__(self, conn, as_of, audit=None):
        self.conn, self.as_of = conn, as_of
        _, selections = load_selections()
        self.projects = {item.subject_id for item in selections.selections}
        self.audit = audit if audit is not None else run_audit()
        self.reviews = claim_reviews(conn)
        self.witnessed = WitnessedSnapshots()
        self.entries = {
            row['company_id']: row['entry'] for row in self.audit['decisions'] if row['status'] == 'included'
        }
        self.digest, self.packet = latest_fixture(conn)
        self.fixture = {c.company_id: c for c in self.packet.companies} if self.packet else {}
        self.by_research = {c.research_subject_id: c.company_id for c in self.fixture.values() if c.research_subject_id}
        self.by_cohort = {
            company_id: fixture_id
            for fixture_id, company_id in FIXTURE_TO_COHORT.items()
            if fixture_id in self.fixture and company_id in self.entries
        }
        self.fixture_events = defaultdict(list)
        if self.packet:
            for event in self.packet.events:
                self.fixture_events[event.company_id].append(event)
        self.fixture_sources = {s.source_id: s for s in self.packet.sources} if self.packet else {}
        self.fixture_witnesses = witnesses_by_source(self.packet.witnesses if self.packet else [])
        self.follow_up = self.audit['follow_up']
        self.follow_sources = {sid: PoolSource.model_validate(raw) for sid, raw in self.follow_up['sources'].items()}
        self.follow_witnesses = witnesses_by_source(
            Witness.model_validate(raw) for raw in self.follow_up['witnesses'].values()
        )

    def apply_reviews(self, claims):
        return [
            claim.model_copy(update={'review_state': 'disputed', 'review_events': self.reviews[claim.claim_id]})
            if claim.claim_id in self.reviews
            else claim
            for claim in claims
        ]

    def identity(self, key):
        fixture_id = self.by_research.get(key, self.by_cohort.get(key, key))
        fixture = self.fixture.get(fixture_id)
        cohort_id = FIXTURE_TO_COHORT.get(fixture_id, key)
        cohort = self.entries.get(cohort_id)
        if key in self.entries:
            cohort = self.entries[key]
        linked = {key}
        if fixture:
            linked.update(filter(None, (fixture.company_id, fixture.venture_id, fixture.research_subject_id)))
        if cohort:
            linked.add(cohort['company_id'])
        return fixture, cohort, linked

    def row(self, key, kind, *, as_subject=False, witness_mode='strict'):
        fixture, entry, _ = self.identity(key)
        graph_id = fixture.research_subject_id if fixture else key if not entry else None
        graph = dossier(self.conn, graph_id) if graph_id else None
        if not (fixture or entry or graph):
            raise SubjectNotFound('Workbench subject not found')
        graph_subject = graph['subject'] if graph else None
        name = entry['name'] if entry else fixture.display_name if fixture else graph_subject['display_name']
        sector = entry['sector'] if entry else fixture.sector if fixture else None
        is_project = key in self.projects
        claims = research_claims(graph, graph_id, self.as_of)
        events = [claim for claim in claims if claim.field in PLOT_FIELDS]
        records = []
        features = []
        if fixture:
            for event in self.fixture_events[fixture.company_id]:
                if claim := event_claim(
                    event, self.fixture_sources[event.source_id], self.fixture_witnesses[event.source_id], self.as_of
                ):
                    claims.append(claim)
                    if event.entity_link == 'supported':
                        events.append(claim)
                        records.append((event, claim))
            features = fixture_feature_claims(self.conn, self.digest, self.packet, fixture.company_id, self.as_of)
            claims.extend(features)
        entry_id = fixture.entry_event_id if fixture else None
        audit_events = {}
        if entry:
            staged = 'pre_seed' if entry['label'].lower().startswith('pre') else 'seed'
            entry_id = 'cohort_entry:' + entry['company_id']
            source_id = entry['source_id']
            source = cohort_source(source_id, self.audit['sources'][source_id])
            if claim := pool_claim(
                entry_id,
                staged,
                entry['passage'],
                entry['locator'],
                source,
                [],
                when=EventDate.model_validate(entry['date']),
                basis=entry['date_basis'],
                as_of=self.as_of,
            ):
                events.append(claim)
                claims.append(claim)
            for raw in self.follow_up['decisions'][entry['company_id']]['events']:
                event = PoolEvent.model_validate(raw)
                source = self.follow_sources.get(event.source_id)
                if source is None:
                    source = cohort_source(event.source_id, self.audit['sources'][event.source_id])
                if claim := event_claim(event, source, self.follow_witnesses[event.source_id], self.as_of):
                    claims.append(claim)
                    if event.entity_link == 'supported':
                        events.append(claim)
                        records.append((event, claim))
                        audit_events[event.event_id] = event
        # Research observations with the same source and dated occurrence can
        # repeat an imported fixture event. Retain both claims in Evidence.
        unique_events = {}
        for claim in events:
            fingerprint = (claim.field, claim.lower_on, claim.upper_on, claim.url)
            if fingerprint not in unique_events or claim.claim_id == entry_id:
                unique_events[fingerprint] = claim
        events = self.apply_reviews(unique_events.values())
        prior_entry = select_anchor('first_institutional_round', events, entry_id, self.as_of) if entry_id else None
        profile_id = entry['company_id'] if entry else fixture.company_id if fixture else key
        witnessed = self.witnessed.claims(
            profile_id,
            self.as_of,
            entry_anchor=prior_entry,
            scope='project_as_of' if is_project else 'institutional_entry',
        )
        contemporaneous = self.witnessed.claims(
            profile_id, self.as_of, entry_anchor=prior_entry, scope='institutional_entry_contemporaneous'
        )
        reference_context = (
            self.witnessed.claims(fixture.company_id, self.as_of, scope='reference_round_context') if fixture else []
        )
        features.extend(witnessed)
        claims = self.apply_reviews([*claims, *witnessed, *contemporaneous, *reference_context])
        features = self.apply_reviews(features)
        anchor = select_anchor(kind, events, entry_id, self.as_of)
        features.extend(
            claim.model_copy(
                update={
                    'field': EVENT_FEATURES[claim.field],
                    'value': claim.field if EVENT_FEATURES[claim.field] == 'stage' else 'yes',
                }
            )
            for claim in events
            if claim.field in EVENT_FEATURES
        )
        analogy = is_project and as_subject
        comparable = snapshot_by(self.as_of, features) if analogy else snapshot_at(anchor, features)
        if not as_subject and witness_mode == 'contemporaneous':
            comparable = contemporaneous_snapshot(anchor, comparable, self.apply_reviews(contemporaneous), self.as_of)
        status, rank = self.comparison_outcome(
            entry, anchor, {key: value for key, value in audit_events.items() if key not in self.reviews}
        )
        gaps = []
        if not anchor:
            gaps.append('No supported dated anchor in the public record at this cutoff.')
        if not comparable:
            gaps.append(
                'The subject profile needs a source availability witness by the as-of date.'
                if analogy
                else 'Same-stage evidence needs a source availability witness on or before the earliest anchor date.'
            )
        decision = self.follow_up['decisions'].get(entry['company_id']) if entry else None
        undisputed = [(event, claim) for event, claim in records if claim.claim_id not in self.reviews]
        latest_outcome = comp_outcome(prior_entry, undisputed, decision['review'] if decision else None, self.as_of)
        return WorkbenchRow(
            company_id=key,
            display_name=name,
            kind='research_project' if is_project else 'company',
            sector=sector,
            anchor=anchor,
            points=points_for(anchor, events, self.as_of),
            snapshot=comparable,
            claims=claims,
            milestones=checklist(comparable),
            gaps=gaps,
            status=status,
            outcome_rank=rank,
            outcome_label=RANK_LABEL.get(rank),
            comp_outcome=latest_outcome,
            not_alignable=gaps[0] if not anchor else None,
        )

    def comparison_outcome(self, entry, anchor, events):
        if not (entry and anchor and self.follow_up['as_of'] <= self.as_of):
            return 'unknown', None
        decision = self.follow_up['decisions'][entry['company_id']]
        start = anchor.claim.upper_on
        horizon = plus_months(anchor.claim.lower_on, 36)
        ladder = [
            STAGE_RANK[event.kind]
            for event in events.values()
            if event.kind in STAGE_RANK
            and event.date.bounds()[0]
            and start < event.date.bounds()[0]
            and event.date.bounds()[1] <= horizon
            and (event.kind not in OUTCOMES or event.instrument == 'priced_equity')
        ]
        if anchor.kind != 'first_institutional_round':
            # Only positive dated results can establish a rank on the
            # alternate clock. Seed-entry censoring cannot establish absence.
            outcome_ranks = [rank for rank in ladder if rank < 5]
            if outcome_ranks:
                return 'reached_outcome', max(ladder)
            if ladder and decision['status'] == 'acquired_or_ipo_before_outcome':
                return 'acquired_or_ipo_before_outcome', max(ladder)
            terminal = events.get(decision['outcome_event_id'])
            if decision['status'] == 'closed_before_outcome' and terminal:
                lower, upper = terminal.date.bounds()
                _, latest_seed = EventDate.model_validate(entry['date']).bounds()
                if latest_seed <= anchor.claim.lower_on and start < lower <= upper <= horizon:
                    return 'closed_before_outcome', 0
            return 'unknown', None
        status = decision['status']
        if decision['outcome_event_id'] and decision['outcome_event_id'] not in events:
            return 'unknown', None
        rank = STATUS_RANK.get(status)
        if status == 'reached_outcome' and ladder:
            rank = max(rank, *ladder)
        return status, rank

    def curated(self, subject_id, kind, witness_mode='strict'):
        if subject_id not in self.by_research and not subject_id.startswith('subj_'):
            return []
        result = compare_healthtech(self.conn, subject_id, as_of=self.as_of)
        return [
            self.row(self.by_research[peer['subject_id']], kind, witness_mode=witness_mode)
            for peer in result['peers']
            if peer['subject_id'] in self.by_research
        ]


@read_consistently
def response(conn, subject_id, kind, as_of, witness_mode='strict'):
    catalog = PrecedentCatalog(conn, as_of)
    subject = catalog.row(subject_id, kind, as_subject=True)
    _, _, identity = catalog.identity(subject_id)
    rows = [
        catalog.row(company_id, kind, witness_mode=witness_mode)
        for company_id in catalog.entries
        if not identity.intersection(catalog.identity(company_id)[2])
    ]
    aligned = [row for row in rows if row.anchor]
    peers = rank_peers(subject, aligned)
    comps, no_closure, abstention = select_comps(peers)
    nearest = nearest_candidates(subject, aligned) if not comps else []
    curated = catalog.curated(subject_id, kind, witness_mode)
    missing = {row.company_id: row for row in [*rows, *curated] if row.not_alignable}
    return PrecedentResponse(
        subject=subject,
        as_of=as_of,
        anchor_kind=kind,
        similarity_version=VERSION,
        witness_mode=witness_mode,
        late_witness_peers=[row for row in aligned if any(claim.peer_witness_delay_days for claim in row.snapshot)],
        peer_count_evaluated=len(aligned),
        peers=peers,
        curated=curated,
        comps=comps,
        not_alignable=[
            UnalignedPeer(company_id=row.company_id, display_name=row.display_name, reason=row.not_alignable)
            for row in missing.values()
        ],
        no_verified_closure=no_closure,
        abstention=abstention,
        questions=[MILESTONES[item.milestone] for item in subject.milestones if item.value != 'yes'],
        thresholds=THRESHOLDS,
        nearest_candidates=nearest,
    )


def install(app, db):
    def compute(subject_id, anchor, as_of, handler, *args):
        try:
            cutoff = day(as_of)
            with closing(connect(db)) as conn:
                return handler(conn, subject_id, anchor, cutoff, *args)
        except SubjectNotFound as error:
            raise HTTPException(404, str(error)) from error
        except ValueError as error:
            raise HTTPException(422, str(error)) from error

    @app.get('/api/precedents/{subject_id}', response_model=PrecedentResponse)
    def precedents(
        subject_id: str,
        anchor: AnchorKind = 'first_institutional_round',
        witness_mode: WitnessMode = 'strict',
        as_of: str = Query(..., pattern=r'^\d{4}-\d{2}-\d{2}$'),
    ):
        return compute(subject_id, anchor, as_of, response, witness_mode)

    @app.get('/api/precedents/{subject_id}/checklist', response_model=ChecklistResponse)
    def milestone_checklist(
        subject_id: str,
        anchor: AnchorKind = 'first_institutional_round',
        as_of: str = Query(..., pattern=r'^\d{4}-\d{2}-\d{2}$'),
    ):
        @read_consistently
        def read(conn, key, kind, cutoff):
            catalog = PrecedentCatalog(conn, cutoff)
            return ChecklistResponse(
                subject=catalog.row(key, kind, as_subject=True),
                as_of=cutoff,
                anchor_kind=kind,
                similarity_version=VERSION,
            )

        return compute(subject_id, anchor, as_of, read)

    @app.get('/api/precedents/{subject_id}/screening-note', response_model=ScreeningDraft)
    def export_screening_note(
        subject_id: str,
        response_headers: Response,
        anchor: AnchorKind = 'first_institutional_round',
        witness_mode: WitnessMode = 'strict',
        as_of: str = Query(..., pattern=r'^\d{4}-\d{2}-\d{2}$'),
    ):
        data = compute(subject_id, anchor, as_of, response, witness_mode)
        response_headers.headers['Content-Disposition'] = 'attachment; filename="venture-frame-screening-note.json"'
        return screening_draft(data)
