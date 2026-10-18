"""FlowingTrit: промежуточные float допустимы, диапазон не клампится."""

from transflux import FlowingTrit, FluxVar


def test_intermediate_float_is_a_real_state():
    """-0.5 — значение, а не округление к {-1, 0, +1}."""
    trit = FlowingTrit(-0.5)
    assert trit.value == -0.5
    assert float(trit) == -0.5


def test_value_outside_poles_is_not_clamped():
    """Проверки диапазона нет: вышедшее за полюса значение остаётся как есть."""
    trit = FlowingTrit(1.7)
    assert trit.value == 1.7
    assert float(trit) == 1.7


def test_nearest_pole_does_not_change_value():
    trit = FlowingTrit(-0.2)
    assert trit.nearest_pole() == 0.0
    assert trit.value == -0.2


def test_flowing_trit_moves_inside_flux_var():
    """Трит течёт как обычное состояние: velocity считается по float."""
    flux = FluxVar(value=FlowingTrit(0.0))
    flux.flow(FlowingTrit(-0.5), dt=1.0)
    assert flux.value == FlowingTrit(-0.5)
    assert flux.velocity == -0.5
    assert flux.trajectory()[0] == FlowingTrit(0.0)


def test_flow_matches_update():
    flux = FluxVar(value=1.0)
    flux.flow(4.0, dt=1.0)
    assert flux.value == 4.0
    assert flux.velocity == 3.0
