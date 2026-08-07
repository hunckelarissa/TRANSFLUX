"""Тесты свойств связанной системы (CP-*) из docs/TRANSFLUX_Formal_Invariants.md, §3."""

from transflux import FluxVar, NoisyFloat, SurvivalState, TransfluxSystem


def test_cp_1_uncertainty_generates_nonnegative_threat():
    """CP-1 (спец. 5.4): низкий confidence порождает больший threat."""
    reliable = NoisyFloat(5.0, 0.1, confidence=0.95)
    unreliable = NoisyFloat(5.0, 0.1, confidence=0.3)

    s1 = SurvivalState()
    s1.update_from_uncertainty(reliable, sensitivity=0.5)
    s2 = SurvivalState()
    s2.update_from_uncertainty(unreliable, sensitivity=0.5)

    assert s1.threat_level >= 0.0
    assert s2.threat_level > s1.threat_level
    assert abs(s1.threat_level - 0.025) < 1e-9
    assert abs(s2.threat_level - 0.35) < 1e-9


def test_cp_2_velocity_generates_nonnegative_threat():
    """CP-2: threat_delta ≥ 0 при sensitivity ≥ 0."""
    flux = FluxVar(value=0.0)
    flux.update(5.0)
    s = SurvivalState()
    s.update_from_flow(flux, sensitivity=0.1)
    assert s.threat_level >= 0.0


def test_cp_3_panic_leads_to_safe_state():
    """CP-3: после panic threat_level == 0 и identity изменён."""
    s = SurvivalState(panic_threshold=0.5)
    initial = s.identity_hash
    panicked = s.update(threat_delta=0.9)
    assert panicked
    assert s.threat_level == 0.0
    assert s.identity_hash != initial


def test_cp_4_higher_confidence_lower_threat():
    """CP-4: выше confidence → меньший threat_delta."""
    a = NoisyFloat(5.0, 0.1, confidence=0.9)
    b = NoisyFloat(5.0, 0.1, confidence=0.4)
    sa, sb = SurvivalState(), SurvivalState()
    sa.update_from_uncertainty(a, sensitivity=0.5)
    sb.update_from_uncertainty(b, sensitivity=0.5)
    assert sa.threat_level < sb.threat_level


def test_cp_5_lower_velocity_lower_threat():
    """CP-5: меньше |velocity| → меньший threat_delta."""
    slow, fast = FluxVar(value=0.0), FluxVar(value=0.0)
    slow.update(1.0)
    fast.update(5.0)
    s_slow, s_fast = SurvivalState(), SurvivalState()
    s_slow.update_from_flow(slow, sensitivity=0.1)
    s_fast.update_from_flow(fast, sensitivity=0.1)
    assert s_slow.threat_level < s_fast.threat_level


def test_transflux_system_panic_resets_to_fallback():
    """Coupling Protocol §4.2: orchestrator присваивает fallback после panic."""
    system = TransfluxSystem(
        state=FluxVar(value=0.0, trauma_threshold=1000.0),
        survival=SurvivalState(panic_threshold=0.3, fallback=0.0),
        flow_sensitivity=0.0,
        uncertainty_sensitivity=1.0,
    )
    panicked = system.tick(
        new_value=10.0,
        noisy_value=NoisyFloat(1.0, 0.1, confidence=0.2),
    )
    assert panicked
    assert system.state.value == 0.0
    assert system.survival.threat_level == 0.0
