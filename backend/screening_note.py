"""Venture Frame JSON with unweighted evidence-based screening measurements."""
from hashlib import sha256
from typing import Literal

from .healthtech_scenarios import venture_frame_measurement_draft
from .ingestion import StrictModel
from .precedent_contracts import AnchorKind, DimensionScore, MilestoneValue, PrecedentResponse, WorkbenchAnchor


class ScreeningMetadata(StrictModel):
    format_version: Literal['vee-screening-note:1'] = 'vee-screening-note:1'
    role: Literal['subject', 'ceiling', 'typical', 'floor']
    company_id: str
    anchor_kind: AnchorKind
    anchor_event: WorkbenchAnchor | None
    as_of: str
    similarity_version: str
    similarity: float | None = None
    coverage: float | None = None
    dimensions: list[DimensionScore]
    milestones: list[MilestoneValue]
    outcome_label: str | None
    explanation: str | None


class ScreeningAlternative(StrictModel):
    id: str
    name: str
    metadata: ScreeningMetadata


class ScreeningScale(StrictModel):
    type: Literal['interval']
    unit: str
    lower: float
    upper: float


class ScreeningCriterion(StrictModel):
    id: str
    name: str
    order: int
    scale: ScreeningScale


class ScreeningMeasurement(StrictModel):
    alternative_id: str
    criterion_id: str
    value: float


class ScreeningDraft(StrictModel):
    schema_version: Literal[1]
    id: str
    title: str
    description: str
    decision_maker: str
    alternatives: list[ScreeningAlternative]
    criteria: list[ScreeningCriterion]
    performances: list[ScreeningMeasurement]
    weight_profiles: list
    scenarios: list


def screening_draft(data: PrecedentResponse):
    key = f'{data.subject.company_id}|{data.anchor_kind}|{data.as_of}'
    project_id = 'vee-screening-' + sha256(key.encode()).hexdigest()[:16]

    def alternative(role, row, peer=None, explanation=None):
        return ScreeningAlternative(id=f'screening-{role}', name=row.display_name,
            metadata=ScreeningMetadata(role=role, company_id=row.company_id, anchor_kind=data.anchor_kind,
                anchor_event=row.anchor, as_of=data.as_of, similarity_version=data.similarity_version,
                similarity=peer.similarity if peer else None, coverage=peer.coverage if peer else None,
                dimensions=peer.dimensions if peer else [], milestones=row.milestones,
                outcome_label=row.outcome_label, explanation=explanation))

    alternatives = [alternative('subject', data.subject, explanation=data.abstention)]
    alternatives.extend(alternative(comp.role, comp.peer.row, comp.peer, comp.reason) for comp in data.comps)
    criteria_names = dict.fromkeys(score.dimension for item in alternatives for score in item.metadata.dimensions
                                   if score.similarity is not None)
    criteria = [ScreeningCriterion(id=f'similarity-{i+1}', name=f'{name} similarity', order=i,
                scale=ScreeningScale(type='interval', unit='similarity', lower=0., upper=1.))
                for i, name in enumerate(criteria_names)]
    criterion_map = dict(zip(criteria_names, (criterion.id for criterion in criteria), strict=True))
    measurements = [ScreeningMeasurement(alternative_id=item.id, criterion_id=criterion_map[score.dimension],
                    value=score.similarity) for item in alternatives for score in item.metadata.dimensions
                    if score.similarity is not None]
    project = venture_frame_measurement_draft(project_id, f'{data.subject.display_name} screening note',
        'Unweighted screening evidence and raw historical peer similarities for analyst review.',
        alternatives, criteria, measurements)
    return ScreeningDraft.model_validate(project)
