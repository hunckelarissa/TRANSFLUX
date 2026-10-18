"""Ось I — State Model: FluxVar<T>.

Переменная как русло: значение в движении, с историей, инерцией
и комфортом текущего состояния.

Спецификация: docs/TRANSFLUX_Specification_v0.3.md, §1.
"""

from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Generic, List, Literal, Optional, Sequence, TypeVar

T = TypeVar("T")


@dataclass
class FluxVar(Generic[T]):
    """Переменная как русло: значение в движении."""

    value: T
    velocity: float = 0.0            # скорость изменения
    acceleration: float = 0.0        # ускорение
    comfort: float = 0.0             # [-1.0, +1.0]: дисфория ↔ эйфория
    history: deque = field(
        default_factory=lambda: deque(maxlen=32)
    )
    trauma_threshold: float = 10.0
    on_trauma: Optional[Callable] = field(default=None, repr=False)
    # Слоя constraints нет намеренно: допустимость value задаёт вызывающий код.

    def update(self, new_value: T, dt: float = 1.0) -> "FluxVar[T]":
        """Обновить состояние с учётом инерции."""
        if dt <= 0:
            raise ValueError("dt must be positive")

        delta = float(new_value) - float(self.value)
        new_velocity = delta / dt

        if abs(new_velocity) > self.trauma_threshold:
            self._handle_trauma(new_velocity)

        self.acceleration = (new_velocity - self.velocity) / dt
        self.velocity = new_velocity
        self.history.append(self.value)
        self.value = new_value
        self.comfort = max(-1.0, min(1.0, self.comfort))
        return self

    def _handle_trauma(self, velocity: float):
        """
        Резкий скачок — сигнал, не фатал.

        Реализация определяется через callback on_trauma.
        Стратегии реакции на травму (не исчерпывающий список):
        - предупреждение (логирование);
        - смягчение (ограничение скорости, адаптивный шаг);
        - эскалация (передача сигнала в SurvivalState).
        """
        if self.on_trauma:
            self.on_trauma(self, velocity)

    def flow(self, new_value: T, dt: float = 1.0) -> "FluxVar[T]":
        """Течение к новому значению — Python-форма оператора `~>`.

        То же самое, что `update`. Синтаксис `~>` и отдельный DSL отложены:
        в библиотеке намерение парадигмы выражается этим методом.
        """
        return self.update(new_value, dt)

    def trajectory(self) -> List[T]:
        """Полная траектория: история + текущее значение."""
        return list(self.history) + [self.value]


JumpKind = Literal["calm", "alone", "shared"]


def classify_jump(sensor: "FluxVar", neighbors: Sequence["FluxVar"]) -> JumpKind:
    """Один датчик дёрнулся или вместе с соседями.

    «Дёрнулся» значит то же, что травма: |velocity| строго выше своего
    trauma_threshold. Сосед из списка, который есть сам sensor, не считается.
    Пустое соседство и скачок — alone: подтверждения нет.

    Функция ничего не меняет. Снизить confidence или поднять угрозу
    решает вызывающий код (DR-022).
    """
    if abs(sensor.velocity) <= sensor.trauma_threshold:
        return "calm"
    peers = [peer for peer in neighbors if peer is not sensor]
    if any(abs(peer.velocity) > peer.trauma_threshold for peer in peers):
        return "shared"
    return "alone"
