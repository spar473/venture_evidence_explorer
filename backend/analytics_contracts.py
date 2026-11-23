"""Wire contracts for the four analytics views."""

from typing import Literal

from pydantic import BaseModel

from .backtest_contracts import BacktestEvent, BacktestField, BacktestReviewMetadata, BacktestSource, BacktestThresholds
from .precedent_contracts import DimensionScore
from .precedent_similarity_general import FieldValue
from .reference_pool import Status
from .workbench_gates import WorkbenchGates


class Provisional(BaseModel):
    provisional: Literal[True]
    label: str


class AnalyticsCompany(BaseModel):
    company_id: str
    name: str
    sector: str
    sector_group: str
    entry: BacktestEvent
    start: str
    end: str
    year: int
    horizon: str


class HeatmapFact(BaseModel):
    name: str
    value: FieldValue
    review_state: Literal['proposed', 'confirmed', 'rejected', 'disputed', 'ai_adjudicated']
    second_reading_matched: bool
    reviewed_by: str | None
    reviewed_on: str | None
    source: BacktestSource


class AnalyticsHistory(BaseModel):
    events: list[BacktestEvent]
    fields: dict[str, HeatmapFact]
    status: Status
    outcome_event_id: str | None
    status_clock: list[tuple[str, Status, str | None]]


class AnalyticsCohort(Provisional):
    audit_date: str
    candidate_records: int
    fields: list[str]
    subjects: list[str]
    companies: list[AnalyticsCompany]
    reveal: dict[str, AnalyticsHistory]
    gates: WorkbenchGates
    preview_peers: int
    strict_gate_passed: bool
    input_sha256: dict[str, str]


class AnalyticsPeer(BaseModel):
    company_id: str
    similarity: float | None
    coverage: float
    product_customer: float | None
    shared_fields: int
    field_scores: dict[str, float]
    dimensions: list[DimensionScore]
    qualifies: bool
    failed_bars: list[str]


class ChangedRole(BaseModel):
    recorded: list[str]
    scenario: list[str]


class AnalyticsScenario(Provisional):
    company_id: str
    cutoff: str
    scenario: bool
    similarity_version: str
    thresholds: BacktestThresholds
    overrides: dict[str, FieldValue]
    qualifying_count: int
    peers: list[AnalyticsPeer]
    roles: dict[str, list[str]]
    changed_roles: dict[str, ChangedRole]


class PresetScenario(BaseModel):
    id: str
    name: str
    result: AnalyticsScenario


class ScorerDimension(BaseModel):
    name: str
    weight: float
    fields: list[str]


class ScorerVocabulary(BaseModel):
    nodes: dict[str, str | None]
    flat: bool
    aliases: dict[str, str]


class ScorerPeer(BaseModel):
    values: dict[str, FieldValue]
    rank: int | None


class ScorerInput(BaseModel):
    dimensions: list[ScorerDimension]
    vocabulary: dict[str, ScorerVocabulary]
    bands: list[str]
    stop: list[str]
    inflections: dict[str, str]
    options: dict[str, list[str]]
    subject: dict[str, FieldValue]
    peers: dict[str, ScorerPeer]


class AnalyticsReviewReveal(BaseModel):
    evidence_reviews: list[BacktestReviewMetadata]


class AnalyticsProfile(Provisional):
    company_id: str
    cutoff: str
    input_sha256: dict[str, str]
    fields: list[BacktestField]
    covered_peer_ids: list[str]
    peer_facts: dict[str, list[BacktestField]]
    reveal: AnalyticsReviewReveal
    recorded: AnalyticsScenario
    presets: list[PresetScenario]
    scorer: ScorerInput


class WeightPerturbation(BaseModel):
    dimension: str
    delta: float
    weights: dict[str, float]
    ranks: list[list[str]]
    roles: dict[str, list[str]]
    changed_roles: list[str]


class BoundaryTie(BaseModel):
    companies: list[str]
    draws: int


class AnalyticsRobustness(Provisional):
    company_id: str
    cutoff: str
    similarity_version: str
    input_sha256: dict[str, str]
    draws: int
    seed: int
    baseline_ranks: list[list[str]]
    membership: dict[str, int]
    ranges: dict[str, dict[str, tuple[float, float]]]
    perturbations: list[WeightPerturbation]
    boundary_ties: list[BoundaryTie]


class SyntheticCurvePoint(BaseModel):
    month: int
    cause: str
    value: float


class SyntheticInterval(BaseModel):
    label: str
    n: int
    value: float
    lower: float
    upper: float


class SyntheticCalibration(BaseModel):
    group: int
    estimate: float
    observed: float
    held_out_n: int


class SyntheticEstimate(BaseModel):
    incidences: dict[str, float]
    shrunk_outcome: float
    interval_90: tuple[float, float]
    effective_sample_size: float
    horizon: float


class AnalyticsMethod(BaseModel):
    synthetic: Literal[True]
    label: str
    seed: int
    reference_n: int
    curves: list[SyntheticCurvePoint]
    sizes: list[SyntheticInterval]
    calibration: list[SyntheticCalibration]
    estimate: SyntheticEstimate
