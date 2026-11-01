"""Scar Memory — память мест, где уже было больно.

Производная оси Survival. Не часть SurvivalState: panic сам шрам не ставит
(Consent-First). Вызывающий код помечает site в callback и дальше усиливает
чувствительность через amplify.
"""

from dataclasses import dataclass, field


@dataclass
class ScarMemory:
    """Шрамы по именованным местам. Усиливают последующие проверки."""

    boost_factor: float = 1.0
    max_scar: float = 1.0
    _scars: dict = field(default_factory=dict)

    def mark(self, site: str, amount: float = 0.25) -> float:
        """Накопить шрам в site. Возвращает новую интенсивность."""
        if amount < 0:
            raise ValueError("amount must be non-negative")
        if self.max_scar < 0:
            raise ValueError("max_scar must be non-negative")
        intensity = min(self.max_scar, self._scars.get(site, 0.0) + amount)
        self._scars[site] = intensity
        return intensity

    def intensity(self, site: str) -> float:
        """Текущая глубина шрама. Неизвестное место — 0."""
        return self._scars.get(site, 0.0)

    def sites(self) -> list:
        """Места с ненулевым шрамом."""
        return [site for site, value in self._scars.items() if value > 0.0]

    def amplify(self, site: str, base: float) -> float:
        """base × (1 + boost_factor × intensity(site))."""
        return base * (1.0 + self.boost_factor * self.intensity(site))

    def fade(self, amount: float = 0.05) -> None:
        """Снять одинаковый слой со всех шрамов. Нулевые исчезают."""
        if amount < 0:
            raise ValueError("amount must be non-negative")
        updated = {}
        for site, value in self._scars.items():
            left = value - amount
            if left > 0.0:
                updated[site] = left
        self._scars = updated
