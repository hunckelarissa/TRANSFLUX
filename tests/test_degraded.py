"""Запасной режим оркестратора: удерживается только если его заранее задали."""

from transflux import FluxVar, NoisyFloat, SurvivalState, TransfluxSystem


def _system(backup: bool) -> TransfluxSystem:
    system = TransfluxSystem(
        state=FluxVar(value=0.0, trauma_threshold=1000.0),
        survival=SurvivalState(panic_threshold=0.5, fallback=0.0, decay_rate=0.0),
        flow_sensitivity=0.0,
        uncertainty_sensitivity=1.0,
    )
    if backup:
        system.backup_value = 1.0
        system.backup_noisy = NoisyFloat(1.0, uncertainty=0.1, confidence=0.95)
    return system


def test_without_backup_each_bad_reading_can_panic_again():
    system = _system(backup=False)
    assert system.tick(5.0, NoisyFloat(5.0, 0.1, confidence=0.2)) is True
    assert system.degraded is False
    assert system.tick(9.0, NoisyFloat(9.0, 0.1, confidence=0.1)) is True
    assert system.survival._panic_count == 2
    assert system.state.value == 0.0


def test_armed_backup_latches_until_recover():
    system = _system(backup=True)
    bad = NoisyFloat(9.0, uncertainty=0.1, confidence=0.1)

    assert system.tick(5.0, NoisyFloat(5.0, 0.1, confidence=0.2)) is True
    assert system.degraded is True
    assert system.state.value == 0.0

    assert system.tick(9.0, bad) is False
    assert system.state.value == 1.0
    assert system.value.confidence == 0.95
    assert system.tick(9.0, bad) is False
    assert system.survival._panic_count == 1

    system.recover()
    assert system.degraded is False
    assert system.tick(9.0, bad) is True
    assert system.survival._panic_count == 2
    assert system.degraded is True
