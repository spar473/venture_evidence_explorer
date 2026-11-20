"""Internal kernel-weighted cumulative incidence. No workbench API publishes it."""
from collections import defaultdict
from dataclasses import dataclass
from math import floor, fsum, isfinite
from random import Random
from typing import Literal

Cause = Literal['outcome', 'closure', 'exit', 'censored']
CAUSES = ('outcome', 'closure', 'exit')


@dataclass(frozen=True)
class FollowUpPeer:
    similarity: float
    duration: float
    cause: Cause

    def __post_init__(self):
        if not isfinite(self.similarity) or not 0 <= self.similarity <= 1:
            raise ValueError('Similarity must be between zero and one')
        if not isfinite(self.duration) or self.duration < 0:
            raise ValueError('Follow-up duration must be finite and nonnegative')
        if self.cause not in (*CAUSES, 'censored'):
            raise ValueError('Unknown follow-up cause')


@dataclass(frozen=True)
class OutlookEstimate:
    incidences: dict[str, float]
    shrunk_outcome: float
    interval_90: tuple[float, float]
    effective_sample_size: float
    horizon: float


def weighted_cif(peers, weights, horizon):
    """Aalen–Johansen with tied events and censoring leaving a shared risk set."""
    at_risk = sum(weights)
    survival = 1.
    incidence = dict.fromkeys(CAUSES, 0.)
    groups = defaultdict(lambda: defaultdict(float))
    for peer, weight in zip(peers, weights, strict=True):
        if peer.duration <= horizon and weight:
            groups[peer.duration][peer.cause] += weight
    for duration in sorted(groups):
        group = groups[duration]
        if at_risk <= 0:
            break
        increments = {cause: group[cause] / at_risk for cause in CAUSES}
        for cause, increment in increments.items():
            incidence[cause] += survival * increment
        survival *= max(0., 1 - sum(increments.values()))
        at_risk -= sum(group.values())
    return {cause: min(1., value) for cause, value in incidence.items()}


def percentile(ordered, probability):
    index = probability * (len(ordered) - 1)
    lower = floor(index)
    upper = min(len(ordered) - 1, lower + 1)
    return ordered[lower] + (index - lower) * (ordered[upper] - ordered[lower])


def estimate_outlook(peers, *, gate_ready, base_rate, horizon=36., gamma=2., prior_strength=4.,
                     bootstrap_samples=500, seed=0):
    """Use supplied training parameters and a fixed horizon in the peer duration unit.

    Intervals are evaluated by calling separately with the lower and upper
    event-time assignments. Unknown histories never enter the estimator.
    """
    if not gate_ready:
        return None
    if (not all(isfinite(x) for x in (base_rate, horizon, gamma, prior_strength))
        or not 0 <= base_rate <= 1 or horizon <= 0 or gamma <= 0 or prior_strength < 0
        or not isinstance(bootstrap_samples, int) or bootstrap_samples < 2):
        raise ValueError('Invalid estimator configuration')
    weighted = [(peer, weight) for peer in peers if (weight := peer.similarity ** gamma) > 0]
    if not weighted:
        return None
    peers, weights = zip(*weighted)
    weight_sum = fsum(weights)
    effective = 1 / fsum((weight / weight_sum) ** 2 for weight in weights)
    if effective < 10 - 1e-12:
        return None

    def shrunk(value, total):
        return (total * value + prior_strength * base_rate) / (total + prior_strength)

    incidences = weighted_cif(peers, weights, horizon)
    rng = Random(seed)
    replicates = []
    for _ in range(bootstrap_samples):
        ids = rng.choices(range(len(peers)), k=len(peers))
        sample = [peers[i] for i in ids]
        sample_weights = [weights[i] for i in ids]
        cif = weighted_cif(sample, sample_weights, horizon)
        replicates.append(shrunk(cif['outcome'], sum(sample_weights)))
    replicates.sort()
    return OutlookEstimate(incidences=incidences, shrunk_outcome=shrunk(incidences['outcome'], weight_sum),
        interval_90=(percentile(replicates, .05), percentile(replicates, .95)),
        effective_sample_size=effective, horizon=horizon)
