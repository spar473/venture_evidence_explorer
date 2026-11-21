"""Seeded masking scaffold. Source loss is not contradiction or relevance evidence."""

import hashlib


def mask_observations(observations, fields, rate, seed):
    if not 0 <= rate <= 1 or not fields:
        raise ValueError('Mask rate must be in [0,1] and fields explicit')
    if any(o['review_status'] != 'accepted' for o in observations):
        raise ValueError('Requires a frozen, reviewed input corpus')
    # Stable per-observation hashing makes masking independent of input order.
    kept, removed = [], []
    for observation in observations:
        draw = (
            int.from_bytes(
                hashlib.sha256((str(seed) + ':' + observation['observation_id']).encode()).digest()[:8], 'big'
            )
            / 2**64
        )
        (removed if observation['field'] in fields and draw < rate else kept).append(dict(observation))
    return {
        'scenario': 'synthetic_field_masking',
        'seed': seed,
        'rate': rate,
        'fields': sorted(fields),
        'kept': kept,
        'removed_ids': sorted(o['observation_id'] for o in removed),
        'limitations': 'Declared experimental loss mechanism; not measured real-world missingness. No human relevance judgments created.',
    }
