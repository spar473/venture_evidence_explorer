"""Configuration boundary only; reviewed scales and development labels are pending."""

from dataclasses import dataclass
from typing import Literal
import math


@dataclass(frozen=True)
class Dimension:
    field: str
    weight: float
    similarity: Literal['categorical_exact', 'set_jaccard', 'numeric_range']
    units: str | None = None
    scale: float | None = None

    def __post_init__(self):
        if not self.field or not math.isfinite(self.weight) or self.weight <= 0:
            raise ValueError('Dimension needs a field and finite positive relevance weight')
        if self.similarity not in ('categorical_exact', 'set_jaccard', 'numeric_range'):
            raise ValueError('Unsupported similarity')
        if self.similarity == 'numeric_range' and (
            not self.units or self.scale is None or not math.isfinite(self.scale) or self.scale <= 0
        ):
            raise ValueError('Numeric dimensions need declared units and a justified positive scale')


def research_status():
    return {
        'status': 'scaffolded',
        'scoring_enabled': False,
        'prerequisites': [
            'Accepted sourced structured features',
            'Investigation-specific dimensions, units and justified scales',
            'Human relevance judgments and coverage-policy validation',
        ],
        'proposed_definition': 'S=sum(observed w*s)/sum(observed w); coverage=sum(observed w)/sum(all w). Sparse-pair inflation requires validation.',
    }
