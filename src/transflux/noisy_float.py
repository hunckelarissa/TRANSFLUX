"""Ось II — Value Model: NoisyFloat.

Значение как распределение: центр, неуверенность и степень доверия.
Шум — не ошибка. Шум — сигнал о природе знания.

Спецификация: docs/en/TRANSFLUX_Specification.md, §2
(русская пара: docs/ru/TRANSFLUX_Specification.md).
"""

import math
from dataclasses import dataclass
from typing import Optional, Sequence


@dataclass
class NoisyFloat:
    """Значение как распределение: центр, неуверенность, доверие."""

    value: float                  # центр распределения (mean)
    uncertainty: float = 0.0      # стандартное отклонение (σ)
    confidence: float = 1.0       # [0.0, 1.0]: степень доверия

    # --- Арифметика с propagation of uncertainty ---
    # Формулы основаны на линейном приближении (first-order Taylor).
    # Confidence propagation: min (слабое звено). Решение зафиксировано:
    # мультипликативная и байесовская стратегии отложены (DR-002, DR-016).

    def __add__(self, other: "NoisyFloat") -> "NoisyFloat":
        """σ_z = √(σ_a² + σ_b²)"""
        return NoisyFloat(
            value=self.value + other.value,
            uncertainty=math.sqrt(self.uncertainty**2 + other.uncertainty**2),
            confidence=min(self.confidence, other.confidence)
        )

    def __sub__(self, other: "NoisyFloat") -> "NoisyFloat":
        """σ_z = √(σ_a² + σ_b²)  (та же формула, что при сложении)"""
        return NoisyFloat(
            value=self.value - other.value,
            uncertainty=math.sqrt(self.uncertainty**2 + other.uncertainty**2),
            confidence=min(self.confidence, other.confidence)
        )

    def __mul__(self, other: "NoisyFloat") -> "NoisyFloat":
        """
        Для z = a·b:
            σ_z = √( b²·σ_a²  +  a²·σ_b² )

        Формула корректна для всех значений, включая нулевые.
        """
        return NoisyFloat(
            value=self.value * other.value,
            uncertainty=math.sqrt(
                (other.value * self.uncertainty) ** 2 +
                (self.value * other.uncertainty) ** 2
            ),
            confidence=min(self.confidence, other.confidence)
        )

    def __truediv__(self, other: "NoisyFloat") -> "NoisyFloat":
        """
        Для z = a/b:
            σ_z = √( (σ_a/b)² + (a·σ_b/b²)² )
        """
        if abs(other.value) < 1e-15:
            raise ZeroDivisionError(
                "Division by NoisyFloat with near-zero value"
            )
        new_value = self.value / other.value
        new_uncertainty = math.sqrt(
            (self.uncertainty / other.value) ** 2 +
            (self.value * other.uncertainty / other.value ** 2) ** 2
        )
        return NoisyFloat(
            value=new_value,
            uncertainty=new_uncertainty,
            confidence=min(self.confidence, other.confidence)
        )

    def __float__(self) -> float:
        """Центр распределения — для velocity в FluxVar / NoisyFlow."""
        return float(self.value)

    def is_reliable(self, min_confidence: float = 0.7) -> bool:
        """Достаточно ли мы уверены в этом значении?"""
        return self.confidence >= min_confidence

    def gradient_of_truth(self) -> float:
        """
        Градиент истинности: степень «правдивости» значения
        как функция соотношения сигнал/шум и доверия.

        - При нулевой неуверенности → confidence.
        - При росте шума → экспоненциально убывает.
        """
        if self.uncertainty == 0:
            return self.confidence
        snr = abs(self.value) / (self.uncertainty + 1e-9)
        return self.confidence * (1 - math.exp(-snr))

    def __repr__(self) -> str:
        return (f"NoisyFloat({self.value:.4f} "
                f"± {self.uncertainty:.4f}, "
                f"conf={self.confidence:.0%})")


def weighted_mean(
    readings: Sequence[NoisyFloat],
    *,
    correlation: float = 0.0,
    covariance: Optional[Sequence[Sequence[float]]] = None,
) -> NoisyFloat:
    """Среднее измерений одной величины. Вес = 1/σ² (или GLS).

    Точный датчик перевешивает шумный: большое uncertainty почти не двигает
    ни значение, ни confidence. Это не арифметика `+` и `/`, где confidence
    берётся как min (DR-016). Здесь confidence — среднее confidence с теми
    же весами (DR-020), с поправкой на correlation / covariance.

    Измерение с σ = 0 забирает весь вес. Если таких несколько и они
    расходятся, uncertainty результата — их среднеквадратичный разброс,
    а confidence — min среди них.

    `correlation` ∈ [0, 1] — средняя попарная корреляция датчиков.
    При 0 формула независима. При росте ρ uncertainty раздувается как
    √(1 + (n−1)·ρ), а confidence тянется к min.

    `covariance` — полная матрица n×n (GLS, DR-029). Диагональ должна
    совпадать с σ_i². Нельзя передавать вместе с correlation ≠ 0.
    С точными (σ = 0) измерениями covariance недопустима (матрица вырождена).

    Пустой список / плохие аргументы — ValueError.
    """
    if not readings:
        raise ValueError("weighted_mean requires at least one reading")
    if not 0.0 <= correlation <= 1.0:
        raise ValueError("correlation must be in [0, 1]")
    if covariance is not None and correlation != 0.0:
        raise ValueError("pass correlation or covariance, not both")

    exact = [reading for reading in readings if reading.uncertainty == 0.0]
    if exact:
        if covariance is not None:
            raise ValueError("covariance cannot be used with exact (σ=0) readings")
        values = [reading.value for reading in exact]
        mean = sum(values) / len(values)
        spread = math.sqrt(sum((value - mean) ** 2 for value in values) / len(values))
        return NoisyFloat(
            value=mean,
            uncertainty=spread,
            confidence=min(reading.confidence for reading in exact),
        )

    if covariance is not None:
        return _weighted_mean_gls(readings, covariance)

    weights = [1.0 / reading.uncertainty ** 2 for reading in readings]
    total = sum(weights)
    n = len(readings)
    independent_sigma = 1.0 / math.sqrt(total)
    uncertainty = independent_sigma * math.sqrt(1.0 + (n - 1) * correlation)
    weighted_confidence = (
        sum(reading.confidence * weight for reading, weight in zip(readings, weights))
        / total
    )
    min_confidence = min(reading.confidence for reading in readings)
    confidence = (
        (1.0 - correlation) * weighted_confidence + correlation * min_confidence
    )
    return NoisyFloat(
        value=sum(reading.value * weight for reading, weight in zip(readings, weights)) / total,
        uncertainty=uncertainty,
        confidence=confidence,
    )


def _weighted_mean_gls(
    readings: Sequence[NoisyFloat],
    covariance: Sequence[Sequence[float]],
) -> NoisyFloat:
    """Обобщённое среднее: μ = (1ᵀΣ⁻¹x)/(1ᵀΣ⁻¹1), σ² = 1/(1ᵀΣ⁻¹1)."""
    n = len(readings)
    matrix = _validate_covariance(readings, covariance)
    ones = [1.0] * n
    values = [reading.value for reading in readings]
    inv_ones = _solve_spd(matrix, ones)
    inv_values = _solve_spd(matrix, values)
    denom = sum(inv_ones)
    if denom <= 0.0:
        raise ValueError("covariance matrix is not usable for a mean")
    mean = sum(inv_values) / denom
    uncertainty = math.sqrt(1.0 / denom)
    weights = [weight / denom for weight in inv_ones]
    weighted_confidence = sum(
        reading.confidence * weight for reading, weight in zip(readings, weights)
    )
    min_confidence = min(reading.confidence for reading in readings)
    avg_rho = _average_correlation(matrix, readings)
    confidence = (1.0 - avg_rho) * weighted_confidence + avg_rho * min_confidence
    return NoisyFloat(value=mean, uncertainty=uncertainty, confidence=confidence)


def _validate_covariance(
    readings: Sequence[NoisyFloat],
    covariance: Sequence[Sequence[float]],
) -> list:
    n = len(readings)
    if len(covariance) != n:
        raise ValueError(f"covariance must be {n}x{n}")
    matrix = []
    for row in covariance:
        if len(row) != n:
            raise ValueError(f"covariance must be {n}x{n}")
        matrix.append([float(cell) for cell in row])
    for i in range(n):
        expected = readings[i].uncertainty ** 2
        if abs(matrix[i][i] - expected) > 1e-9 * max(1.0, expected):
            raise ValueError(
                f"covariance diagonal[{i}] must match uncertainty² "
                f"({expected}), got {matrix[i][i]}"
            )
        for j in range(i + 1, n):
            if abs(matrix[i][j] - matrix[j][i]) > 1e-9:
                raise ValueError("covariance matrix must be symmetric")
    return matrix


def _average_correlation(matrix: Sequence[Sequence[float]], readings: Sequence[NoisyFloat]) -> float:
    n = len(readings)
    if n < 2:
        return 0.0
    total = 0.0
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            denom = readings[i].uncertainty * readings[j].uncertainty
            if denom == 0.0:
                continue
            total += max(0.0, min(1.0, matrix[i][j] / denom))
            count += 1
    return total / count if count else 0.0


def _solve_spd(matrix: Sequence[Sequence[float]], rhs: Sequence[float]) -> list:
    """Решить Σx = b для симметричной положительно определённой Σ (Гаусс)."""
    n = len(rhs)
    a = [row[:] + [float(rhs[i])] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = col
        for row in range(col + 1, n):
            if abs(a[row][col]) > abs(a[pivot][col]):
                pivot = row
        if abs(a[pivot][col]) < 1e-15:
            raise ValueError("covariance matrix is singular or not positive definite")
        a[col], a[pivot] = a[pivot], a[col]
        pivot_val = a[col][col]
        for j in range(col, n + 1):
            a[col][j] /= pivot_val
        for row in range(n):
            if row == col:
                continue
            factor = a[row][col]
            for j in range(col, n + 1):
                a[row][j] -= factor * a[col][j]
    return [a[i][n] for i in range(n)]
