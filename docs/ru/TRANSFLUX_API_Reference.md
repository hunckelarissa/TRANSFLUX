> **Язык:** русский · [English](../en/TRANSFLUX_API_Reference.md)

# TRANSFLUX API Reference

> Компактный справочник Python-библиотеки (`src/transflux/`), октябрь 2026.
> Полная семантика и обоснования — в [спецификации](TRANSFLUX_Specification.md).

```python
from transflux import (
    FluxVar, FlowingTrit, NoisyFloat, NoisyFlow,
    IdentityLedger, PolyphonicIdentity, ScarMemory,
    SurvivalState, TransfluxSystem, classify_jump, weighted_mean,
    stale_threat, uncertainty_margin_threat,
)
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
| `comfort` | `float` | `0.0` | `[-1.0, +1.0]`: дисфория ↔ эйфория; движется при trauma/calm (DR-024) |
| `history` | `deque` | `maxlen=32` | предыдущие значения |
| `trauma_threshold` | `float` | `10.0` | порог trauma по \|velocity\| |
| `trauma_comfort_cost` | `float` | `0.25` | насколько comfort падает при trauma |
| `calm_comfort_gain` | `float` | `0.02` | насколько comfort растёт на спокойном шаге |
| `on_trauma` | `Callable \| None` | `None` | callback `(flux, velocity) → None` |

### Методы

| Метод | Возвращает | Описание |
|---|---|---|
| `update(new_value, dt=1.0)` | `FluxVar[T]` | обновить состояние; `dt ≤ 0` → `ValueError`; \|velocity\| > `trauma_threshold` → вызов `on_trauma` и снижение comfort; иначе рост comfort (значение устанавливается всегда, INV-F4) |
| `flow(new_value, dt=1.0)` | `FluxVar[T]` | то же, что `update`. Python-форма оператора `~>`; сам оператор отложен вместе с DSL |
| `trajectory()` | `List[T]` | история + текущее значение |

Слоя `constraints` нет: допустимость `value` задаёт вызывающий код (DR-017). Нулевые ставки замораживают comfort как раньше.

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
| `float(noisy)` | `float` | центр (`value`); даёт `FluxVar` / `NoisyFlow` считать velocity |

`NoisyFlow` — алиас `FluxVar[NoisyFloat]`.

`weighted_mean(readings, *, correlation=0.0, covariance=None) → NoisyFloat` — среднее измерений одной величины. Вес `1/σ²`. При всех `σ > 0` и `correlation=0`: `uncertainty = 1/√(Σ 1/σ²)`, confidence — взвешенное среднее (DR-020). При `correlation=ρ ∈ [0,1]` uncertainty становится `σ_indep·√(1+(n−1)ρ)`, confidence тянется к `min` (DR-027). При `covariance=Σ` (n×n, диагональ = `σ²`) — GLS-среднее (DR-029); не вместе с `correlation ≠ 0`; не с точными `σ = 0`. `σ = 0` без covariance забирает весь вес; если точные расходятся — среднеквадратичный разброс и `min` confidence. Плохая форма / вырожденная Σ / пустой список / `ρ` вне `[0,1]` → `ValueError`. Арифметика `+` и `/` этого веса не даёт.

`stale_threat(elapsed, timeout, sensitivity=1.0) → float` — дельта угрозы, когда сигнала нет дольше `timeout`; до таймаута — `0`; клип в `1.0`.

`uncertainty_margin_threat(noisy, max_uncertainty, sensitivity=1.0) → float` — дельта угрозы, когда `σ` выше запаса; пока в пределах — `0`.

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
| `on_panic_local` / `on_panic_process` / `on_panic_system` | `Callable \| None` | `None` | scope-хук после `on_panic` (DR-025) |

### Методы

| Метод | Возвращает | Описание |
|---|---|---|
| `update(threat_delta)` | `bool` | применить decay и delta; `True`, если сработал panic |
| `update_from_uncertainty(noisy, sensitivity=0.5)` | `bool` | `threat_delta = (1 − confidence) × sensitivity` |
| `update_from_flow(flux, sensitivity=0.1)` | `bool` | `threat_delta = min(1, \|velocity\| × sensitivity)` |
| `is_safe()` | `bool` | `threat_level < panic_threshold × 0.5` |

Panic (внутренний `_panic()`): инкремент счётчика, ротация `identity_hash`, сброс `threat_level` в 0, вызов `on_panic`, затем подходящий scope-хук, если задан. Не отменяется callbacks (DR-013). Маски `PolyphonicIdentity` при этом не трогает.

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
| `live()` (classmethod) | `list` | достижимые книги процесса (weak-реестр, DR-030) |
| `erase_live(old_hash)` (classmethod) | `str` | переписать хеш во всех живых книгах, где он есть; неизвестный → `KeyError` |

## IdentityLedger — несколько книг (DR-026, DR-030)

Именованные книги, зарегистрированные явно. Незарегистрированная книга невидима для обычного `erase`.

| Метод | Возвращает | Описание |
|---|---|---|
| `register(name, book=None)` | `PolyphonicIdentity` | добавить книгу; повтор имени → `ValueError`; `book=None` создаёт пустую |
| `book(name)` | `PolyphonicIdentity` | книга; нет имени → `KeyError` |
| `names()` | `list` | имена в порядке добавления |
| `holds(identity_hash)` | `bool` | есть ли хеш хотя бы в одной зарегистрированной книге |
| `erase(old_hash, *, discovered=False)` | `str` | переписать в зарегистрированных; при `discovered=True` ещё и в живых незарегистрированных (DR-030); неизвестный → `KeyError` |
| `rotate_all()` | `dict` | `{имя_книги: mapping}` для каждой книги |

## ScarMemory — шрамы (DR-028)

Именованные места, где уже было больно. Panic их не ставит — это делает вызывающий код.

| Поле / метод | По умолчанию / возвращает | Описание |
|---|---|---|
| `boost_factor` | `1.0` | насколько intensity усиливает `amplify` |
| `max_scar` | `1.0` | потолок intensity на site |
| `mark(site, amount=0.25)` | `float` | накопить шрам; возвращает новую интенсивность |
| `intensity(site)` | `float` | текущая глубина; неизвестное место → `0` |
| `sites()` | `list` | места с intensity `> 0` |
| `amplify(site, base)` | `float` | `base × (1 + boost_factor × intensity)` |
| `fade(amount=0.05)` | `None` | снять одинаковый слой со всех шрамов; нули исчезают |

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
| `signal_timeout` | `None` | вместе с `signal_age` в `tick` включает `stale_threat` |
| `stale_sensitivity` | `1.0` | чувствительность stale-хелпера |
| `uncertainty_limit` | `None` | если задан — `uncertainty_margin_threat` по наблюдению |
| `margin_sensitivity` | `1.0` | чувствительность margin-хелпера |

`tick(new_value, noisy_value, dt=1.0, *, signal_age=None) → bool` — один цикл. Если `degraded` и запасная пара задана, вход подменяется до `state.flow`. Дальше: запомнить `value` → coupling → опциональная угроза stale/margin → при panic `state.flow(fallback)`. Если на этом цикле был panic и пара задана, `degraded` становится `True`. Возвращает `True`, если был panic.

`backup_armed() → bool` — заданы и `backup_value`, и `backup_noisy`. `recover()` снимает `degraded`; сама пара остаётся. Без вооружённой пары panic не залипает (DR-021).

---

## Callbacks (Event Model, спецификация §4.3)

| Примитив | Callback | Сигнатура | Когда |
|---|---|---|---|
| `FluxVar` | `on_trauma` | `(flux, velocity) → None` | \|velocity\| > `trauma_threshold` |
| `SurvivalState` | `on_panic` | `(survival, old_hash) → None` | `threat_level ≥ panic_threshold` |
| `SurvivalState` | `on_panic_local` / `process` / `system` | `(survival, old_hash) → None` | после `on_panic`, только хук, совпавший с `scope` |

Вызываются синхронно, не могут отменить операцию, при `None` событие молча проглатывается.

---

Гарантии реализации: [Formal Invariants](TRANSFLUX_Formal_Invariants.md) (INV/OP/CP), проверяются тестами в `tests/`.
