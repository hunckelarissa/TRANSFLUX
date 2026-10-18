"""FlowingTrit — непрерывный трит (производная оси State).

Полюса -1, 0 и +1 задают смысл: отрицание, порог, утверждение.
Само состояние — число с плавающей точкой. -0.5 — обычное значение,
а не ошибка и не «ещё не доехавшее» до дискретной метки.

Диапазон не проверяется. Значение вне [-1, 1] остаётся как есть:
это ответственность вызывающего кода (DR-017, DR-018).
"""

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class FlowingTrit:
    """Непрерывное троичное состояние. Промежуточные float допустимы."""

    NEGATIVE: ClassVar[float] = -1.0
    LIMINAL: ClassVar[float] = 0.0
    POSITIVE: ClassVar[float] = 1.0

    value: float

    def __float__(self) -> float:
        return float(self.value)

    def nearest_pole(self) -> float:
        """Ближайший полюс из {-1, 0, +1}.

        Подсказка для чтения состояния. Значение при этом не меняется.
        При равном расстоянии побеждает более ранний полюс: -1, затем 0, затем +1.
        """
        poles = (self.NEGATIVE, self.LIMINAL, self.POSITIVE)
        return min(poles, key=lambda pole: abs(pole - float(self.value)))
