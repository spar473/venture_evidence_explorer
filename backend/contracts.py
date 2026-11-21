"""Exported API contracts. Input assertions are separately typed in ingestion."""

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class Contract(BaseModel):
    model_config = ConfigDict(extra='forbid')


class PartialDate(Contract):
    precision: Literal['unknown', 'day', 'month', 'year']
    lower_bound: str | None = None
    upper_bound: str | None = None


class ObservationRelation(Contract):
    relation_id: str
    observation_id: str
    replacement_id: str
    relation_type: Literal['supersedes', 'corrects']
    reviewer: str
    recorded_at: str
    rationale: str


class FinancialValue(Contract):
    raw_amount: str
    currency: str | None
    amount_qualifier: str
    scope: str
    event_date: PartialDate


class EventValue(Contract):
    event_type: str
    description: str
    event_date: PartialDate


class Observation(Contract):
    observation_id: str
    venture_id: str
    field: str
    value_text: str
    source_id: str
    source_title: str
    url: str
    publisher: str
    published_at: str | None
    retrieved_at: str
    locator: str
    review_status: str
    assertion_type: str
    effective_at: str | None
    date_basis: str
    limitations: str
    effective_review_status: str = 'unreviewed'
    superseded: bool = False
    relations: list[ObservationRelation] = Field(default_factory=list)
    financial_value: FinancialValue | None = None
    event_value: EventValue | None = None
    publication_date: PartialDate | None = None
    effective_date: PartialDate | None = None
    announcement_date: PartialDate | None = None


class Award(Contract):
    award_id: str
    venture_id: str
    programme: str
    award_year: int
    award_label: str
    place: int | None
    event_date: str | None
    publication_date: PartialDate
    event_interval: PartialDate
    source_id: str
    locator: str
    review_status: str
    source_title: str
    url: str
    publisher: str
    published_at: str | None
    retrieved_at: str
    limitations: str


class Connection(Contract):
    connection_id: str
    venture_id: str
    connection_type: str
    institution: str
    observation_id: str
    evidence: Observation


class Annotation(Contract):
    annotation_id: str
    venture_id: str
    field: str
    value_text: str
    basis_observation_ids: list[str]
    origin: str
    review_status: str
    purpose: str


class VentureIdentity(Contract):
    venture_id: str
    display_name: str
    aliases: list[str]
    entity_type: str
    legal_name: str | None
    registration_id: str | None
    current_operating_status: str | None
    current_funding_stage: str | None
    selection_bucket: str
    identity_review_status: str


class Recognition(Contract):
    award_id: str
    programme: str
    award_year: int


class VentureSummary(VentureIdentity):
    product_excerpt: str | None
    award_count: int
    recognitions: list[Recognition]
    connection_types: list[str]
    source_count: int
    publication_dates: list[str | None]


class Venture(VentureIdentity):
    observations: list[Observation]
    awards: list[Award]
    connections: list[Connection]
    proposed_annotations: list[Annotation]


class VenturePage(Contract):
    items: list[VentureSummary]
    total: int
    filtered_ventures: int
    total_ventures: int
    limit: int
    offset: int


class ProgrammeFacet(Contract):
    programme: str
    awards: int
    ventures: int


class ConnectionFacet(Contract):
    connection_type: str
    recorded_connections: int
    distinct_ventures: int


class Facets(Contract):
    programmes: list[ProgrammeFacet]
    years: list[int]
    connection_types: list[ConnectionFacet]
    counts: dict[str, int]


class ComparisonRequest(Contract):
    query: str = Field(default='', max_length=5000)
    subject_id: str | None = None
    mode: Literal['product_customer', 'commercialisation', 'stage_milestone'] = 'product_customer'
    programme: str = ''
    year: int | None = None
    connection_type: str = ''
    policy: Literal['exploration', 'accepted'] = 'exploration'
    cutoff: str | None = Field(default=None, pattern=r'^\d{4}-\d{2}-\d{2}$')


class Method(Contract):
    name: str
    version: str
    normalization: str
    fields: dict[str, list[str]]
    scoring: str
    abstention: str
    limitations: str


class EvidencePolicy(Contract):
    version: str
    name: str
    description: str
    historical_cutoff: str | None
    availability_requirement: str


class MatchEvidence(Contract):
    observation: Observation
    matched_terms: list[str]


class WordingDifferences(Contract):
    query_only_terms: list[str]
    candidate_only_terms: list[str]
    meaning: str


class ComparisonResult(Contract):
    venture: Venture
    ranking_score: float
    query_token_coverage: float
    matched_terms: list[str]
    evidence: list[MatchEvidence]
    wording_differences: WordingDifferences
    unavailable_evidence: list[str]
    brief: str


class SelectedObservation(Contract):
    observation_id: str
    review_status: str


class ResultItemSignature(Contract):
    venture_id: str
    ranking_score: float
    query_token_coverage: float
    matched_terms: list[str]
    observation_ids: list[str]


class ResultSignature(Contract):
    abstention_reason: str | None
    subject_id: str | None
    results: list[ResultItemSignature]


class ComparisonRun(Contract):
    record_version: str
    method_version: str
    policy_version: str
    corpus_digest: str
    request: ComparisonRequest
    selected_observations: list[SelectedObservation]
    result_signature: ResultSignature
    run_id: str


class Comparison(Contract):
    method: Method
    mode: str
    query: str
    effective_query: str | None = None
    subject: Venture | None
    results: list[ComparisonResult]
    questions: list[str]
    brief_type: str
    annotations_used: bool
    abstention_reason: str | None
    evidence_policy: EvidencePolicy
    run: ComparisonRun


class ProgrammeRecognition(Contract):
    programme: str
    award_year: int
    recorded_awards: int
    distinct_ventures: int


class SourceCoverage(Contract):
    venture_id: str
    display_name: str
    source_count: int
    observation_count: int
    earliest_source_date: str | None
    latest_source_date: str | None
    latest_retrieval_date: str | None
    as_of_date: str
    latest_source_age_days: int | None
    evidence_note: str


class AnalyticsTables(Contract):
    programme_recognition: list[ProgrammeRecognition]
    connection_coverage: list[ConnectionFacet]
    source_coverage: list[SourceCoverage]


class AnalyticsResponse(Contract):
    scope: str
    tables: AnalyticsTables


class Health(Contract):
    status: Literal['ok']
    schema_migrations: list[str]
