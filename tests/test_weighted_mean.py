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


def test_full_correlation_does_not_shrink_equal_sensors():
    left = NoisyFloat(10.0, uncertainty=2.0, confidence=0.9)
    right = NoisyFloat(14.0, uncertainty=2.0, confidence=0.5)
    independent = weighted_mean([left, right])
    coupled = weighted_mean([left, right], correlation=1.0)
    assert coupled.value == pytest.approx(independent.value)
    assert coupled.uncertainty == pytest.approx(2.0)
    assert coupled.confidence == pytest.approx(0.5)


def test_partial_correlation_inflates_between_extremes():
    readings = [
        NoisyFloat(10.0, uncertainty=2.0, confidence=0.8),
        NoisyFloat(14.0, uncertainty=2.0, confidence=0.6),
    ]
    independent = weighted_mean(readings, correlation=0.0)
    partial = weighted_mean(readings, correlation=0.5)
    full = weighted_mean(readings, correlation=1.0)
    assert independent.uncertainty < partial.uncertainty < full.uncertainty
    assert partial.confidence == pytest.approx(0.65)


def test_correlation_out_of_range_is_rejected():
    reading = NoisyFloat(1.0, uncertainty=1.0, confidence=1.0)
    with pytest.raises(ValueError):
        weighted_mean([reading], correlation=-0.1)
    with pytest.raises(ValueError):
        weighted_mean([reading], correlation=1.1)


def test_full_covariance_matches_scalar_when_uniform():
    """Одинаковые σ и попарное ρ: GLS совпадает со скалярной формулой.

    ρ=1 даёт вырожденную Σ — для полной матрицы берём ρ=0.5.
    """
    left = NoisyFloat(10.0, uncertainty=2.0, confidence=0.8)
    right = NoisyFloat(14.0, uncertainty=2.0, confidence=0.6)
    scalar = weighted_mean([left, right], correlation=0.5)
    cov = [
        [4.0, 2.0],
        [2.0, 4.0],
    ]
    gls = weighted_mean([left, right], covariance=cov)
    assert gls.value == pytest.approx(scalar.value)
    assert gls.uncertainty == pytest.approx(scalar.uncertainty)
    assert gls.confidence == pytest.approx(scalar.confidence)


def test_asymmetric_covariance_changes_weights():
    calm = NoisyFloat(10.0, uncertainty=1.0, confidence=0.9)
    noisy = NoisyFloat(20.0, uncertainty=2.0, confidence=0.9)
    independent = weighted_mean([calm, noisy], correlation=0.0)
    # Corr(calm, noisy)=0.5 → cov12 = 0.5*1*2 = 1.0
    cov = [
        [1.0, 1.0],
        [1.0, 4.0],
    ]
    gls = weighted_mean([calm, noisy], covariance=cov)
    assert gls.uncertainty > independent.uncertainty
    assert gls.value != pytest.approx(independent.value)


def test_covariance_rejects_bad_shape_and_both_modes():
    a = NoisyFloat(1.0, uncertainty=1.0, confidence=1.0)
    b = NoisyFloat(2.0, uncertainty=1.0, confidence=1.0)
    with pytest.raises(ValueError):
        weighted_mean([a, b], correlation=0.2, covariance=[[1, 0], [0, 1]])
    with pytest.raises(ValueError):
        weighted_mean([a, b], covariance=[[1.0]])
    with pytest.raises(ValueError):
        weighted_mean([a, b], covariance=[[1.0, 0.0], [0.1, 1.0]])


def test_covariance_rejects_exact_readings():
    exact = NoisyFloat(1.0, uncertainty=0.0, confidence=1.0)
    noisy = NoisyFloat(2.0, uncertainty=1.0, confidence=1.0)
    with pytest.raises(ValueError):
        weighted_mean([exact, noisy], covariance=[[0.0, 0.0], [0.0, 1.0]])
