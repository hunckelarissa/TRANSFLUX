"""Маски одной сущности и стирание старого имени."""

import pytest

from transflux import PolyphonicIdentity, SurvivalState


def test_three_roles_do_not_reveal_each_other():
    book = PolyphonicIdentity()
    for role in ("public", "desk", "source"):
        book.add(role)
    book.grant("desk", "accredited")

    shown = [book.present(role) for role in ("public", "desk", "source")]
    assert len(set(shown)) == 3
    assert book.in_group("accredited") is True
    assert book.in_group("missing") is False


def test_duplicate_role_is_rejected():
    book = PolyphonicIdentity()
    book.add("public")
    with pytest.raises(ValueError):
        book.add("public")


def test_erase_replaces_every_reference_and_keeps_membership():
    book = PolyphonicIdentity()
    book.add("desk")
    book.alias("badge", "desk")
    book.grant("desk", "accredited")
    old = book.present("desk")

    new = book.erase(old)

    assert new != old
    assert book.present("desk") == new
    assert book.present("badge") == new
    assert book.holds(old) is False
    assert book.in_group("accredited") is True


def test_unknown_hash_is_not_erased():
    book = PolyphonicIdentity()
    book.add("public")
    before = book.present("public")
    with pytest.raises(KeyError):
        book.erase("no-such-hash")
    assert book.present("public") == before


def test_panic_rotates_masks_only_through_the_callback():
    """Книга, которую не передали в on_panic, остаётся при своих именах."""
    book = PolyphonicIdentity()
    for role in ("public", "desk", "source"):
        book.add(role)
    book.grant("desk", "accredited")
    shown = {role: book.present(role) for role in ("public", "desk", "source")}

    other = PolyphonicIdentity()
    other.add("public")
    kept = other.present("public")

    survival = SurvivalState(
        panic_threshold=0.5,
        on_panic=lambda state, old_hash: book.rotate_all(),
    )
    assert survival.update(1.0) is True

    assert book.in_group("accredited") is True
    assert all(book.present(role) != old for role, old in shown.items())
    assert not any(book.holds(old) for old in shown.values())
    assert other.present("public") == kept
    assert other.holds(kept) is True


def test_rotate_all_on_an_empty_book():
    assert PolyphonicIdentity().rotate_all() == {}
