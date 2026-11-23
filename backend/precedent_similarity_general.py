"""Frozen cross-sector entry similarity, separate from the clinical profile."""

from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
import math
from typing import Mapping, cast

from pydantic import BaseModel, Field

from .database import ROOT
from .precedent_contracts import DimensionScore
from .precedent_similarity import corpus_idf
from .retrieval import tokens

VERSION = 'general-gower-b1:1'
MIN_SIMILARITY = 0.35
MIN_COVERAGE = 0.35
MIN_PRODUCT = 0.25
PRODUCT = 'Product and customer'
DIMENSIONS = {
    PRODUCT: (0.35, ('description', 'product_type', 'buyer', 'business_model')),
    'Market': (0.15, ('sector_normalised', 'market_focus')),
    'Stage evidence': (0.30, ('prototype', 'paid_pilot_or_revenue', 'full_time_team')),
    'Funding context': (0.20, ('round_size_band', 'lead_investor_type', 'months_since_founding')),
}
ROUND_BANDS = ('lt0.5m', '0.5m_to_lt2m', '2m_to_lt5m', '5m_to_lt10m', 'gte10m')
FieldValue = str | int
Snapshot = Mapping[str, FieldValue]


class FamilyTree(BaseModel):
    families: dict[str, list[str]]
    aliases: dict[str, str] = Field(default_factory=dict)
    flat: bool = False

    def nodes(self) -> dict[str, str | None]:
        parents = {parent: None for parent in self.families if not self.flat}
        return {**parents, **{child: parent for parent, children in self.families.items() for child in children}}


class Vocabulary(BaseModel):
    version: str
    fields: dict[str, FamilyTree]


VOCABULARY_BYTES = (ROOT / 'schema/vocabulary/general-b1.json').read_bytes()
VOCABULARY_DIGEST = sha256(VOCABULARY_BYTES).hexdigest()
VOCABULARY = Vocabulary.model_validate_json(VOCABULARY_BYTES)
if VOCABULARY.version != VERSION:
    raise ValueError('Unexpected cross-sector vocabulary version')


def categorical_score(field: str, left: str, right: str) -> float | None:
    tree = VOCABULARY.fields[field]
    nodes = tree.nodes()
    if left not in nodes or right not in nodes:
        return None
    if left == right:
        return 1.0
    if not tree.flat and (nodes[left] == right or nodes[right] == left or nodes[left] == nodes[right] is not None):
        return 0.5
    return 0.0


def normalise(snapshot: Snapshot) -> tuple[dict[str, FieldValue], dict[str, FieldValue]]:
    known = {}
    unknown = {}
    for name, raw in snapshot.items():
        if name in VOCABULARY.fields:
            tree = VOCABULARY.fields[name]
            value = ' '.join(str(raw).casefold().split())
            value = tree.aliases.get(value, value)
            if value not in tree.nodes():
                unknown[name] = raw
                continue
            known[name] = value
        elif name != 'description' or tokens(str(raw)):
            if name == 'round_size_band' and raw not in ROUND_BANDS:
                unknown[name] = raw
            else:
                known[name] = raw
    return known, unknown


def field_score(name: str, left: FieldValue, right: FieldValue, idf: Mapping[str, float]) -> float | None:
    if name in VOCABULARY.fields:
        return categorical_score(name, str(left), str(right))
    if name == 'description':
        a, b = cast(set[str], tokens(str(left))), cast(set[str], tokens(str(right)))
        total = sum(idf[term] for term in sorted(a | b))
        return sum(idf[term] for term in sorted(a & b)) / total if total else None
    if name == 'months_since_founding':
        return max(0.0, 1 - abs(int(left) - int(right)) / 120)
    if name == 'round_size_band':
        return 1 - abs(ROUND_BANDS.index(str(left)) - ROUND_BANDS.index(str(right))) / 4
    return float(left == right)


@dataclass(frozen=True)
class PairScore:
    similarity: float
    coverage: float
    dimensions: list[DimensionScore]
    fields: dict[str, float]

    def failed_bars(self, subject_fields: int, peer_fields: int, min_fields: int) -> list[str]:
        return [
            bar
            for bar, passed in (
                ('similarity', self.similarity >= MIN_SIMILARITY),
                ('coverage', self.coverage >= MIN_COVERAGE),
                ('product_customer', (self.dimensions[0].similarity or 0) >= MIN_PRODUCT),
                ('subject_fields', subject_fields >= min_fields),
                ('peer_fields', peer_fields >= min_fields),
            )
            if not passed
        ]


def score(left: Snapshot, right: Snapshot, idf: Mapping[str, float]) -> PairScore:
    dimensions = []
    field_scores = {}
    coverage = weighted_sum = available_weight = 0.0
    for dimension, (weight, fields) in DIMENSIONS.items():
        scores = {}
        for name in fields:
            if name in left and name in right:
                value = field_score(name, left[name], right[name], idf)
                if value is not None:
                    scores[name] = value
        observed = len(scores) / len(fields)
        similarity = sum(scores.values()) / len(scores) if scores else None
        coverage += weight * observed
        if similarity is not None:
            weighted_sum += weight * similarity
            available_weight += weight
        dimensions.append(
            DimensionScore(
                dimension=dimension,
                similarity=similarity,
                coverage=observed,
                matched_fields=[key for key, value in scores.items() if value > 0],
                different_fields=[key for key, value in scores.items() if value < 1],
            )
        )
        field_scores.update(scores)
    return PairScore(weighted_sum / available_weight if available_weight else 0.0, coverage, dimensions, field_scores)


def description_idf(snapshots: list[Snapshot]) -> dict[str, float]:
    count = sum('description' in snapshot for snapshot in snapshots)
    # A peer below the field bar is scored for inspection without adding its
    # text to the fit corpus. Its unseen terms have document frequency zero.
    return defaultdict(lambda: 1 + math.log(count + 1), cast(dict[str, float], corpus_idf(snapshots)))
