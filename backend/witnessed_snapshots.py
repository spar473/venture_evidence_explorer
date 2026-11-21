"""Validate source-backed entry features and present-day project profiles."""

from datetime import date, timedelta
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

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
