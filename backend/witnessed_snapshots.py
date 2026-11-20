"""Validate source-backed entry features and present-day project profiles."""
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from .database import ROOT
from .ingestion import StrictModel, Text, day
from .precedent_evidence import pool_claim
from .precedent_similarity import DIMENSIONS, MILESTONES
from .reference_pool import EventDate, Feature, Id, PoolSource, Witness, unique_index
from .research_validation import decode_packet

PACKET = ROOT / 'research/healthtech-pilot/witnessed-snapshots.json'
FEATURES = {field for _, fields in DIMENSIONS.values() for field in fields}


class WitnessedProfile(StrictModel):
    subject_id: Id
    scope: Literal['institutional_entry', 'project_as_of']
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
        unique_index(self.profiles, 'subject_id')
        for witness in witnesses.values():
            source = sources.get(witness.source_id)
            if source is None or source.retrieved_on > self.compiled_on:
                raise ValueError('Witness requires a source retrieved by the compilation date')
            witness.check_source(source)
        for profile in self.profiles:
            if day(profile.cutoff) > self.compiled_on:
                raise ValueError('Profile cutoff exceeds the compilation date')
            if (profile.scope == 'institutional_entry') != bool(profile.anchor_claim_id):
                raise ValueError('Entry profiles require a specific existing anchor claim')
            unique_index(profile.features, 'name')
            for feature in profile.features:
                witness = witnesses.get(feature.witness_id)
                if (not witness or witness.source_id != feature.source_id or witness.available_on > profile.cutoff):
                    raise ValueError('Feature requires a source-version witness by its profile cutoff')
                published = sources[feature.source_id].published_on
                if published and published > profile.cutoff:
                    raise ValueError('Feature source publication exceeds its profile cutoff')
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
        self.profiles = unique_index(packet.profiles, 'subject_id')

    def claims(self, subject_id, as_of, *, entry_anchor=None, is_project=False):
        profile = self.profiles.get(subject_id)
        if profile is None:
            return []
        if profile.scope == 'project_as_of':
            if not is_project:
                return []
        elif (entry_anchor is None or entry_anchor.kind != 'first_institutional_round'
              or entry_anchor.claim.claim_id != profile.anchor_claim_id
              or entry_anchor.claim.lower_on != profile.cutoff):
            return []
        claims = []
        for feature in profile.features:
            witness = self.witnesses[feature.witness_id]
            claim = pool_claim(f'witnessed:{subject_id}:{feature.name}:{feature.source_id}', feature.name, feature.value,
                feature.passage, self.sources[feature.source_id], [witness],
                when=EventDate(value=witness.available_on, precision='day'),
                basis='Evidence available by this day', as_of=as_of)
            if claim:
                claims.append(claim)
        return claims
