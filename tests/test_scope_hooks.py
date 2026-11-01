"""Scope-хуки вызываются только для текущего scope (DR-025)."""

from transflux import SurvivalState


def test_only_matching_scope_hook_runs():
    seen = []
    survival = SurvivalState(
        panic_threshold=0.5,
        scope="process",
        on_panic=lambda s, old: seen.append(("general", s.scope)),
        on_panic_local=lambda s, old: seen.append("local"),
        on_panic_process=lambda s, old: seen.append("process"),
        on_panic_system=lambda s, old: seen.append("system"),
    )
    assert survival.update(0.6) is True
    assert seen == [("general", "process"), "process"]


def test_missing_scope_hook_is_silent():
    survival = SurvivalState(panic_threshold=0.5, scope="system")
    assert survival.update(0.6) is True
    assert survival._panic_count == 1
