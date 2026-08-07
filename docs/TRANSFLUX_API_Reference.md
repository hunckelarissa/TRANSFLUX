# TRANSFLUX API Reference

> Компактный справочник по примитивам референсной реализации (`src/transflux/`).
> Полная семантика и обоснования — в [спецификации v0.3](TRANSFLUX_Specification_v0.3.md).

```python
from transflux import FluxVar, NoisyFloat, SurvivalState, TransfluxSystem
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
| `trajectory()` | `List[T]` | история + текущее значение |

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

Panic (внутренний `_panic()`): инкремент счётчика, ротация `identity_hash`, сброс `threat_level` в 0, вызов `on_panic`. Не отменяется callbacks (DR-013).

---

## TransfluxSystem — orchestrator (спецификация §4.2)

Рекомендуемый паттерн, не часть ядра. Связывает три оси в явном цикле.

| Поле | По умолчанию | Описание |
|---|---|---|
| `state: FluxVar` | — | ось State |
| `survival: SurvivalState` | — | ось Survival |
| `flow_sensitivity` | `0.1` | чувствительность связи State → Survival |
| `uncertainty_sensitivity` | `0.5` | чувствительность связи Value → Survival |

`tick(new_value, noisy_value, dt=1.0) → bool` — один цикл: update state → coupling → при panic присваивает `fallback` в state. Возвращает `True`, если был panic.

---

## Callbacks (Event Model, спецификация §4.3)

| Примитив | Callback | Сигнатура | Когда |
|---|---|---|---|
| `FluxVar` | `on_trauma` | `(flux, velocity) → None` | \|velocity\| > `trauma_threshold` |
| `SurvivalState` | `on_panic` | `(survival, old_hash) → None` | `threat_level ≥ panic_threshold` |

Вызываются синхронно, не могут отменить операцию, при `None` событие молча проглатывается.

---

Гарантии реализации: [Formal Invariants](TRANSFLUX_Formal_Invariants.md) (INV/OP/CP), проверяются тестами в `tests/`.
