"""Synthetic-only demonstration of the locked competing-outcomes estimator."""

from dataclasses import asdict
from functools import lru_cache
from random import Random
from typing import Any

from .precedent_outlook import CAUSES, Cause, FollowUpPeer, estimate_outlook, weighted_cif

SYNTHETIC_LABEL = 'Synthetic cohort, no real company'
TODAY_REFERENCE_N = 55


def synthetic_peers(rng: Random, count: int, risk: float) -> list[FollowUpPeer]:
    peers = []
    for _ in range(count):
        times: dict[Cause, float] = {
            'outcome': rng.expovariate(risk),
            'closure': rng.expovariate(0.013),
            'exit': rng.expovariate(0.005),
            'censored': min(37, rng.expovariate(0.009)),
        }
        cause, duration = min(times.items(), key=lambda item: item[1])
        peers.append(FollowUpPeer(round(rng.uniform(0.55, 0.95), 6), round(duration, 6), cause))
    return peers


def estimate(peers: list[FollowUpPeer], seed: int) -> Any:
    result = estimate_outlook(peers, gate_ready=True, base_rate=0.30, seed=seed)
    if result is None:
        raise ValueError('Synthetic sample missed the effective-size bar')
    return result


@lru_cache(maxsize=8)
def method_lab(seed: int, today_n: int = TODAY_REFERENCE_N) -> dict[str, Any]:
    if not 20 <= today_n <= 500:
        raise ValueError('The reference count must be between 20 and 500')
    rng = Random(seed)
    peers = synthetic_peers(rng, 500, 0.018)
    weights = [peer.similarity**2 for peer in peers]
    curves = []
    for month in range(37):
        cif = weighted_cif(peers, weights, month)
        curves.extend({'month': month, 'cause': cause, 'value': cif[cause]} for cause in CAUSES)
    sizes = []
    for label, size in [('Today', today_n), ('150', 150), ('500', 500)]:
        fitted = estimate(peers[:size], seed)
        sizes.append(
            {
                'label': label,
                'n': size,
                'value': fitted.shrunk_outcome,
                'lower': fitted.interval_90[0],
                'upper': fitted.interval_90[1],
            }
        )
    calibration = []
    for i, risk in enumerate((0.004, 0.012, 0.025, 0.045, 0.08), start=1):
        train = synthetic_peers(rng, 120, risk)
        held_out = synthetic_peers(rng, 240, risk)
        observed = weighted_cif(held_out, [1] * len(held_out), 36)['outcome']
        calibration.append(
            {
                'group': i,
                'estimate': estimate(train, seed).shrunk_outcome,
                'observed': observed,
                'held_out_n': len(held_out),
            }
        )
    return {
        'label': SYNTHETIC_LABEL,
        'synthetic': True,
        'seed': seed,
        'reference_n': today_n,
        'curves': curves,
        'sizes': sizes,
        'calibration': calibration,
        'estimate': asdict(estimate(peers, seed)),
    }


def synthetic_cohort(seed: int) -> dict[str, Any]:
    return {
        'synthetic': True,
        'label': SYNTHETIC_LABEL,
        'seed': seed,
        'companies': [
            {'id': f'synthetic-{i:03}', **asdict(peer)}
            for i, peer in enumerate(synthetic_peers(Random(seed), 500, 0.018), start=1)
        ],
    }
