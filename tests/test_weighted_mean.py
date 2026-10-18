"""weighted_mean: вес 1/σ², точное измерение забирает среднее."""

import math

import pytest

from transflux import NoisyFloat, weighted_mean


def test_empty_readings_are_rejected():
    with pytest.raises(ValueError):
        weighted_mean([])


def test_single_reading_is_unchanged():
    reading = NoisyFloat(3.0, uncertainty=0.4, confidence=0.7)
    result = weighted_mean([reading])
    assert result.value == pytest.approx(3.0)
    assert result.uncertainty == pytest.approx(0.4)
    assert result.confidence == pytest.approx(0.7)


def test_equal_uncertainty_shrinks_by_sqrt_n():
    left = NoisyFloat(10.0, uncertainty=2.0, confidence=0.8)
    right = NoisyFloat(14.0, uncertainty=2.0, confidence=0.6)
    result = weighted_mean([left, right])
    assert result.value == pytest.approx(12.0)
    assert result.uncertainty == pytest.approx(2.0 / math.sqrt(2))
    assert result.confidence == pytest.approx(0.7)


def test_noisy_outlier_barely_moves_the_mean():
    calm_a = NoisyFloat(12.0, uncertainty=1.0, confidence=0.92)
    calm_b = NoisyFloat(15.0, uncertainty=1.2, confidence=0.88)
    broken = NoisyFloat(300.0, uncertainty=40.0, confidence=0.20)
    result = weighted_mean([calm_a, calm_b, broken])
    assert result.value == pytest.approx(13.3354, abs=1e-3)
    assert result.uncertainty == pytest.approx(0.7681, abs=1e-3)
    assert result.confidence == pytest.approx(0.9033, abs=1e-3)
    assert result.confidence > broken.confidence


def test_exact_reading_overrides_a_noisy_one():
    exact = NoisyFloat(10.0, uncertainty=0.0, confidence=0.95)
    noisy = NoisyFloat(100.0, uncertainty=5.0, confidence=0.2)
    result = weighted_mean([exact, noisy])
    assert result.value == pytest.approx(10.0)
    assert result.uncertainty == pytest.approx(0.0)
    assert result.confidence == pytest.approx(0.95)


def test_disagreeing_exact_readings_keep_their_spread():
    result = weighted_mean([
        NoisyFloat(5.0, uncertainty=0.0, confidence=1.0),
        NoisyFloat(7.0, uncertainty=0.0, confidence=0.5),
    ])
    assert result.value == pytest.approx(6.0)
    assert result.uncertainty == pytest.approx(1.0)
    assert result.confidence == pytest.approx(0.5)
