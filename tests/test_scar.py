"""ScarMemory: шрам усиливает чувствительность, fade снимает слой."""

import pytest

from transflux import ScarMemory


def test_mark_accumulates_up_to_max():
    scars = ScarMemory(max_scar=0.5)
    assert scars.mark("ward.fever", 0.3) == pytest.approx(0.3)
    assert scars.mark("ward.fever", 0.3) == pytest.approx(0.5)
    assert scars.intensity("ward.fever") == pytest.approx(0.5)
    assert scars.sites() == ["ward.fever"]


def test_amplify_scales_base_sensitivity():
    scars = ScarMemory(boost_factor=2.0)
    scars.mark("drone.gps", 0.5)
    assert scars.amplify("drone.gps", base=0.1) == pytest.approx(0.2)
    assert scars.amplify("unknown", base=0.1) == pytest.approx(0.1)


def test_fade_removes_healed_sites():
    scars = ScarMemory()
    scars.mark("a", 0.1)
    scars.mark("b", 0.3)
    scars.fade(0.1)
    assert scars.sites() == ["b"]
    assert scars.intensity("b") == pytest.approx(0.2)


def test_negative_amounts_are_rejected():
    scars = ScarMemory()
    with pytest.raises(ValueError):
        scars.mark("x", -0.1)
    with pytest.raises(ValueError):
        scars.fade(-0.1)
