"""Автопоиск живых PolyphonicIdentity без регистрации (DR-030)."""

import gc

import pytest

from transflux import IdentityLedger, PolyphonicIdentity


def test_live_lists_reachable_books_and_drops_garbage():
    kept = PolyphonicIdentity()
    kept.add("public")
    orphan = PolyphonicIdentity()
    orphan.add("ghost")
    orphan_id = id(orphan)
    assert id(kept) in {id(book) for book in PolyphonicIdentity.live()}
    assert orphan_id in {id(book) for book in PolyphonicIdentity.live()}

    del orphan
    gc.collect()

    live_ids = {id(book) for book in PolyphonicIdentity.live()}
    assert id(kept) in live_ids
    assert orphan_id not in live_ids


def test_erase_live_rewrites_unregistered_books():
    desk = PolyphonicIdentity()
    field = PolyphonicIdentity()
    shared = desk.add("byline")
    field._slots["source"] = shared

    new = PolyphonicIdentity.erase_live(shared)

    assert desk.present("byline") == new
    assert field.present("source") == new
    assert desk.holds(shared) is False


def test_ledger_discovered_reaches_outside_register():
    ledger = IdentityLedger()
    seen = ledger.register("desk")
    hidden = PolyphonicIdentity()
    shared = seen.add("public")
    hidden._slots["ghost"] = shared

    new = ledger.erase(shared, discovered=True)
    assert seen.present("public") == new
    assert hidden.present("ghost") == new


def test_erase_live_unknown_hash_is_keyerror():
    book = PolyphonicIdentity()
    book.add("public")
    with pytest.raises(KeyError):
        PolyphonicIdentity.erase_live("no-such-hash")
