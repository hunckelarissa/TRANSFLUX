"""Десять синтетических сценариев: работает ли концепция на примерах.

Это не проверки формул из Formal Invariants. Каждый тест — короткая история.
Графики пишутся в docs/figures/synthetic/ там, где важна форма кривой.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from charts import save_bars, save_lines
from transflux import (
    FlowingTrit,
    FluxVar,
    NoisyFloat,
    SurvivalState,
    TransfluxSystem,
    classify_jump,
    weighted_mean,
)

FIGURES = Path(__file__).resolve().parents[2] / "docs" / "figures" / "synthetic"


def test_smooth_fever_does_not_panic():
    """Плавный нагрев на 0.1 °C в час — не травма и не panic.

    История есть: velocity держится около 0.1. Абсолютное значение
    само по себе тревогу не включает.
    """
    system = _ward(trauma_threshold=1.0, decay_rate=0.04)
    threats = []
    for hour in range(8):
        temperature = 36.6 + 0.1 * hour
        panicked = system.tick(temperature, NoisyFloat(temperature, 0.2, confidence=0.92))
        threats.append(system.survival.threat_level)
        assert panicked is False
    assert system.survival._panic_count == 0
    assert system.state.velocity == pytest.approx(0.1)
    assert max(threats) < 0.1
    assert system.state.trajectory()[0] == 36.6
    assert system.state.value == pytest.approx(37.3)


def test_glitch_is_trauma_but_value_is_kept():
    """Скачок 36.6 → 40.2 за час — сигнал травмы, не остановка.

    Значение всё равно становится 40.2. Comfort сам не реагирует:
    библиотека только ограничивает его в [-1, 1], если его задали снаружи.
    """
    traumas = []
    fever = FluxVar(value=36.6, trauma_threshold=1.0, comfort=0.0)
    fever.on_trauma = lambda flux, velocity: traumas.append(velocity)

    fever.flow(40.2)

    assert fever.value == pytest.approx(40.2)
    assert traumas == pytest.approx([3.6])
    assert fever.comfort == 0.0
    assert fever.trajectory() == pytest.approx([36.6, 40.2])


def test_gradient_of_truth_shrinks_when_signal_is_buried():
    """Серая зона появляется, когда шум сопоставим с величиной.

    38.1 ± 2 при confidence 0.4 почти целиком сохраняет эту уверенность:
    само число большое относительно шума. Маленький сигнал в широком
    шуме проседает сильнее, чем говорит один confidence.
    """
    certain = NoisyFloat(38.1, uncertainty=0.0, confidence=0.95)
    loud = NoisyFloat(38.1, uncertainty=2.0, confidence=0.4)
    buried = NoisyFloat(0.3, uncertainty=2.0, confidence=0.9)

    assert certain.gradient_of_truth() == pytest.approx(0.95)
    assert loud.gradient_of_truth() == pytest.approx(0.4, abs=0.01)
    assert 0 < buried.gradient_of_truth() < 0.3
    assert buried.gradient_of_truth() < buried.confidence


def test_dilution_confidence_follows_the_weakest_step():
    """Разведение: итог не увереннее самой слабой склянки.

    Запас 0.95 и вода 0.90, но аликвота только 0.80 — у порции confidence 0.80.
    Неуверенность не выбрасывается по дороге.
    """
    stock = NoisyFloat(10.0, uncertainty=0.2, confidence=0.95)
    water = NoisyFloat(90.0, uncertainty=0.5, confidence=0.90)
    aliquot = NoisyFloat(4.0, uncertainty=0.05, confidence=0.80)

    mix = stock + water
    portion = mix / aliquot

    assert mix.confidence == pytest.approx(0.90)
    assert mix.uncertainty > stock.uncertainty
    assert portion.value == pytest.approx(25.0)
    assert portion.confidence == pytest.approx(0.80)
    assert portion.uncertainty > 0


def test_trit_keeps_the_halfway_value():
    """Мнение течёт через -0.5, а не перескакивает с «нет» на «да»."""
    steps = [-1.0, -0.5, -0.25, 0.0, 0.5, 1.0]
    opinion = FluxVar(value=FlowingTrit(steps[0]))
    for step in steps[1:]:
        opinion.flow(FlowingTrit(step))

    traced = [item.value for item in opinion.trajectory()]
    assert traced == steps
    assert -0.5 in traced
    assert opinion.value.value == 1.0

    save_lines(
        FIGURES / "trit_flow.svg",
        "Трит: промежуточные значения сохраняются",
        [{
            "title": "от «нет» к «да» через половину",
            "ylabel": "трит",
            "series": [{"name": "значение", "values": traced, "color": "#1d4e89"}],
            "hlines": [
                {"y": -1, "label": "нет", "color": "#52606d"},
                {"y": 0, "label": "порог", "color": "#52606d"},
                {"y": 1, "label": "да", "color": "#2f6f4e"},
            ],
        }],
        xlabel="шаг",
    )


def test_decay_releases_threat_that_paranoia_would_fire():
    """Одинаковая вспышка угрозы. Без затухания — panic. С затуханием — спад."""
    burst = [0.2] * 4 + [0.0] * 12
    paranoia = _threat_trace(burst, decay_rate=0.0)
    recovery = _threat_trace(burst, decay_rate=0.08)

    assert paranoia["panicked_at"] == 3
    assert recovery["panicked_at"] is None
    assert max(recovery["levels"]) < 0.75
    assert recovery["levels"][-1] == 0.0

    save_lines(
        FIGURES / "threat_fade.svg",
        "Одна и та же вспышка: паранойя срывается, затухание отпускает",
        [{
            "title": "threat_level",
            "ylabel": "угроза",
            "series": [
                {"name": "decay = 0", "values": paranoia["levels"], "color": "#9b2226"},
                {"name": "decay = 0.08", "values": recovery["levels"], "color": "#2f6f4e"},
            ],
            "hlines": [{"y": 0.75, "label": "порог panic", "color": "#9b2226"}],
            "events": [{"index": 3, "label": "panic"}],
        }],
        xlabel="цикл",
    )


def test_panic_changes_identity_and_erases_only_via_callback():
    """Panic меняет имя сам. Переписку стирает только тот, кто на это подписался.

    Без callback ящик остаётся. С callback — пустеет. Это Consent-First:
    уничтожение данных не спрятано внутри примитива.
    """
    kept = ["источник", "черновик"]
    silent = SurvivalState(panic_threshold=0.75, scope="system", fallback=0)
    old_silent = silent.identity_hash
    assert silent.update(1.0) is True
    assert silent.identity_hash != old_silent
    assert kept == ["источник", "черновик"]
    assert silent.threat_level == 0.0

    inbox = ["источник", "черновик"]
    loud = SurvivalState(
        panic_threshold=0.75,
        scope="system",
        on_panic=lambda survival, old_hash: inbox.clear(),
    )
    old_loud = loud.identity_hash
    assert loud.update(1.0) is True
    assert inbox == []
    assert loud.identity_hash != old_loud


def test_gust_returns_drone_to_fallback():
    """Порыв сдвигает дрон. Скорость скачка сама доводит Survival до panic.

    К концу шага положение — fallback, а не сорванная координата.
    Плохой GPS в этот сценарий не подмешан: срыв делает одна ось State.
    """
    commanded = [0.0, 1.0, 2.0, 2.5, 14.0, 2.5, 2.5, 2.5]
    drone = TransfluxSystem(
        state=FluxVar(value=commanded[0], trauma_threshold=4.0),
        survival=SurvivalState(panic_threshold=0.75, fallback=2.5, decay_rate=0.0),
        flow_sensitivity=0.08,
        uncertainty_sensitivity=0.0,
    )
    traumas = []
    drone.state.on_trauma = lambda flux, velocity: traumas.append(velocity)

    state = []
    threat = []
    panics = []
    for index, position in enumerate(commanded):
        panicked = drone.tick(position, NoisyFloat(position, 1.0, confidence=0.4))
        state.append(float(drone.state.value))
        threat.append(drone.peak_threat)
        if panicked:
            panics.append(index)

    assert panics == [4]
    assert threat[4] >= 0.75
    assert traumas and abs(traumas[0]) > 4
    assert state[4] == pytest.approx(2.5)
    assert drone.survival._panic_count == 1

    save_lines(
        FIGURES / "drone_gust.svg",
        "Дрон: порыв не становится новой правдой",
        [
            {
                "title": "положение",
                "ylabel": "метры",
                "series": [
                    {"name": "команда", "values": commanded, "color": "#c44900"},
                    {"name": "state", "values": state, "color": "#1d4e89"},
                ],
                "events": [{"index": 4, "label": "panic"}],
            },
            {
                "title": "пик угрозы в цикле",
                "ylabel": "угроза",
                "series": [{"name": "threat", "values": threat, "color": "#9b2226"}],
                "hlines": [{"y": 0.75, "label": "порог", "color": "#9b2226"}],
                "events": [{"index": 4, "label": "panic"}],
            },
        ],
        xlabel="тик",
    )


def test_precise_sensors_outweigh_a_broken_one():
    """Сбойный датчик на 300 не должен задавать воздух в городе.

    Обычное среднее через `+` и `/` уезжает к 109 и берёт confidence худшего.
    `weighted_mean` весит измерения как 1/σ²: итог около 13, confidence
    остаётся у спокойных датчиков. Скачок одного датчика — его травма;
    сосед без скачка травмы не получает.
    """
    calm_a = NoisyFloat(12.0, uncertainty=1.0, confidence=0.92)
    calm_b = NoisyFloat(15.0, uncertainty=1.2, confidence=0.88)
    broken = NoisyFloat(300.0, uncertainty=40.0, confidence=0.20)
    readings = [calm_a, calm_b, broken]

    naive = _arithmetic_mean(readings)
    city = weighted_mean(readings)

    assert naive.value == pytest.approx(109.0)
    assert naive.confidence == pytest.approx(0.20)
    assert city.value == pytest.approx(13.3354, abs=1e-3)
    assert city.confidence == pytest.approx(0.9033, abs=1e-3)
    assert city.uncertainty < broken.uncertainty

    jumped = FluxVar(value=12.0, trauma_threshold=50.0)
    neighbor = FluxVar(value=14.0, trauma_threshold=50.0)
    jumped_traumas = []
    neighbor_traumas = []
    jumped.on_trauma = lambda flux, velocity: jumped_traumas.append(velocity)
    neighbor.on_trauma = lambda flux, velocity: neighbor_traumas.append(velocity)
    jumped.flow(300.0)
    neighbor.flow(16.0)
    assert jumped_traumas and not neighbor_traumas

    save_bars(
        FIGURES / "air_sensors.svg",
        "Воздух: точный датчик перевешивает сбой",
        ["среднее через + и /", "weighted_mean"],
        [{
            "name": "PM2.5",
            "values": [naive.value, city.value],
            "color": "#1d4e89",
        }],
        ylabel="мкг/м³; у weighted_mean confidence около 90%, не 20%",
    )


def test_lone_spike_is_not_a_shared_cloud():
    """Один точный на вид скачок не должен становиться воздухом города.

    Соседи спокойны, classify_jump отвечает alone и сами числа не меняет.
    Пока вызывающий код не расширит uncertainty этого датчика, weighted_mean
    ему верит: σ маленькая, вес большой.
    """
    north = [12.0, 12.4, 12.2, 12.6, 12.5, 12.8, 12.6, 12.9]
    south = [14.0, 14.2, 14.1, 14.4, 14.5, 14.3, 14.6, 14.4]
    yard = [13.0, 13.2, 13.1, 13.0, 180.0, 13.4, 13.2, 13.5]
    traces = {
        "север": FluxVar(value=north[0], trauma_threshold=30.0),
        "юг": FluxVar(value=south[0], trauma_threshold=30.0),
        "двор": FluxVar(value=yard[0], trauma_threshold=30.0),
    }
    series = {"север": north, "юг": south, "двор": yard}
    kinds = []
    for index in range(1, len(yard)):
        for name, values in series.items():
            traces[name].flow(values[index])
        kinds.append(classify_jump(traces["двор"], [traces["север"], traces["юг"]]))

    assert kinds[3] == "alone"
    assert yard[4] == 180.0
    assert traces["двор"].comfort == 0.0

    trusted = weighted_mean([
        NoisyFloat(12.5, uncertainty=1.0, confidence=0.9),
        NoisyFloat(14.5, uncertainty=1.0, confidence=0.9),
        NoisyFloat(180.0, uncertainty=1.0, confidence=0.9),
    ])
    distrusted = weighted_mean([
        NoisyFloat(12.5, uncertainty=1.0, confidence=0.9),
        NoisyFloat(14.5, uncertainty=1.0, confidence=0.9),
        NoisyFloat(180.0, uncertainty=80.0, confidence=0.2),
    ])
    assert trusted.value == pytest.approx(69.0)
    assert distrusted.value == pytest.approx(13.5, abs=0.1)

    save_lines(
        FIGURES / "sensor_jumps.svg",
        "Воздух: скачок одного двора — не общее облако",
        [{
            "title": "PM2.5",
            "ylabel": "мкг/м³",
            "series": [
                {"name": "север", "values": north, "color": "#2f6f4e"},
                {"name": "юг", "values": south, "color": "#1d4e89"},
                {"name": "двор", "values": yard, "color": "#c44900"},
            ],
            "events": [{"index": 4, "label": "alone"}],
        }],
        xlabel="шаг",
    )


def test_ward_switches_to_backup_after_panic():
    """Сутки в палате: плавный рост, сбой, падение уверенности.

    Запасная пара задана заранее. Плохой датчик после panic продолжает
    врать, но оркестратор уже держится backup и второй раз не срывается.
    Без этой пары режим сам не включается.
    """
    script = [(36.6 + 0.1 * hour, 0.92) for hour in range(8)]
    script += [(40.2, 0.92), (37.4, 0.90)]
    script += [(37.4, confidence) for confidence in (0.55, 0.40, 0.25, 0.20, 0.20)]

    system = _ward(trauma_threshold=1.0, decay_rate=0.04)
    system.backup_value = 37.5
    system.backup_noisy = NoisyFloat(37.5, uncertainty=0.3, confidence=0.95)
    traumas = []
    system.state.on_trauma = lambda flux, velocity: traumas.append(velocity)

    readings = []
    states = []
    sensor_confidence = []
    used_confidence = []
    threats = []
    panic_hours = []

    for hour in range(20):
        temperature, confidence = script[min(hour, len(script) - 1)]
        panicked = system.tick(temperature, NoisyFloat(temperature, 0.3, confidence))
        readings.append(temperature)
        states.append(float(system.state.value))
        sensor_confidence.append(confidence)
        used_confidence.append(system.value.confidence)
        threats.append(system.peak_threat)
        if panicked:
            panic_hours.append(hour)

    assert panic_hours == [11]
    assert threats[11] >= 0.75
    assert len(traumas) == 2
    assert abs(traumas[0]) > 1
    assert states[11] == pytest.approx(36.6)
    assert states[-1] == pytest.approx(37.5)
    assert system.degraded is True
    assert used_confidence[-1] == pytest.approx(0.95)
    assert sensor_confidence[-1] == pytest.approx(0.20)
    assert max(threats[12:]) < 0.05
    assert system.survival._panic_count == 1

    save_lines(
        FIGURES / "ward_day.svg",
        "Палата: после panic система держится запасного датчика",
        [
            {
                "title": "температура",
                "ylabel": "°C",
                "series": [
                    {"name": "датчик", "values": readings, "color": "#c44900"},
                    {"name": "state", "values": states, "color": "#1d4e89"},
                ],
                "events": [{"index": 11, "label": "panic"}],
            },
            {
                "title": "уверенность",
                "ylabel": "confidence",
                "series": [
                    {"name": "датчик", "values": sensor_confidence, "color": "#c44900"},
                    {"name": "система", "values": used_confidence, "color": "#7a306c"},
                ],
                "events": [{"index": 11, "label": "panic"}],
            },
            {
                "title": "пик угрозы в цикле",
                "ylabel": "угроза",
                "series": [{"name": "threat", "values": threats, "color": "#9b2226"}],
                "hlines": [{"y": 0.75, "label": "порог", "color": "#9b2226"}],
                "events": [{"index": 11, "label": "panic"}],
            },
        ],
        xlabel="час",
    )


def _ward(trauma_threshold, decay_rate):
    return TransfluxSystem(
        state=FluxVar(value=36.6, trauma_threshold=trauma_threshold),
        survival=SurvivalState(panic_threshold=0.75, fallback=36.6, decay_rate=decay_rate),
        flow_sensitivity=0.05,
        uncertainty_sensitivity=0.9,
    )


def _threat_trace(deltas, decay_rate):
    survival = SurvivalState(panic_threshold=0.75, decay_rate=decay_rate)
    levels = []
    panicked_at = None
    for index, delta in enumerate(deltas):
        if survival.update(delta) and panicked_at is None:
            panicked_at = index
        levels.append(survival.peak_threat)
    return {"levels": levels, "panicked_at": panicked_at}


def _arithmetic_mean(readings):
    total = readings[0]
    for reading in readings[1:]:
        total = total + reading
    return total / NoisyFloat(float(len(readings)), uncertainty=0.0, confidence=1.0)

