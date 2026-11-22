"""Wire contracts for the retrospective Time Machine."""

from typing import Literal

from pydantic import Field

from .ingestion import StrictModel
from .precedent_contracts import DimensionScore
from .reference_pool import EventDate, Status

Track = Literal['preview', 'strict']
EvidenceMode = Literal['strict', 'lenient']
PeerHistory = Literal['as_of_anchor', 'today']


class BacktestSource(StrictModel):
    source_id: str
    publisher: str
    url: str
    locator: str
    available_on: str
    published_on: str | None = None
    witness_id: str | None = None
    witness_on: str | None = None


class BacktestField(StrictModel):
    name: str
    value: str | int
    raw_value: str | int
    rationale: str
    source: BacktestSource
    review_state: Literal['ai_adjudicated', 'confirmed', 'proposed']
    second_reading_matched: bool
    delay_days: int


class BacktestPeerScore(StrictModel):
    company_id: str
    display_name: str
    entry: EventDate
    similarity: float
    coverage: float
    dimensions: list[DimensionScore]
    field_scores: dict[str, float]
    fields: list[BacktestField]
    failed_bars: list[str]
    missing_on_peer: list[str]
    missing_on_subject: list[str]


class BacktestEvent(StrictModel):
    event_id: str
    kind: str
    date: EventDate
    source: BacktestSource
    lower_days: int
    upper_days: int
    review_state: Literal['dated_source', 'source_recorded']
    hindsight: bool = False


class BacktestHistory(StrictModel):
    events: list[BacktestEvent]
    follow_up_days: int
    status: Status


class BacktestNearest(BacktestPeerScore):
    not_a_comp: Literal[True] = True
    history: BacktestHistory


class BacktestComp(BacktestPeerScore):
    role: Literal['ceiling', 'typical', 'floor', 'representative']
    history: BacktestHistory


class BacktestReviewMetadata(StrictModel):
    company_id: str
    field: str
    reviewed_by: str
    reviewed_on: str


class BacktestReveal(StrictModel):
    status: Status
    through: str
    events: list[BacktestEvent]
    later_events: list[BacktestEvent]
    evidence_reviews: list[BacktestReviewMetadata]


class BacktestSubject(StrictModel):
    company_id: str
    display_name: str
    entry: EventDate
    cutoff: str
    fields: list[BacktestField]
    entry_round_source: BacktestSource | None = None


class BacktestExclusion(StrictModel):
    company_id: str
    reason: str


class BacktestThresholds(StrictModel):
    similarity: float
    coverage: float
    product_customer: float
    fields: int
    peers: int
    top_k: int


class BacktestResponse(StrictModel):
    track: Track
    witness_mode: EvidenceMode
    peer_history: PeerHistory
    hindsight: bool
    provisional: bool
    label: str | None = None
    strict_gate_passed: bool
    preview_peers: int | None = None
    required_peers: int
    similarity_version: str
    preregistration_commit: str
    input_sha256: dict[str, str]
    thresholds: BacktestThresholds
    subject: BacktestSubject
    eligible_peer_ids: list[str] = Field(default_factory=list)
    covered_peer_ids: list[str] = Field(default_factory=list)
    excluded: list[BacktestExclusion] = Field(default_factory=list)
    corpus_ids: list[str] = Field(default_factory=list)
    # This reference makes the exact description corpus inspectable without transmitting its text.
    corpus_sha256: str | None = None
    unknown_tokens: dict[str, dict[str, str | int]] = Field(default_factory=dict)
    ranked_ids: list[str] = Field(default_factory=list)
    qualifying_count: int = 0
    comps: list[BacktestComp] = Field(default_factory=list)
    nearest_candidates: list[BacktestPeerScore] = Field(default_factory=list)
    nearest_available: list[BacktestNearest] = Field(default_factory=list)
    abstention: (
        Literal['strict_gate', 'no_subject_evidence', 'too_few_subject_fields', 'too_few_peers', 'no_outcomes'] | None
    ) = None
    reveal: BacktestReveal | None = None
