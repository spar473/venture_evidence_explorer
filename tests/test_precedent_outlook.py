import pytest

from backend.precedent_outlook import FollowUpPeer, estimate_outlook, weighted_cif


def test_weighted_aalen_johansen_handles_competing_events_and_tied_censoring():
    peers = [FollowUpPeer(1, 1, 'outcome'), FollowUpPeer(1, 1, 'closure'),
             FollowUpPeer(1, 1, 'censored'), FollowUpPeer(1, 2, 'exit'),
             FollowUpPeer(1, 3, 'outcome')]
    weights = [2, 1, 1, 1, 1]
    assert weighted_cif(peers, weights, 1) == pytest.approx({'outcome':2/6, 'closure':1/6, 'exit':0})
    assert weighted_cif(peers, weights, 2) == pytest.approx({'outcome':2/6, 'closure':1/6, 'exit':1/4})
    assert weighted_cif(peers, weights, 3) == pytest.approx({'outcome':2/6+1/4, 'closure':1/6, 'exit':1/4})


def test_effective_sample_gate_shrinkage_and_reproducible_bootstrap():
    peers = [FollowUpPeer(1, 1, 'outcome')] * 4 + [FollowUpPeer(1, 1, 'closure')] * 3 + [FollowUpPeer(1, 2, 'censored')] * 3
    assert estimate_outlook(iter(()), gate_ready=False, base_rate=.2) is None
    assert estimate_outlook(peers[:9], gate_ready=True, base_rate=.2) is None
    unequal = [FollowUpPeer(1, 1, 'outcome')] + [FollowUpPeer(.01, 2, 'censored')] * 11
    assert estimate_outlook(unequal, gate_ready=True, base_rate=.2) is None
    first = estimate_outlook(peers, gate_ready=True, base_rate=.2, prior_strength=10, bootstrap_samples=200, seed=14)
    assert first == estimate_outlook(peers, gate_ready=True, base_rate=.2, prior_strength=10, bootstrap_samples=200, seed=14)
    assert first.effective_sample_size == pytest.approx(10)
    assert first.incidences == pytest.approx({'outcome':.4, 'closure':.3, 'exit':0})
    assert first.shrunk_outcome == pytest.approx(.3)
    assert 0 <= first.interval_90[0] < first.shrunk_outcome < first.interval_90[1] <= 1
    with pytest.raises(ValueError):
        FollowUpPeer(1, -1, 'outcome')
