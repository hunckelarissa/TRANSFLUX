"""Полифоническая идентичность и стирание старого имени.

Производная оси Survival. Не часть SurvivalState: panic сам по себе
маски не крутит и не стирает (DR-023).
"""

import weakref
from dataclasses import dataclass, field
from typing import List, Optional

from .survival import _new_hash

# Живые книги без явной регистрации (DR-030). Weak-ссылки: мёртвые исчезают.
_LIVE_BOOKS: List[weakref.ref] = []


def _register_live(book: "PolyphonicIdentity") -> None:
    _LIVE_BOOKS.append(weakref.ref(book))


def _sweep_live() -> List["PolyphonicIdentity"]:
    alive_refs = []
    books = []
    for ref in _LIVE_BOOKS:
        book = ref()
        if book is not None:
            alive_refs.append(ref)
            books.append(book)
    _LIVE_BOOKS[:] = alive_refs
    return books


@dataclass
class PolyphonicIdentity:
    """Несколько масок одной сущности. Слои не раскрывают друг друга."""

    _slots: dict = field(default_factory=dict)
    _groups: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        _register_live(self)

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

    @classmethod
    def live(cls) -> List["PolyphonicIdentity"]:
        """Все ещё достижимые книги процесса (weak-registry)."""
        return _sweep_live()

    @classmethod
    def erase_live(cls, old_hash: str) -> str:
        """Стереть old_hash во всех живых книгах, где он есть, одним новым.

        Явный opt-in на автопоиск (DR-030). Нет ни одной книги с хешем —
        KeyError, ничего не меняется.
        """
        targets = [book for book in _sweep_live() if book._contains(old_hash)]
        if not targets:
            raise KeyError(old_hash)
        new_hash = _new_hash()
        for book in targets:
            book._rewrite(old_hash, new_hash)
        return new_hash

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


@dataclass
class IdentityLedger:
    """Несколько книг масок. Стирание по зарегистрированным и, по запросу, по живым.

    Книга, которую не зарегистрировали, невидима для обычного erase.
    `erase(..., discovered=True)` и `PolyphonicIdentity.erase_live` видят
    все живые экземпляры (DR-030).
    Один и тот же old_hash во всех книгах получает один new_hash.
    """

    _books: dict = field(default_factory=dict)

    def register(
        self,
        name: str,
        book: Optional[PolyphonicIdentity] = None,
    ) -> PolyphonicIdentity:
        """Добавить книгу под именем. Повтор имени — ValueError."""
        if name in self._books:
            raise ValueError(f"book already registered: {name}")
        if book is None:
            book = PolyphonicIdentity()
        self._books[name] = book
        return book

    def book(self, name: str) -> PolyphonicIdentity:
        """Книга по имени. Нет имени — KeyError."""
        return self._books[name]

    def names(self) -> list:
        """Имена зарегистрированных книг в порядке добавления."""
        return list(self._books.keys())

    def holds(self, identity_hash: str) -> bool:
        """Есть ли хеш хотя бы в одной зарегистрированной книге."""
        return any(book._contains(identity_hash) for book in self._books.values())

    def erase(self, old_hash: str, *, discovered: bool = False) -> str:
        """Заменить old_hash одним новым.

        По умолчанию — только зарегистрированные книги.
        `discovered=True` — ещё и все живые PolyphonicIdentity процесса.
        Ни одна цель не содержит хеш — KeyError, ничего не меняется.
        """
        targets = [
            book for book in self._books.values() if book._contains(old_hash)
        ]
        if discovered:
            seen = {id(book) for book in targets}
            for book in PolyphonicIdentity.live():
                if id(book) not in seen and book._contains(old_hash):
                    targets.append(book)
        if not targets:
            raise KeyError(old_hash)
        new_hash = _new_hash()
        for book in targets:
            book._rewrite(old_hash, new_hash)
        return new_hash

    def rotate_all(self) -> dict:
        """rotate_all в каждой книге. Словарь: имя книги → её mapping."""
        return {name: book.rotate_all() for name, book in self._books.items()}
