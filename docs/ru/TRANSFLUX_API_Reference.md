> **Язык:** русский · [English](../en/TRANSFLUX_API_Reference.md)

# TRANSFLUX API Reference

> Компактный справочник Python-библиотеки (`src/transflux/`), октябрь 2026.
> Полная семантика и обоснования — в [спецификации](TRANSFLUX_Specification.md).

```python
from transflux import FluxVar, FlowingTrit, NoisyFloat, PolyphonicIdentity, SurvivalState, TransfluxSystem, classify_jump, weighted_mean
```

---

## FluxVar\<T\> — State Model (спецификация §1)

Переменная как русло: значение в движении, с историей и инерцией.

### Поля

| Поле | Тип | По умолчанию | Описание |
|---|---|---|---|
| `value` | `T` | — | текущее значение |
| `velocity` | `float` | `0.0` | скорость изменения |
| `acceleration` | `float` | `0.0` | ускорение |
| `comfort` | `float` | `0.0` | `[-1.0, +1.0]`: дисфория ↔ эйфория |
| `history` | `deque` | `maxlen=32` | предыдущие значения |
| `trauma_threshold` | `float` | `10.0` | порог trauma по \|velocity\| |
| `on_trauma` | `Callable \| None` | `None` | callback `(flux, velocity) → None` |

### Методы

| Метод | Возвращает | Описание |
|---|---|---|
| `update(new_value, dt=1.0)` | `FluxVar[T]` | обновить состояние; `dt ≤ 0` → `ValueError`; \|velocity\| > `trauma_threshold` → вызов `on_trauma` (значение устанавливается всегда, INV-F4) |
| `flow(new_value, dt=1.0)` | `FluxVar[T]` | то же, что `update`. Python-форма оператора `~>`; сам оператор отложен вместе с DSL |
| `trajectory()` | `List[T]` | история + текущее значение |

Слоя `constraints` нет: допустимость `value` задаёт вызывающий код (DR-017).

`classify_jump(sensor, neighbors) → "calm" | "alone" | "shared"` — скачок относительно соседей. Скачок: `|velocity| > trauma_threshold` этого датчика. `alone` — скачок есть, ни один другой датчик из списка его не подтвердил. Сам `sensor` в списке соседей не считается. Состояние не меняется (DR-022).

---

## FlowingTrit — непрерывный трит (спецификация §1.4)

Полюса `FlowingTrit.NEGATIVE` (`-1`), `LIMINAL` (`0`), `POSITIVE` (`+1`). Поле `value: float` хранится как есть: `-0.5` допустим, значение вне `[-1, 1]` не обрезается (INV-T1).

| Метод | Возвращает | Описание |
|---|---|---|
| `float(trit)` | `float` | само `value` |
| `nearest_pole()` | `float` | ближайший полюс; при равном расстоянии — более ранний из `-1`, `0`, `+1`. Значение не меняет |

Траектория: `FluxVar(value=FlowingTrit(...))` и дальше `flow()`. `float(trit)` нужен, чтобы `FluxVar` мог посчитать velocity.

---

## NoisyFloat — Value Model (спецификация §2)

Значение как распределение: центр, неуверенность, доверие.

### Поля

| Поле | Тип | По умолчанию | Описание |
|---|---|---|---|
| `value` | `float` | — | центр распределения (mean) |
| `uncertainty` | `float` | `0.0` | стандартное отклонение (σ) |
| `confidence` | `float` | `1.0` | `[0.0, 1.0]`: степень доверия |

### Операции (propagation of uncertainty, first-order Taylor)

| Операция | σ результата | confidence |
|---|---|---|
| `a + b`, `a - b` | `√(σ_a² + σ_b²)` | `min(c_a, c_b)` |
| `a * b` | `√(b²·σ_a² + a²·σ_b²)` | `min(c_a, c_b)` |
| `a / b` | `√((σ_a/b)² + (a·σ_b/b²)²)`; `b.value ≈ 0` → `ZeroDivisionError` | `min(c_a, c_b)` |

### Методы

| Метод | Возвращает | Описание |
|---|---|---|
| `is_reliable(min_confidence=0.7)` | `bool` | `confidence ≥ min_confidence` |
| `gradient_of_truth()` | `float` | `confidence × (1 − e^(−SNR))`; при σ = 0 → `confidence` |

`weighted_mean(readings) → NoisyFloat` — среднее независимых измерений одной величины. Вес `1/σ²`. При всех `σ > 0`: `uncertainty = 1/√(Σ 1/σ²)`, confidence — среднее confidence с теми же весами (DR-020). `σ = 0` забирает весь вес; если точные измерения расходятся, uncertainty — их среднеквадратичный разброс, confidence — `min` среди них. Пустой список → `ValueError`. Арифметика `+` и `/` этого веса не даёт.

---

## SurvivalState — Survival Model (спецификация §3)

Модель выживания: непрерывная угроза → дискретное перерождение (panic).

### Поля

| Поле | Тип | По умолчанию | Описание |
|---|---|---|---|
| `threat_level` | `float` | `0.0` | `[0.0, 1.0]` |
| `panic_threshold` | `float` | `0.75` | порог фазового перехода |
| `fallback` | `Any` | `None` | безопасное состояние для отката |
| `scope` | `"local" \| "process" \| "system"` | `"local"` | масштаб эффектов panic |
| `identity_hash` | `str` | случайный SHA-256 | текущая идентичность |
| `decay_rate` | `float` | `0.0` | затухание threat за цикл |
| `on_panic` | `Callable \| None` | `None` | callback `(survival, old_hash) → None` |

### Методы

| Метод | Возвращает | Описание |
|---|---|---|
| `update(threat_delta)` | `bool` | применить decay и delta; `True`, если сработал panic |
| `update_from_uncertainty(noisy, sensitivity=0.5)` | `bool` | `threat_delta = (1 − confidence) × sensitivity` |
| `update_from_flow(flux, sensitivity=0.1)` | `bool` | `threat_delta = min(1, \|velocity\| × sensitivity)` |
| `is_safe()` | `bool` | `threat_level < panic_threshold × 0.5` |

Panic (внутренний `_panic()`): инкремент счётчика, ротация `identity_hash`, сброс `threat_level` в 0, вызов `on_panic`. Не отменяется callbacks (DR-013). Маски `PolyphonicIdentity` при этом не трогает.

---

## PolyphonicIdentity — маски (спецификация §3.4)

Несколько хешей одной сущности. Panic их не вращает, пока callback сам этого не попросит (DR-023).

| Метод | Возвращает | Описание |
|---|---|---|
| `add(role)` | `str` | новая маска; повтор роли → `ValueError` |
| `alias(role, source)` | `str` | ещё одна ссылка на хеш `source` |
| `present(role)` | `str` | хеш этой роли |
| `grant(role, group)` | `None` | текущий хеш роли входит в группу |
| `in_group(group)` | `bool` | есть ли живая маска в группе; роль не называется |
| `holds(identity_hash)` | `bool` | показывает ли какая-нибудь маска этот хеш |
| `erase(old_hash)` | `str` | все ссылки на старый хеш становятся одним новым; неизвестный хеш → `KeyError` |
| `rotate_all()` | `dict` | каждый различный хеш заменён; старых в книге нет |

---

## TransfluxSystem — orchestrator (спецификация §4.2)

Рекомендуемый паттерн, не часть ядра. Связывает три оси в явном цикле.

| Поле | По умолчанию | Описание |
|---|---|---|
| `state: FluxVar` | — | ось State |
| `survival: SurvivalState` | — | ось Survival |
| `flow_sensitivity` | `0.1` | чувствительность связи State → Survival |
| `uncertainty_sensitivity` | `0.5` | чувствительность связи Value → Survival |
| `value: NoisyFloat \| None` | `None` | последнее наблюдение Value, записывается в `tick` |
| `ticks` | `0` | сколько раз вызван `tick` |
| `peak_threat` | `0` | наибольшая угроза внутри цикла, до того как panic обнулит `threat_level` |
| `backup_value` | `None` | запасное состояние; вместе с `backup_noisy` вооружает режим |
| `backup_noisy` | `None` | запасное наблюдение Value |
| `degraded` | `False` | система слушает запасную пару, а не вход `tick` |

`tick(new_value, noisy_value, dt=1.0) → bool` — один цикл. Если `degraded` и запасная пара задана, вход подменяется до `state.flow`. Дальше: запомнить `value` → coupling → при panic `state.flow(fallback)`. Если на этом цикле был panic и пара задана, `degraded` становится `True`. Возвращает `True`, если был panic.

`backup_armed() → bool` — заданы и `backup_value`, и `backup_noisy`. `recover()` снимает `degraded`; сама пара остаётся. Без вооружённой пары panic не залипает (DR-021).

---

## Callbacks (Event Model, спецификация §4.3)

| Примитив | Callback | Сигнатура | Когда |
|---|---|---|---|
| `FluxVar` | `on_trauma` | `(flux, velocity) → None` | \|velocity\| > `trauma_threshold` |
| `SurvivalState` | `on_panic` | `(survival, old_hash) → None` | `threat_level ≥ panic_threshold` |

Вызываются синхронно, не могут отменить операцию, при `None` событие молча проглатывается.

---

Гарантии реализации: [Formal Invariants](TRANSFLUX_Formal_Invariants.md) (INV/OP/CP), проверяются тестами в `tests/`.
