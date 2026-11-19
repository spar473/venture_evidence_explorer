"""A curated view of imported question-readiness evidence, separate from B0.

This selects explicit research comparisons, never scores, trains or promotes
records. Research 0.2.1 cannot encode historical availability witnesses, so a
historical request always abstains. A future contract must supply and validate
those witnesses before enabling backtests.
"""
import hashlib
from datetime import date
from typing import Literal

from pydantic import Field, model_validator
from .database import ROOT
from .ingestion import day
from .research_adapter import research_time_interval
from .research_contracts import (ResearchContract, ResearchObservation, ResearchSource,
    ResearchReadiness, ResearchUnknown, ResearchCase, ResearchTime)
from .research_repository import dossier, read_consistently
from .research_validation import decode_packet

SELECTION_PATH = ROOT / 'research/healthtech-pilot/comparisons.json'
POLICY = 'healthtech-curated-pathways-1.1'


class PeerSelection(ResearchContract):
    subject_id: str
    readiness_id: str
    reference_document_date: str
    reference_observation_ids: list[str] = Field(min_length=1)
    later_observation_ids: list[str]
    follow_up_readiness_ids: list[str] = Field(default_factory=list)

    @model_validator(mode='after')
    def dates_and_ids(self):
        day(self.reference_document_date)
        ids = self.reference_observation_ids + self.later_observation_ids
        if len(ids) != len(set(ids)):
            raise ValueError('Comparison evidence IDs must be unique')
        if self.readiness_id in self.follow_up_readiness_ids or len(set(self.follow_up_readiness_ids)) != len(self.follow_up_readiness_ids):
            raise ValueError('Follow-up assessment IDs must be unique')
        return self


class Selection(ResearchContract):
    subject_id: str
    peers: list[PeerSelection] = Field(max_length=3)
    gap_readiness_ids: list[str] = Field(default_factory=list)

    @model_validator(mode='after')
    def no_self_or_duplicates(self):
        ids = [p.subject_id for p in self.peers]
        if self.subject_id in ids or len(ids) != len(set(ids)):
            raise ValueError('Self and duplicate peers are forbidden')
        return self


class Selections(ResearchContract):
    format_version: Literal['healthtech-comparisons:1']
    prepared_on: str
    selections: list[Selection]

    @model_validator(mode='after')
    def unique_subjects(self):
        day(self.prepared_on)
        ids = [s.subject_id for s in self.selections]
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate comparison subject')
        return self


class ComparisonEvidence(ResearchContract):
    observation: ResearchObservation
    source: ResearchSource


class FollowUpEvidence(ResearchContract):
    readiness: ResearchReadiness
    evidence: list[ComparisonEvidence]


class ElapsedEvidence(ResearchContract):
    date_type: Literal['document_context', 'reported_occurrence', 'prospective_target']
    time: ResearchTime
    lower_days: int | None
    upper_days: int | None
    observation_id: str


class PathwayPeer(ResearchContract):
    subject_id: str
    display_name: str
    classification: Literal['pathway_precedent']
    early_stage_anchor: None = None
    reference_document_date: str
    readiness: ResearchReadiness
    reference_evidence: list[ComparisonEvidence]
    later_evidence: list[ComparisonEvidence]
    follow_up: list[FollowUpEvidence]
    elapsed_evidence: list[ElapsedEvidence]
    unknowns: list[ResearchUnknown]
    unresolved_cases: list[ResearchCase]


class HealthtechComparison(ResearchContract):
    subject_id: str
    question: str
    view: Literal['research', 'historical']
    as_of: str
    policy_version: str
    selection_sha256: str
    graph_sha256: str
    source_packet_sha256s: list[str]
    same_stage_assessment: Literal['abstain']
    status: Literal['pathway_precedents', 'abstain']
    explanation: str
    subject_evidence: list[ComparisonEvidence]
    peers: list[PathwayPeer]
    gaps: list[str]
    limitations: list[str]


class ReferenceVenture(ResearchContract):
    subject_id: str
    display_name: str


class ProjectCoverage(ResearchContract):
    subject_id: str
    peers: list[ReferenceVenture]


class HealthtechCoverage(ResearchContract):
    as_of: str
    project_count: int
    projects_with_peers: int
    distinct_reference_count: int
    pair_count: int
    projects: list[ProjectCoverage]


def time_proves_by(value, cutoff):
    """Use the latest possible day. Unknown and overlapping partial dates fail."""
    interval = research_time_interval(value)
    return interval['upper_bound'] is not None and interval['upper_bound'] <= cutoff


def evidence_eligible(observation, source, cutoff, view):
    if view == 'historical':
        # The authoritative 0.2.1 schema fixes historical_availability_verified
        # to false and has no locator/day witness. Never treat publication,
        # document context, or a current retrieval as a substitute.
        return False
    if source['access_status'] != 'text_read' or source['retrieved_on'] > cutoff:
        return False
    if observation['review']['state'] not in ('source_checked', 'accepted') or observation['review']['checked_on'] > cutoff:
        return False
    for value in (source['published_time'], source['updated_time'], observation['context_time'], observation['effective_time']):
        if value['precision'] != 'unknown' and not time_proves_by(value, cutoff):
            return False
    return True


def elapsed_evidence(evidence, reference_document_date):
    """Align reported dates to a reference document, keeping their original roles."""
    origin = date.fromisoformat(reference_document_date)
    rows = []
    for item in evidence:
        observation = item['observation']
        dates = [('document_context', observation['context_time'])]
        if observation['assertion_nature'] == 'reported_occurrence':
            dates.append(('reported_occurrence', observation['effective_time']))
        if observation['target_time']['precision'] != 'unknown':
            dates.append(('prospective_target', observation['target_time']))
        for date_type, time in dates:
            interval = research_time_interval(time)
            lower, upper = interval['lower_bound'], interval['upper_bound']
            rows.append(dict(date_type=date_type, time=time, observation_id=observation['observation_id'],
                lower_days=(date.fromisoformat(lower)-origin).days if lower is not None else None,
                upper_days=(date.fromisoformat(upper)-origin).days if upper is not None else None))
    rows.sort(key=lambda row: (row['lower_days'] is None, row['lower_days'] or 0))
    return rows


@read_consistently
def compare_healthtech(conn, subject_id, *, as_of, view='research', packet_sha256=None):
    day(as_of)
    if view not in ('research', 'historical'):
        raise ValueError('Unknown comparison view')
    raw, selections = load_selections()
    graph = dossier(conn, subject_id, packet_sha256)
    if graph is None:
        raise LookupError('Research subject not found')
    return compare_graph(graph, selections, raw, as_of, view)


def load_selections():
    raw = SELECTION_PATH.read_bytes()
    return raw, Selections.model_validate(decode_packet(raw))


@read_consistently
def healthtech_coverage(conn):
    """Count the pairs a reader can open at the pilot research cutoff."""
    raw, selections = load_selections()
    projects = []
    reference_ids = set()
    for choice in selections.selections:
        graph = dossier(conn, choice.subject_id)
        if graph is None:
            continue
        comparison = compare_graph(graph, selections, raw, selections.prepared_on, 'research')
        peers = [ReferenceVenture(subject_id=p['subject_id'], display_name=p['display_name'])
                 for p in comparison['peers']]
        projects.append(ProjectCoverage(subject_id=choice.subject_id, peers=peers))
        reference_ids.update(p.subject_id for p in peers)
    return HealthtechCoverage(as_of=selections.prepared_on, projects=projects,
        project_count=len(projects), projects_with_peers=sum(bool(p.peers) for p in projects),
        distinct_reference_count=len(reference_ids), pair_count=sum(len(p.peers) for p in projects))


def compare_graph(graph, selections, raw, as_of, view):
    subject_id = graph['subject']['subject_id']
    packet = graph['packet']
    sources = {s['source_id']: s for s in packet['sources']}
    observations = {o['observation_id']: o for o in packet['observations']}
    readiness = {r['readiness_id']: r for r in packet['readiness']}
    subjects = {s['subject_id']: s for s in packet['subjects']}
    choice = next((s for s in selections.selections if s.subject_id == subject_id), None)

    def review_allows(record_id, review):
        if review['checked_on'] > as_of or review['state'] not in ('source_checked', 'accepted'):
            return False
        decisions = [r for r in packet['review_events'] if r['target_id'] == record_id and r['reviewed_on'] <= as_of]
        if not decisions:
            return True
        latest = max(r['reviewed_on'] for r in decisions)
        # Day-only review dates cannot establish ordering within one day.
        # A disagreement on the latest day withholds the record.
        return all(r['decision'] == 'accepted' for r in decisions if r['reviewed_on'] == latest)

    def eligible(oid):
        o = observations.get(oid)
        return (o is not None and o['source_id'] in sources and review_allows(oid, o['review'])
            and evidence_eligible(o, sources[o['source_id']], as_of, view))

    def evidence(ids):
        return [dict(observation=observations[oid], source=sources[observations[oid]['source_id']]) for oid in ids if eligible(oid)]

    def assessment_is_eligible(assessment, peer_id):
        return (assessment is not None
            and set(assessment['subject_ids']) == {subject_id, peer_id}
            and assessment['evidence_cutoff'] <= as_of
            and review_allows(assessment['readiness_id'], assessment['review'])
            and assessment['assessment'] == 'limited_conclusions_supported'
            and all(review_allows(c['conclusion_id'], c['review']) for c in assessment['supported_conclusions'])
            and all(eligible(oid) for oid in assessment['supporting_observation_ids']))

    gaps = []
    peers = []
    if view == 'historical':
        gaps.append('No historical availability witness is representable in research 0.2.1. Publication and document dates cannot establish what was available at this cutoff.')
    elif choice is not None and selections.prepared_on > as_of:
        gaps.append('The comparison assessment was prepared after this research cutoff.')
    elif not review_allows(subject_id, graph['subject']['review']):
        gaps.append('The selected research subject is not eligible under its recorded review state at this cutoff.')
    elif choice is None:
        gaps.append('No source-supported curated comparison has been assembled for this subject. Shared healthcare wording alone is insufficient.')
    else:
        for rid in choice.gap_readiness_ids:
            r = readiness.get(rid)
            if (r and r['subject_ids'] == [subject_id] and r['evidence_cutoff'] <= as_of
                and review_allows(rid, r['review'])
                and all(eligible(oid) for oid in r['supporting_observation_ids'])):
                gaps.append(r['rationale'])
        for peer in choice.peers:
            # Defensive even if a malformed future manifest bypasses validation.
            if peer.subject_id == subject_id:
                continue
            r = readiness.get(peer.readiness_id)
            peer_subject = subjects.get(peer.subject_id)
            if peer_subject and peer_subject['proposed_application_id'] == graph['subject']['proposed_application_id']:
                gaps.append('A possible shared brand/project identity is withheld to avoid a self-comparison; the identity mapping remains unresolved.')
                continue
            ids = peer.reference_observation_ids + peer.later_observation_ids
            if (peer_subject is None
                or not review_allows(peer.subject_id, peer_subject['review'])
                or not assessment_is_eligible(r, peer.subject_id)
                or not all(eligible(oid) and observations[oid]['subject_id'] == peer.subject_id for oid in ids)):
                gaps.append('A selected comparison lacks eligible, subject-correct evidence or an assessment at this cutoff; it is withheld.')
                continue
            if not all(time_proves_by(observations[oid]['context_time'], peer.reference_document_date) for oid in peer.reference_observation_ids):
                gaps.append('Reference-document timing is unresolved; the selected comparison is withheld.')
                continue
            later_evidence = evidence(peer.later_observation_ids)
            reference_evidence = evidence(peer.reference_observation_ids)
            follow_up = []
            for rid in peer.follow_up_readiness_ids:
                assessment = readiness.get(rid)
                if assessment_is_eligible(assessment, peer.subject_id):
                    follow_up.append(dict(readiness=assessment, evidence=evidence(assessment['supporting_observation_ids'])))
            timeline_items = {item['observation']['observation_id']: item
                for item in reference_evidence + later_evidence + [item for group in follow_up for item in group['evidence']]
                if item['observation']['subject_id'] == peer.subject_id}
            peers.append(dict(subject_id=peer.subject_id, display_name=subjects[peer.subject_id]['display_name'],
                classification='pathway_precedent', early_stage_anchor=None,
                reference_document_date=peer.reference_document_date, readiness=r,
                reference_evidence=reference_evidence, later_evidence=later_evidence, follow_up=follow_up,
                elapsed_evidence=elapsed_evidence(timeline_items.values(), peer.reference_document_date),
                unknowns=[u for u in packet['unknowns'] if u['subject_id'] in (subject_id, peer.subject_id) and u['as_of'] <= as_of and u['review']['checked_on'] <= as_of],
                unresolved_cases=[c for c in packet['reconciliation_cases'] if peer.subject_id in c['subject_ids'] and all(eligible(oid) for oid in c['observation_ids'])]))
    return dict(subject_id=subject_id,
        question='What did comparable Kiwi healthtech ventures have to demonstrate before a healthcare provider would evaluate or adopt their product?',
        view=view, as_of=as_of, policy_version=POLICY,
        selection_sha256=hashlib.sha256(raw).hexdigest(), graph_sha256=graph['graph_sha256'],
        source_packet_sha256s=graph['source_packet_sha256s'], same_stage_assessment='abstain',
        status='pathway_precedents' if peers else 'abstain',
        explanation='No verified same-stage peer or provider admission threshold is established. The supported slice contains scoped pathway precedents.' if peers else 'Insufficient eligible evidence for a supported comparison at this cutoff. Abstaining.',
        subject_evidence=evidence([oid for oid,o in observations.items() if o['subject_id'] == subject_id]),
        peers=peers[:3], gaps=list(dict.fromkeys(gaps)),
        limitations=['Curated analyst selection from imported question-readiness records; no similarity score or independent relevance judgment.',
            'Reference-document evidence is read today, not a verified historical snapshot. Early-stage anchors remain unset.',
            'Later reports are separate context; financing, grants, intentions, evaluations and paid deployment are not interchangeable.',
            'These cases cannot estimate success probabilities or establish causal prerequisites for adoption.'])
