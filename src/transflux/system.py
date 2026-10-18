"""Оркестрация трёх осей: TransfluxSystem.

Явный цикл связи State, Value и Survival. Примитивы по-прежнему не знают
друг о друге (DR-014). См. Coupling Protocol, спецификация §4.2.
"""

from dataclasses import dataclass
from typing import Any, Optional

from .flux_var import FluxVar
from .noisy_float import NoisyFloat
from .survival import SurvivalState


@dataclass
class TransfluxSystem:
    """Оркестратор: один цикл, в котором три оси связаны."""

    state: FluxVar
    survival: SurvivalState
    flow_sensitivity: float = 0.1
    uncertainty_sensitivity: float = 0.5
    value: Optional[NoisyFloat] = None
    ticks: int = 0
    peak_threat: float = 0.0
    backup_value: Any = None
    backup_noisy: Optional[NoisyFloat] = None
    degraded: bool = False

    def tick(self, new_value, noisy_value: NoisyFloat, dt: float = 1.0) -> bool:
        """Один цикл обновления всех осей.

        Порядок фиксирован:
        1. Если включён запасной режим — вход подменяется на backup.
        2. State течёт к new_value.
        3. Value запоминается как последнее наблюдение.
        4. Резкая velocity повышает угрозу.
        5. Низкий confidence повышает угрозу.
        6. Если случился panic и задан fallback — state течёт к нему.
        7. Если panic и запасная пара задана — режим остаётся включённым.

        Возвращает True, если на этом цикле был panic.
        """
        if self.degraded and self.backup_armed():
            new_value = self.backup_value
            noisy_value = self.backup_noisy

        self.ticks += 1
        self.state.flow(new_value, dt)
        self.value = noisy_value

        panicked = False
        panicked |= self.survival.update_from_flow(
            self.state, self.flow_sensitivity
        )
        flow_peak = self.survival.peak_threat
        panicked |= self.survival.update_from_uncertainty(
            noisy_value, self.uncertainty_sensitivity
        )
        self.peak_threat = max(flow_peak, self.survival.peak_threat)

        if panicked and self.survival.fallback is not None:
            self.state.flow(self.survival.fallback, dt)
        if panicked and self.backup_armed():
            self.degraded = True

        return panicked

    def backup_armed(self) -> bool:
        """Запасной режим можно удержать только если заданы и значение, и наблюдение."""
        return self.backup_value is not None and self.backup_noisy is not None

    def recover(self) -> None:
        """Снять запасной режим. Дальше tick снова слушает свой вход."""
        self.degraded = False
