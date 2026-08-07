"""Тесты инвариантов типов (INV-*) из docs/TRANSFLUX_Formal_Invariants.md, §1."""

import math

from transflux import FluxVar, NoisyFloat, SurvivalState


# --- 1.1 NoisyFloat ---

def test_inv_n1_uncertainty_nonnegative():
    """INV-N1: uncertainty ≥ 0 сохраняется операциями."""
    a = NoisyFloat(5.0, uncertainty=0.3, confidence=0.9)
    b = NoisyFloat(-2.0, uncertainty=0.1, confidence=0.85)
    for z in (a + b, a - b, a * b, a / b):
        assert z.uncertainty >= 0


def test_inv_n2_confidence_bounded():
    """INV-N2: 0 ≤ confidence ≤ 1 сохраняется операциями."""
    a = NoisyFloat(5.0, 0.3, confidence=0.9)
    b = NoisyFloat(2.0, 0.1, confidence=0.85)
    for z in (a + b, a - b, a * b, a / b):
        assert 0.0 <= z.confidence <= 1.0


def test_inv_n3_gradient_of_truth_bounded():
    """INV-N3: 0 ≤ gradient_of_truth() ≤ confidence."""
    cases = [
        NoisyFloat(5.0, 0.0, 0.9),
        NoisyFloat(5.0, 0.3, 0.9),
        NoisyFloat(0.0, 0.5, 0.7),
        NoisyFloat(-3.0, 2.0, 0.4),
    ]
    for n in cases:
        g = n.gradient_of_truth()
        assert 0.0 <= g <= n.confidence + 1e-12


# --- 1.2 FluxVar ---

def test_inv_f1_comfort_bounded():
    """INV-F1: -1 ≤ comfort ≤ 1 после update."""
    flux = FluxVar(value=0.0, comfort=5.0)
    flux.update(1.0)
    assert -1.0 <= flux.comfort <= 1.0


def test_inv_f2_history_bounded():
    """INV-F2: len(history) ≤ maxlen."""
    flux = FluxVar(value=0.0)
    for i in range(100):
        flux.update(float(i))
    assert len(flux.history) <= flux.history.maxlen


def test_inv_f3_trajectory_consistent():
    """INV-F3: trajectory() == list(history) + [value]."""
    flux = FluxVar(value=0.0)
    for i in range(5):
        flux.update(float(i))
    assert flux.trajectory() == list(flux.history) + [flux.value]


def test_inv_f4_update_always_sets_value():
    """INV-F4 (спец. 5.5): trauma — сигнал, не блокировка."""
    flux = FluxVar(value=0.0, trauma_threshold=1.0)
    flux.update(new_value=100.0, dt=0.001)
    assert flux.value == 100.0


def test_inv_f5_velocity_consistent():
    """INV-F5: velocity == (v - old_value) / dt."""
    flux = FluxVar(value=2.0)
    flux.update(new_value=10.0, dt=4.0)
    assert flux.velocity == (10.0 - 2.0) / 4.0


# --- 1.3 SurvivalState ---

def test_inv_s1_threat_level_bounded():
    """INV-S1: 0 ≤ threat_level ≤ 1."""
    s = SurvivalState(panic_threshold=2.0)  # порог вне диапазона: panic не сработает
    s.update(threat_delta=5.0)
    assert 0.0 <= s.threat_level <= 1.0
    s.update(threat_delta=-10.0)
    assert 0.0 <= s.threat_level <= 1.0


def test_inv_s2_s3_s4_s5_panic():
    """INV-S2..S5 (спец. 5.3): детерминизм panic, сброс, ротация identity."""
    s = SurvivalState(threat_level=0.0, panic_threshold=0.75)
    initial_hash = s.identity_hash
    panicked = s.update(threat_delta=0.8)
    assert panicked is True                    # INV-S5
    assert s.threat_level == 0.0               # INV-S2
    assert s.identity_hash != initial_hash     # INV-S3
    assert s._panic_count == 1                 # INV-S4

    # Ниже порога panic не срабатывает (INV-S5, обратная сторона)
    s2 = SurvivalState(panic_threshold=0.75)
    assert s2.update(threat_delta=0.5) is False
    assert s2._panic_count == 0
