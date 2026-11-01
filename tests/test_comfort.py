"""Comfort реагирует на trauma и на спокойный шаг (DR-024)."""

from transflux import FluxVar


def test_trauma_lowers_comfort():
    flux = FluxVar(value=0.0, trauma_threshold=1.0, comfort=0.0)
    flux.flow(5.0)
    assert flux.comfort == -0.25


def test_calm_raises_comfort():
    flux = FluxVar(value=0.0, trauma_threshold=10.0, comfort=0.0)
    flux.flow(0.5)
    assert flux.comfort == 0.02


def test_comfort_stays_bounded_under_repeated_trauma():
    flux = FluxVar(
        value=0.0,
        trauma_threshold=0.1,
        comfort=0.0,
        trauma_comfort_cost=0.5,
    )
    for step in range(10):
        flux.flow(float(step + 1) * 10.0)
    assert flux.comfort == -1.0


def test_zero_rates_keep_legacy_freeze():
    """Стоимость и прирост 0 — comfort только клипится, как раньше."""
    flux = FluxVar(
        value=36.6,
        trauma_threshold=1.0,
        comfort=0.0,
        trauma_comfort_cost=0.0,
        calm_comfort_gain=0.0,
    )
    flux.flow(40.2)
    assert flux.comfort == 0.0
