"""Оркестрация трёх осей: TransfluxSystem.

Рекомендуемый паттерн (не обязательный компонент ядра) — см. Coupling
Protocol в docs/TRANSFLUX_Specification_v0.2.md, §4.2 и DR-014.
"""

from dataclasses import dataclass

from .flux_var import FluxVar
from .noisy_float import NoisyFloat
from .survival import SurvivalState


@dataclass
class TransfluxSystem:
    """Минимальный orchestrator: один цикл обновления всех осей."""

    state: FluxVar
    survival: SurvivalState
    flow_sensitivity: float = 0.1
    uncertainty_sensitivity: float = 0.5

    def tick(self, new_value, noisy_value: NoisyFloat, dt: float = 1.0):
        """Один цикл обновления всех осей."""
        self.state.update(new_value, dt)

        panicked = False
        panicked |= self.survival.update_from_flow(
            self.state, self.flow_sensitivity
        )
        panicked |= self.survival.update_from_uncertainty(
            noisy_value, self.uncertainty_sensitivity
        )

        if panicked and self.survival.fallback is not None:
            self.state.update(self.survival.fallback, dt)

        return panicked
