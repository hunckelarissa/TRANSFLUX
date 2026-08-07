"""Тесты свойств операций (OP-*) из docs/TRANSFLUX_Formal_Invariants.md, §2."""

import math

import pytest

from transflux import NoisyFloat


def test_op_1_uncertainty_nondecreasing_add():
    """OP-1 (спец. 5.1): uncertainty не убывает при сложении."""
    a = NoisyFloat(value=5.0, uncertainty=0.3, confidence=0.9)
    b = NoisyFloat(value=2.0, uncertainty=0.1, confidence=0.85)
    z = a + b
    assert z.uncertainty >= max(a.uncertainty, b.uncertainty)
    assert math.isclose(z.uncertainty, math.sqrt(0.3**2 + 0.1**2), rel_tol=1e-9)


def test_op_2_confidence_nonincreasing():
    """OP-2: confidence ≤ min(c_a, c_b)."""
    a = NoisyFloat(5.0, 0.3, 0.9)
    b = NoisyFloat(2.0, 0.1, 0.85)
    assert (a + b).confidence <= min(a.confidence, b.confidence)
    assert (a - b).confidence <= min(a.confidence, b.confidence)


def test_op_3_value_exact():
    """OP-3: значение точно (в пределах float precision)."""
    a = NoisyFloat(5.0, 0.3, 0.9)
    b = NoisyFloat(2.0, 0.1, 0.85)
    assert (a + b).value == 7.0
    assert (a - b).value == 3.0


def test_op_4_mul_uncertainty_formula():
    """OP-4: σ_z = √(b²·σ_a² + a²·σ_b²)."""
    a = NoisyFloat(5.0, 0.3, 0.9)
    b = NoisyFloat(2.0, 0.1, 0.85)
    z = a * b
    expected = math.sqrt((2.0 * 0.3) ** 2 + (5.0 * 0.1) ** 2)
    assert math.isclose(z.uncertainty, expected, rel_tol=1e-9)


def test_op_5_mul_zero_value():
    """OP-5 (спец. 5.2): формула корректна при нулевом значении."""
    a = NoisyFloat(value=0.0, uncertainty=0.5, confidence=0.9)
    b = NoisyFloat(value=3.0, uncertainty=0.1, confidence=0.8)
    z = a * b
    assert z.value == 0.0
    assert math.isclose(z.uncertainty, 3.0 * 0.5, rel_tol=1e-9)
    assert z.confidence == 0.8


def test_op_6_relative_uncertainty_bound():
    """OP-6: σ_rel(z) ≤ σ_rel(a) + σ_rel(b) для a, b ≠ 0."""
    a = NoisyFloat(5.0, 0.3, 0.9)
    b = NoisyFloat(2.0, 0.1, 0.85)
    z = a * b
    rel = lambda n: n.uncertainty / abs(n.value)
    assert rel(z) <= rel(a) + rel(b) + 1e-12


def test_op_7_div_uncertainty_formula():
    """OP-7: σ_z = √((σ_a/b)² + (a·σ_b/b²)²)."""
    a = NoisyFloat(5.0, 0.3, 0.9)
    b = NoisyFloat(2.0, 0.1, 0.85)
    z = a / b
    expected = math.sqrt((0.3 / 2.0) ** 2 + (5.0 * 0.1 / 4.0) ** 2)
    assert math.isclose(z.uncertainty, expected, rel_tol=1e-9)


def test_op_8_division_by_near_zero():
    """OP-8: деление на near-zero → ZeroDivisionError."""
    a = NoisyFloat(5.0, 0.3, 0.9)
    b = NoisyFloat(0.0, 0.1, 0.85)
    with pytest.raises(ZeroDivisionError):
        a / b
