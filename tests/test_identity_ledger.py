"""IdentityLedger: стирание хеша сразу в нескольких книгах."""

import pytest

from transflux import IdentityLedger, PolyphonicIdentity


def test_erase_rewrites_every_registered_book_with_one_hash():
    ledger = IdentityLedger()
    desk = ledger.register("desk")
    field = ledger.register("field")
    shared = desk.add("public")
    field._slots["mirror"] = shared
    field.grant("mirror", "watchers")
    alone = field.add("local")

    new = ledger.erase(shared)

    assert new != shared
    assert desk.present("public") == new
    assert field.present("mirror") == new
    assert field.present("local") == alone
    assert ledger.holds(shared) is False
    assert field.in_group("watchers") is True


def test_unregistered_book_is_invisible_to_erase():
    ledger = IdentityLedger()
    seen = ledger.register("seen")
    hidden = PolyphonicIdentity()
    shared = seen.add("public")
    hidden._slots["ghost"] = shared

    ledger.erase(shared)

    assert seen.holds(shared) is False
    assert hidden.present("ghost") == shared


def test_unknown_hash_raises_and_changes_nothing():
    ledger = IdentityLedger()
    book = ledger.register("only")
    kept = book.add("public")
    with pytest.raises(KeyError):
        ledger.erase("missing")
    assert book.present("public") == kept


def test_duplicate_register_is_rejected():
    ledger = IdentityLedger()
    ledger.register("desk")
    with pytest.raises(ValueError):
        ledger.register("desk")


def test_rotate_all_returns_per_book_mappings():
    ledger = IdentityLedger()
    a = ledger.register("a")
    b = ledger.register("b")
    old_a = a.add("public")
    old_b = b.add("public")

    mapping = ledger.rotate_all()

    assert set(mapping) == {"a", "b"}
    assert mapping["a"][old_a] != old_a
    assert mapping["b"][old_b] != old_b
    assert a.present("public") == mapping["a"][old_a]
    assert b.present("public") == mapping["b"][old_b]
