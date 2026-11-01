"""Ось III — Survival Model: SurvivalState.

Модель выживания: непрерывная угроза → дискретное перерождение.
Приоритет: выживание > целостность данных > скорость.

Спецификация: docs/en/TRANSFLUX_Specification.md, §3
(русская пара: docs/ru/TRANSFLUX_Specification.md).
"""

import hashlib
import os
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Literal, Optional

if TYPE_CHECKING:
    from .flux_var import FluxVar
    from .noisy_float import NoisyFloat

ScopeType = Literal["local", "process", "system"]


def _new_hash() -> str:
    """Генерация нового идентификатора (криптографически случайного)."""
    return hashlib.sha256(
        os.urandom(32) + str(time.time_ns()).encode()
    ).hexdigest()


@dataclass
class SurvivalState:
    """Модель выживания: непрерывная угроза → дискретное перерождение."""

    threat_level: float = 0.0           # [0.0, 1.0]
    panic_threshold: float = 0.75
    fallback: Any = None                # безопасное состояние для отката
    scope: ScopeType = "local"
    identity_hash: str = field(
        default_factory=lambda: _new_hash()
    )
    decay_rate: float = 0.0             # затухание threat за цикл
    on_panic: Optional[Callable] = field(default=None, repr=False)
    on_panic_local: Optional[Callable] = field(default=None, repr=False)
    on_panic_process: Optional[Callable] = field(default=None, repr=False)
    on_panic_system: Optional[Callable] = field(default=None, repr=False)
    peak_threat: float = 0.0           # уровень до сброса panic в этом update
    _panic_count: int = field(default=0, repr=False)

    def update(self, threat_delta: float) -> bool:
        """
        Обновить уровень угрозы.
        Применяет decay_rate (затухание) перед добавлением новой угрозы.
        Возвращает True, если был вызван panic.
        """
        self.peak_threat = max(0.0, min(1.0,
            self.threat_level - self.decay_rate + threat_delta
        ))
        self.threat_level = self.peak_threat
        if self.threat_level >= self.panic_threshold:
            self._panic()
            return True
        return False

    def update_from_uncertainty(self,
                                noisy: "NoisyFloat",
                                sensitivity: float = 0.5):
        """
        Связь с Value Model:
        низкий confidence генерирует угрозу.

        threat_delta = (1 - confidence) × sensitivity
        """
        threat = (1.0 - noisy.confidence) * sensitivity
        return self.update(threat_delta=threat)

    def update_from_flow(self,
                         flux: "FluxVar",
                         sensitivity: float = 0.1):
        """
        Связь со State Model:
        резкая velocity генерирует угрозу.

        threat_delta = min(1.0, |velocity| × sensitivity)
        """
        threat = min(1.0, abs(flux.velocity) * sensitivity)
        return self.update(threat_delta=threat)

    def _panic(self):
        """
        Детерминированный фазовый переход: перерождение идентичности.

        1. Инкремент счётчика panic.
        2. Генерация нового identity_hash.
        3. Сброс threat_level в 0.
        4. Общий on_panic, затем scope-хук (Consent-First: хуки опциональны):
           - local → on_panic_local;
           - process → on_panic_process;
           - system → on_panic_system.
        """
        self._panic_count += 1
        old_hash = self.identity_hash
        self.identity_hash = _new_hash()
        self.threat_level = 0.0
        if self.on_panic:
            self.on_panic(self, old_hash)
        scope_hook = {
            "local": self.on_panic_local,
            "process": self.on_panic_process,
            "system": self.on_panic_system,
        }.get(self.scope)
        if scope_hook:
            scope_hook(self, old_hash)
        return self.fallback

    def is_safe(self) -> bool:
        """Уровень угрозы значительно ниже порога."""
        return self.threat_level < self.panic_threshold * 0.5


def stale_threat(
    elapsed: float,
    timeout: float,
    sensitivity: float = 1.0,
) -> float:
    """Угроза от долгого отсутствия сигнала.

    Пока elapsed < timeout — 0. Дальше растёт как
    ((elapsed − timeout) / timeout) × sensitivity, верх — 1.0.
    """
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    if elapsed < timeout:
        return 0.0
    return min(1.0, ((elapsed - timeout) / timeout) * sensitivity)


def uncertainty_margin_threat(
    noisy: "NoisyFloat",
    max_uncertainty: float,
    sensitivity: float = 1.0,
) -> float:
    """Угроза, когда σ выше допустимого запаса.

    Пока uncertainty ≤ max_uncertainty — 0. Дальше растёт как
    ((σ − margin) / margin) × sensitivity при margin > 0;
    при margin = 0 любой положительный σ даёт sensitivity (клип в 1.0).
    """
    if max_uncertainty < 0:
        raise ValueError("max_uncertainty must be non-negative")
    if noisy.uncertainty <= max_uncertainty:
        return 0.0
    if max_uncertainty == 0.0:
        return min(1.0, sensitivity)
    excess = noisy.uncertainty - max_uncertainty
    return min(1.0, (excess / max_uncertainty) * sensitivity)
