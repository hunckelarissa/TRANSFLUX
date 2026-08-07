"""Ось II — Value Model: NoisyFloat.

Значение как распределение: центр, неуверенность и степень доверия.
Шум — не ошибка. Шум — сигнал о природе знания.

Спецификация: docs/TRANSFLUX_Specification_v0.3.md, §2.
"""

import math
from dataclasses import dataclass


@dataclass
class NoisyFloat:
    """Значение как распределение: центр, неуверенность, доверие."""

    value: float                  # центр распределения (mean)
    uncertainty: float = 0.0      # стандартное отклонение (σ)
    confidence: float = 1.0       # [0.0, 1.0]: степень доверия

    # --- Арифметика с propagation of uncertainty ---
    # Формулы основаны на линейном приближении (first-order Taylor).
    # Confidence propagation: min (консервативная стратегия).
    # Альтернативы (мультипликативная, байесовская) — предмет расширения.

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
        new_value = self.value * other.value
        new_uncertainty = math.sqrt(
            (other.value * self.uncertainty) ** 2 +
            (self.value * other.uncertainty) ** 2
        )
        return NoisyFloat(
            value=new_value,
            uncertainty=new_uncertainty,
            confidence=min(self.confidence, other.confidence)
        )

    def __truediv__(self, other: "NoisyFloat") -> "NoisyFloat":
        """
        Для z = a/b:
            σ_z = √( (σ_a/b)²  +  (a·σ_b/b²)² )

        Требует other.value ≠ 0.
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
