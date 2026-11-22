"""Validate source-backed entry features and present-day project profiles."""

from datetime import date, timedelta
from pathlib import Path
from typing import Literal

from pydantic import Field, StrictInt, model_validator

from .database import ROOT
from .ingestion import StrictModel, Text, day
from .precedent_evidence import CONTEMPORANEOUS_WINDOW_DAYS, pool_claim
from .precedent_similarity import CLINICAL_WORKFLOW, DIMENSIONS, MILESTONES
from .reference_pool import EventDate, Feature, Id, PoolSource, Witness, unique_index
from .research_validation import decode_packet

PACKET = ROOT / 'research/healthtech-pilot/witnessed-snapshots.json'
FEATURES = {field for _, fields in DIMENSIONS.values() for field in fields}
CONTEMPORANEOUS_FIELDS = set(DIMENSIONS[CLINICAL_WORKFLOW][1]) | set(DIMENSIONS['Buyer and sales path'][1])
ProfileScope = Literal[
    'institutional_entry', 'project_as_of', 'institutional_entry_contemporaneous', 'reference_round_context'
]
ANCHORED = {'institutional_entry', 'institutional_entry_contemporaneous'}


class WitnessedProfile(StrictModel):
    subject_id: Id
    scope: ProfileScope
    cutoff: str
    anchor_claim_id: Text | None = None
    features: list[Feature] = Field(min_length=1)


class WitnessedSnapshotPacket(StrictModel):
    format_version: Literal['witnessed-snapshots:1']
    compiled_on: str
    sources: list[PoolSource]
    witnesses: list[Witness]
    profiles: list[WitnessedProfile]

    @model_validator(mode='after')
    def validate_witness_graph(self):
        day(self.compiled_on)
        sources = unique_index(self.sources, 'source_id')
        witnesses = unique_index(self.witnesses, 'witness_id')
        keys = {(profile.subject_id, profile.scope) for profile in self.profiles}
        if len(keys) != len(self.profiles):
            raise ValueError('Duplicate subject and snapshot scope')
        for witness in witnesses.values():
            source = sources.get(witness.source_id)
            if source is None or source.retrieved_on > self.compiled_on:
                raise ValueError('Witness requires a source retrieved by the compilation date')
            witness.check_source(source)
        for profile in self.profiles:
            if day(profile.cutoff) > self.compiled_on:
                raise ValueError('Profile cutoff exceeds the compilation date')
            if (profile.scope in ANCHORED) != bool(profile.anchor_claim_id):
                raise ValueError('Entry profiles require a specific existing anchor claim')
            contemporaneous = profile.scope == 'institutional_entry_contemporaneous'
            round_day = date.fromisoformat(profile.cutoff)
            cutoff = (
                (round_day + timedelta(days=CONTEMPORANEOUS_WINDOW_DAYS)).isoformat()
                if contemporaneous
                else profile.cutoff
            )
            cutoff = min(cutoff, self.compiled_on)
            unique_index(profile.features, 'name')
            for feature in profile.features:
                witness = witnesses.get(feature.witness_id)
                if not witness or witness.source_id != feature.source_id or witness.available_on > cutoff:
                    raise ValueError('Feature requires a source-version witness by its profile cutoff')
                published = sources[feature.source_id].published_on
                if published and published > cutoff:
                    raise ValueError('Feature source publication exceeds its profile cutoff')
                if (
                    profile.scope in ('institutional_entry_contemporaneous', 'reference_round_context')
                    and feature.name not in CONTEMPORANEOUS_FIELDS
                ):
                    raise ValueError('Round descriptions are limited to clinical workflow and buyer fields')
                if contemporaneous and witness.available_on <= profile.cutoff:
                    raise ValueError('Contemporaneous profiles require a later workflow or buyer witness')
                if feature.name not in FEATURES:
                    raise ValueError('Feature must belong to a comparison dimension')
                if feature.name in MILESTONES and feature.value not in ('yes', 'no'):
                    raise ValueError('A witnessed milestone must have an explicit Yes or No value')
        return self


class WitnessedSnapshots:
    def __init__(self, path: Path = PACKET):
        packet = WitnessedSnapshotPacket.model_validate(decode_packet(path.read_bytes()))
        self.sources = unique_index(packet.sources, 'source_id')
        self.witnesses = unique_index(packet.witnesses, 'witness_id')
        self.profiles = {(profile.subject_id, profile.scope): profile for profile in packet.profiles}

    def claims(self, subject_id, as_of, *, entry_anchor=None, scope: ProfileScope = 'institutional_entry'):
        profile = self.profiles.get((subject_id, scope))
        if profile is None:
            return []
        if scope in ANCHORED and (
            entry_anchor is None
            or entry_anchor.kind != 'first_institutional_round'
            or entry_anchor.claim.claim_id != profile.anchor_claim_id
            or entry_anchor.claim.lower_on != profile.cutoff
        ):
            return []
        claims = []
        for feature in profile.features:
            witness = self.witnesses[feature.witness_id]
            claim = pool_claim(
                f'witnessed:{subject_id}:{feature.name}:{feature.source_id}',
                feature.name,
                feature.value,
                feature.passage,
                self.sources[feature.source_id],
                [witness],
                when=EventDate(value=witness.available_on, precision='day'),
                basis='Evidence available by this day',
                as_of=as_of,
            )
            if claim:
                claims.append(claim)
        return claims


# Separate packet and review contract: nothing below is loaded by b0:3 or the app.
BACKTEST_PACKET = ROOT / 'research/healthtech-pilot/backtest-snapshots.json'
BACKTEST_FIELDS = (
    'description',
    'product_type',
    'buyer',
    'business_model',
    'sector_normalised',
    'market_focus',
    'prototype',
    'paid_pilot_or_revenue',
    'full_time_team',
    'round_size_band',
    'lead_investor_type',
    'months_since_founding',
)
BACKTEST_DESCRIPTORS = set(BACKTEST_FIELDS[:6])
BACKTEST_MILESTONES = set(BACKTEST_FIELDS[6:9])
BACKTEST_CATEGORIES = {
    'product_type': {
        'software',
        'analytics',
        'workflow',
        'marketplace',
        'hardware',
        'medical_device',
        'industrial_equipment',
        'physical_goods',
        'food_beverage',
        'materials',
        'service',
        'financial_service',
        'professional_service',
    },
    'buyer': {
        'business',
        'small_business',
        'enterprise',
        'consumer',
        'individual',
        'household',
        'public_sector',
        'government',
        'education',
        'clinician',
        'radiologist',
        'optometrist',
        'general_practitioner',
        'surgeon',
    },
    'business_model': {
        'subscription',
        'saas',
        'membership',
        'transaction',
        'marketplace_commission',
        'retail_margin',
        'sales',
        'hardware_sale',
        'licensing',
        'service_fee',
        'professional_fee',
        'pay_per_use',
    },
    'sector_normalised': {
        'digital',
        'enterprise_software',
        'fintech',
        'retail_ecommerce',
        'media',
        'science',
        'healthtech',
        'biotech',
        'agritech',
        'cleantech',
        'advanced_materials',
        'industrial',
        'manufacturing',
        'aerospace',
        'energy',
        'consumer',
        'food_beverage',
        'consumer_products',
    },
    'market_focus': {'new_zealand', 'australia_new_zealand', 'international'},
    'lead_investor_type': {
        'institutional',
        'venture_capital',
        'angel_network',
        'corporate_venture',
        'other',
        'public_fund',
        'accelerator',
    },
    'round_size_band': {'lt0.5m', '0.5m_to_lt2m', '2m_to_lt5m', '5m_to_lt10m', 'gte10m'},
}


class BacktestFeature(StrictModel):
    name: Text
    value: Text | StrictInt
    raw_value: Text | StrictInt
    derivation: Literal['stated', 'normalised', 'calculated']
    rationale: Text
    source_id: Id
    witness_id: Id
    passage: Text
    locator: Text
    effective_on: str | None = None
    timing: Literal['strict', 'lenient'] = 'strict'
    review_state: Literal['proposed', 'confirmed', 'rejected', 'disputed', 'ai_adjudicated'] = 'proposed'
    reviewer: Text | None = None
    reviewed_on: str | None = None
    review_reference: Text | None = None
    proposed_value: Text | StrictInt | None = None
    decided_by: Text | None = None
    review_date: str | None = None
    second_reading_value: str | None = None
    readings_match: Text | None = None
    human_confirmed: bool | None = None

    @model_validator(mode='after')
    def field_and_review(self):
        if self.name not in BACKTEST_FIELDS:
            raise ValueError('Unknown backtest feature')
        if self.name in BACKTEST_MILESTONES and self.value not in ('yes', 'no'):
            raise ValueError('Backtest milestones require explicit yes or no')
        if (
            self.name in BACKTEST_CATEGORIES
            and self.value not in BACKTEST_CATEGORIES[self.name]
            and self.review_state != 'ai_adjudicated'
        ):
            raise ValueError('Backtest categorical value is outside the registered vocabulary')
        if self.name == 'months_since_founding' and (type(self.value) is not int or self.value < 0):
            raise ValueError('Founding age requires nonnegative integer months')
        if self.effective_on is not None:
            day(self.effective_on)
        reviewed = (self.reviewer, self.reviewed_on, self.review_reference)
        if self.decided_by is not None:
            if not self.review_date or not self.readings_match or self.human_confirmed is not False or any(reviewed):
                raise ValueError('AI decisions require dated review metadata and cannot claim human confirmation')
            if self.review_state not in ('ai_adjudicated', 'proposed', 'rejected'):
                raise ValueError('AI decisions cannot assign a human review state')
            day(self.review_date)
        elif self.review_state == 'ai_adjudicated':
            raise ValueError('AI-adjudicated features require decision metadata')
        elif self.review_state == 'proposed':
            if any(value is not None for value in reviewed):
                raise ValueError('A proposal cannot claim a completed human review')
        elif not all(reviewed):
            raise ValueError('Reviewed features require reviewer, date and review reference')
        if self.reviewed_on is not None:
            day(self.reviewed_on)
        return self


class BacktestProfile(StrictModel):
    company_id: Id
    scope: Literal['backtest_entry']
    entry_date: EventDate
    anchor_source_id: Id
    anchor_locator: Text
    features: list[BacktestFeature]


class BacktestInvestigation(StrictModel):
    company_id: Id
    checked_on: str
    url: Text
    disposition: Literal['proposals_recorded', 'later_revision', 'access_blocked', 'insufficient_fields', 'too_late']
    note: Text


class BacktestSnapshotPacket(StrictModel):
    format_version: Literal['backtest-snapshots:1']
    compiled_on: str
    preregistration_commit: str = Field(pattern=r'^[0-9a-f]{40}$')
    cohort_input_sha256: dict[str, str]
    sources: list[PoolSource]
    witnesses: list[Witness]
    profiles: list[BacktestProfile]
    investigations: list[BacktestInvestigation] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_backtest_graph(self):
        import re
        from .reference_pool import https

        day(self.compiled_on)
        if set(self.cohort_input_sha256) != {'discovery', 'entry_evidence'} or any(
            not re.fullmatch(r'[0-9a-f]{64}', value) for value in self.cohort_input_sha256.values()
        ):
            raise ValueError('Backtest requires both frozen cohort input digests')
        sources = unique_index(self.sources, 'source_id')
        witnesses = unique_index(self.witnesses, 'witness_id')
        unique_index(self.profiles, 'company_id')
        for source in sources.values():
            if source.retrieved_on > self.compiled_on:
                raise ValueError('Source retrieval exceeds compilation')
        for witness in witnesses.values():
            if witness.source_id not in sources:
                raise ValueError('Backtest witness requires a known source')
            witness.check_source(sources[witness.source_id])
            published = sources[witness.source_id].published_on
            if published and witness.available_on < published:
                raise ValueError('Backtest witness predates source publication')
        for profile in self.profiles:
            start, end = profile.entry_date.bounds()
            if start is None or end > self.compiled_on:
                raise ValueError('Backtest entry requires a known historical interval')
            unique_index(profile.features, 'name')
            for feature in profile.features:
                witness = witnesses.get(feature.witness_id)
                if not witness or witness.source_id != feature.source_id:
                    raise ValueError('Backtest feature requires a matching source-version witness')
                source = sources[feature.source_id]
                cutoff = start
                if feature.timing == 'lenient':
                    if feature.name not in BACKTEST_DESCRIPTORS:
                        raise ValueError('Lenient evidence is limited to offering, buyer and market descriptors')
                    cutoff = (date.fromisoformat(start) + timedelta(days=90)).isoformat()
                    if witness.available_on <= start:
                        raise ValueError('Lenient evidence must actually be later than entry')
                if any(
                    value and value > cutoff
                    for value in (
                        witness.available_on,
                        source.published_on,
                        source.revised_on,
                        feature.effective_on,
                    )
                ):
                    raise ValueError('Backtest feature exceeds its entry evidence cutoff')
                if feature.reviewed_on and not source.retrieved_on <= feature.reviewed_on <= self.compiled_on:
                    raise ValueError('Feature review must follow source retrieval and precede compilation')
                if feature.review_date and feature.review_date < source.retrieved_on:
                    raise ValueError('AI adjudication must follow source retrieval')
        for investigation in self.investigations:
            https(investigation.url)
            if day(investigation.checked_on) > self.compiled_on:
                raise ValueError('Investigation follows compilation')
        return self
