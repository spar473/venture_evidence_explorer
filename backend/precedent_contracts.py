"""Typed workbench projections. Claim IDs remain stable across views."""
from typing import Literal

from pydantic import Field

from .ingestion import StrictModel
from .reference_pool import Status, Witness
from .workbench_reviews import ClaimReview

AnchorKind = Literal['first_institutional_round', 'first_provider_or_clinical_study',
                     'first_regulatory_decision', 'first_paid_customer']
WitnessMode = Literal['strict', 'contemporaneous']


class WorkbenchClaim(StrictModel):
    claim_id: str
    field: str
    value: str | int
    passage: str
    publisher: str
    url: str
    published_on: str | None
    retrieved_on: str
    witness: Witness | None = None
    date_value: str | None = None
    date_precision: str | None = None
    lower_on: str | None = None
    upper_on: str | None = None
    date_basis: str | None = None
    peer_witness_delay_days: int | None = None
    review_state: str = 'source_attributed'
    review_events: list[ClaimReview] = Field(default_factory=list)


class WorkbenchAnchor(StrictModel):
    kind: AnchorKind
    claim: WorkbenchClaim


class WorkbenchPoint(StrictModel):
    claim: WorkbenchClaim
    lower_days: int
    upper_days: int
    is_anchor: bool


class MilestoneValue(StrictModel):
    milestone: str
    value: Literal['yes', 'no', 'unknown']
    claim_ids: list[str]


class CompOutcome(StrictModel):
    rank: Literal[0, 1, 2, 3, 4, 5]
    label: str
    date_value: str
    date_precision: str
    claim: WorkbenchClaim


class WorkbenchRow(StrictModel):
    company_id: str
    display_name: str
    kind: Literal['company', 'research_project']
    sector: str | None
    anchor: WorkbenchAnchor | None
    points: list[WorkbenchPoint]
    snapshot: list[WorkbenchClaim]
    claims: list[WorkbenchClaim]
    milestones: list[MilestoneValue]
    gaps: list[str]
    status: Status
    outcome_rank: int | None
    outcome_label: str | None
    comp_outcome: CompOutcome | None = None
    not_alignable: str | None


class DimensionScore(StrictModel):
    dimension: str
    similarity: float | None
    coverage: float
    matched_fields: list[str]
    different_fields: list[str]


class RankedPeer(StrictModel):
    row: WorkbenchRow
    similarity: float
    coverage: float
    dimensions: list[DimensionScore]


class SelectedComp(StrictModel):
    role: Literal['ceiling', 'typical', 'floor', 'representative']
    peer: RankedPeer
    reason: str


class UnalignedPeer(StrictModel):
    company_id: str
    display_name: str
    reason: str


class PrecedentResponse(StrictModel):
    subject: WorkbenchRow
    as_of: str
    anchor_kind: AnchorKind
    similarity_version: str
    witness_mode: WitnessMode = 'strict'
    peer_count_evaluated: int
    peers: list[RankedPeer]
    curated: list[WorkbenchRow]
    late_witness_peers: list[WorkbenchRow] = Field(default_factory=list)
    comps: list[SelectedComp]
    not_alignable: list[UnalignedPeer]
    no_verified_closure: bool
    abstention: str | None
    questions: list[str]


class ChecklistResponse(StrictModel):
    subject: WorkbenchRow
    as_of: str
    anchor_kind: AnchorKind
    similarity_version: str
