"""Полифоническая идентичность и стирание старого имени.

Производная оси Survival. Не часть SurvivalState: panic сам по себе
маски не крутит и не стирает (DR-023).
"""

from dataclasses import dataclass, field

from .survival import _new_hash


@dataclass
class PolyphonicIdentity:
    """Несколько масок одной сущности. Слои не раскрывают друг друга."""

    _slots: dict = field(default_factory=dict)
    _groups: dict = field(default_factory=dict)

    def add(self, role: str) -> str:
        """Новая маска со своим хешем. Повтор роли — ValueError."""
        if role in self._slots:
            raise ValueError(f"role already exists: {role}")
        self._slots[role] = _new_hash()
        return self._slots[role]

    def alias(self, role: str, source: str) -> str:
        """Вторая ссылка на тот же хеш, что у source."""
        if role in self._slots:
            raise ValueError(f"role already exists: {role}")
        self._slots[role] = self._slots[source]
        return self._slots[role]

    def present(self, role: str) -> str:
        """Хеш, который эта роль показывает наружу."""
        return self._slots[role]

    def grant(self, role: str, group: str) -> None:
        """Текущий хеш роли входит в группу."""
        self._groups.setdefault(group, set()).add(self._slots[role])

    def in_group(self, group: str) -> bool:
        """Есть ли хоть одна живая маска в группе.

        Ответ — да или нет. Какая роль член группы, метод не сообщает.
        """
        members = self._groups.get(group, set())
        return any(mask in members for mask in self._slots.values())

    def holds(self, identity_hash: str) -> bool:
        """Показывает ли какая-нибудь маска этот хеш прямо сейчас."""
        return identity_hash in self._slots.values()

    def erase(self, old_hash: str) -> str:
        """Заменить все ссылки на old_hash одним новым хешем.

        Слоты и членство в группах меняются вместе. После возврата
        старого хеша в книге нет. Неизвестное имя — KeyError, книга не меняется.
        """
        if not self._contains(old_hash):
            raise KeyError(old_hash)
        new_hash = _new_hash()
        self._rewrite(old_hash, new_hash)
        return new_hash

    def rotate_all(self) -> dict:
        """Каждый различный хеш заменить новым. Старых в книге не остаётся.

        Возвращает соответствие старый → новый. Пустая книга — пустой словарь.
        """
        mapping = {old: _new_hash() for old in set(self._slots.values())}
        for old_hash, new_hash in mapping.items():
            self._rewrite(old_hash, new_hash)
        return mapping

    def _contains(self, identity_hash: str) -> bool:
        if identity_hash in self._slots.values():
            return True
        return any(identity_hash in members for members in self._groups.values())

    def _rewrite(self, old_hash: str, new_hash: str) -> None:
        self._slots = {
            role: new_hash if value == old_hash else value
            for role, value in self._slots.items()
        }
        self._groups = {
            group: {
                new_hash if value == old_hash else value
                for value in members
            }
            for group, members in self._groups.items()
        }
