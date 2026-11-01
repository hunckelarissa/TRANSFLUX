"""Хелперы stale_threat и uncertainty_margin_threat."""

import pytest

from transflux import (
    NoisyFloat,
    NoisyFlow,
    TransfluxSystem,
    FluxVar,
    SurvivalState,
    stale_threat,
    uncertainty_margin_threat,
)


def test_stale_threat_zero_before_timeout():
    assert stale_threat(elapsed=4.0, timeout=5.0) == 0.0


def test_stale_threat_grows_after_timeout():
    assert stale_threat(elapsed=10.0, timeout=5.0, sensitivity=1.0) == 1.0
    assert stale_threat(elapsed=7.5, timeout=5.0, sensitivity=1.0) == 0.5


def test_stale_threat_rejects_nonpositive_timeout():
    with pytest.raises(ValueError):
        stale_threat(1.0, timeout=0.0)


def test_uncertainty_margin_within_limit():
    noisy = NoisyFloat(1.0, uncertainty=0.2, confidence=0.9)
    assert uncertainty_margin_threat(noisy, max_uncertainty=0.5) == 0.0


def test_uncertainty_margin_above_limit():
    noisy = NoisyFloat(1.0, uncertainty=1.0, confidence=0.9)
    assert uncertainty_margin_threat(noisy, max_uncertainty=0.5) == 1.0


def test_noisy_flow_is_flux_of_noisy_float():
    channel: NoisyFlow = FluxVar(value=NoisyFloat(1.0, 0.1, 0.9))
    channel.flow(NoisyFloat(2.0, 0.2, 0.8))
    assert channel.value.value == pytest.approx(2.0)
    assert channel.value.uncertainty == pytest.approx(0.2)


def test_tick_applies_stale_and_margin():
    system = TransfluxSystem(
        state=FluxVar(value=0.0, trauma_threshold=100.0),
        survival=SurvivalState(panic_threshold=0.95, decay_rate=0.0),
        flow_sensitivity=0.0,
        uncertainty_sensitivity=0.0,
        signal_timeout=2.0,
        uncertainty_limit=0.3,
        margin_sensitivity=0.5,
        stale_sensitivity=0.5,
    )
    quiet = NoisyFloat(1.0, uncertainty=0.1, confidence=1.0)
    assert system.tick(1.0, quiet, signal_age=1.0) is False
    assert system.survival.threat_level == 0.0

    loud = NoisyFloat(1.0, uncertainty=0.6, confidence=1.0)
    assert system.tick(1.0, loud, signal_age=1.0) is False
    assert system.survival.threat_level == pytest.approx(0.5)
    assert system.peak_threat == pytest.approx(0.5)

    system.survival.threat_level = 0.0
    assert system.tick(1.0, quiet, signal_age=4.0) is False
    assert system.survival.threat_level == pytest.approx(0.5)
