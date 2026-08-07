# TRANSFLUX: Глоссарий и справочная карта

> Быстрая навигация по терминам, инвариантам и решениям.

---

## Формула

```
TRANSFLUX = Flow(State) · Uncertainty(Value) · Adaptation(Survival)
```

---

## Примитивы

| Примитив | Ось | Ключевые поля | Описание |
|---|---|---|---|
| `FluxVar<T>` | State | value, velocity, acceleration, comfort, history, trauma_threshold | Переменная как русло |
| `NoisyFloat` | Value | value, uncertainty, confidence | Значение как распределение |
| `SurvivalState` | Survival | threat_level, panic_threshold, identity_hash, scope, decay_rate, fallback | Модель выживания |
| `TransfluxSystem` | Orchestrator | state, survival, sensitivities | Паттерн оркестрации (не Core) |

---

## Производные концепции

| Концепция | Источник | Описание |
|---|---|---|
| Gradient of Truth | NoisyFloat | Степень истинности: f(confidence, SNR) |
| NoisyFlow | FluxVar × NoisyFloat | `FluxVar[NoisyFloat]` |
| FlowingTrit | FluxVar | `FluxVar[Trit]` с непрерывным вектором |
| Continuous Becoming | FluxVar | Вычисление = поток, не вызов |
| Polyphonic Identity | SurvivalState | Множество identity_hash на сущность |
| Deadname Erasure | SurvivalState | Атомарная ротация всех ссылок |
| Consent-First | SurvivalState | Деструктивные операции требуют явного согласия |

---

## Ключевые термины

| Термин | Значение |
|---|---|
| **Panic-First** | Архитектурный принцип: приоритет выживания над целостностью данных |
| **Consent-First** | Принцип API: деструктивные операции не выполняются без явной политики |
| **trauma** | Событие: velocity превысила trauma_threshold (advisory, не blocking) |
| **panic** | Фазовый переход: threat ≥ threshold → ротация identity, сброс threat |
| **decay_rate** | Скорость затухания threat_level в стабильных условиях |
| **momentum** | Образ инерции из манифеста; в коде = velocity + acceleration |
| **dispersion** | Устаревший синоним uncertainty |
| **coupling** | Связь между осями: ортогональны по определению, связаны по поведению |

---

## Callbacks

| Callback | Примитив | Сигнатура | Когда |
|---|---|---|---|
| `on_trauma` | FluxVar | `(flux, velocity) → None` | velocity > trauma_threshold |
| `on_panic` | SurvivalState | `(survival, old_hash) → None` | threat ≥ panic_threshold |

---

## Инварианты (INV)

| ID | Примитив | Утверждение |
|---|---|---|
| INV-N1 | NoisyFloat | uncertainty ≥ 0 |
| INV-N2 | NoisyFloat | 0 ≤ confidence ≤ 1 |
| INV-N3 | NoisyFloat | 0 ≤ gradient_of_truth() ≤ confidence |
| INV-F1 | FluxVar | -1 ≤ comfort ≤ 1 |
| INV-F2 | FluxVar | len(history) ≤ maxlen |
| INV-F3 | FluxVar | trajectory() == list(history) + [value] |
| INV-F4 | FluxVar | После update(v): value == v (trauma advisory) |
| INV-F5 | FluxVar | velocity == (new - old) / dt |
| INV-S1 | SurvivalState | 0 ≤ threat_level ≤ 1 |
| INV-S2 | SurvivalState | После panic: threat_level == 0 |
| INV-S3 | SurvivalState | После panic: identity_hash уникален |
| INV-S4 | SurvivalState | panic_count монотонно растёт |
| INV-S5 | SurvivalState | threat ≥ threshold → panic (детерминизм) |

## Свойства операций (OP)

| ID | Операция | Свойство |
|---|---|---|
| OP-1 | a ± b | uncertainty ≥ max(σ_a, σ_b) |
| OP-2 | a ± b | confidence ≤ min(c_a, c_b) |
| OP-3 | a ± b | value = a.value ± b.value (точно) |
| OP-4 | a × b | σ_z = √(b²σ_a² + a²σ_b²) |
| OP-5 | a × b | Корректно при нулевых значениях |
| OP-6 | a × b | σ_rel ≤ σ_rel_a + σ_rel_b |
| OP-7 | a / b | σ_z = √((σ_a/b)² + (aσ_b/b²)²) |
| OP-8 | a / b | b ≈ 0 → ZeroDivisionError |

## Свойства coupling (CP)

| ID | Связь | Свойство |
|---|---|---|
| CP-1 | Value → Survival | Ниже confidence → выше threat (монотонно) |
| CP-2 | State → Survival | Выше velocity → выше threat (монотонно) |
| CP-3 | Survival → State | Panic → threat=0, identity сменён |
| CP-4 | Value → Survival | Более надёжное значение → меньше threat |
| CP-5 | State → Survival | Более стабильное состояние → меньше threat |

---

## Design Rationale (DR)

| ID | Решение | Суть |
|---|---|---|
| DR-001 | Три оси | Минимально полный ортогональный базис |
| DR-002 | min() для confidence | Консервативная стратегия (weakest link) |
| DR-003 | decay_rate = 0 | Параноидный default безопаснее оптимистичного |
| DR-004 | comfort — скаляр | Простота достаточна для Core |
| DR-005 | trauma_threshold — число | Простота, тестируемость, детерминизм |
| DR-006 | history maxlen=32 | Trade-off память / контекст |
| DR-007 | Panic детерминирован | Гарантия безопасности ≠ азартная игра |
| DR-008 | update(value), не target | Общность > конкретная физика |
| DR-009 | σ, не σ² | Читаемость > микрооптимизация |
| DR-010 | Ортогональны, но coupled | Связь порождает emergent-поведение |
| DR-011 | Consent-First | Деструкция требует явной политики |
| DR-012 | Одна формула (·) | Мнемоника + критерий полноты |
| DR-013 | Advisory callbacks | Trauma/panic — сигнал, не блокировка |
| DR-014 | Orchestrator pattern | Примитивы не знают друг о друге |
| DR-015 | Один пакет, подмодули | Минимальный порог входа |

---

## Документы проекта

| Документ | Для кого |
|---|---|
| [One-pager](TRANSFLUX_One_Pager.md) | Первое знакомство (2 мин) |
| [Манифест](TRANSFLUX_Manifesto.md) | Позиция и голос |
| [Описание парадигмы](TRANSFLUX_Paradigm.md) | Разработчики, архитекторы |
| [Спецификация v0.3](TRANSFLUX_Specification_v0.3.md) | Формальное ядро |
| [Сценарии применения](TRANSFLUX_Use_Cases.md) | Конкретные примеры |
| [Смежные парадигмы](TRANSFLUX_Related_Paradigms.md) | Честное позиционирование |
| [Design Rationale](TRANSFLUX_Design_Rationale.md) | Обоснования решений |
| [Формальные инварианты](TRANSFLUX_Formal_Invariants.md) | Гарантии и тесты |
| [Anti-patterns](TRANSFLUX_Anti_Patterns.md) | Как НЕ надо |
| [API Reference](TRANSFLUX_API_Reference.md) | Справочник по примитивам и callbacks |
| [Архитектура](TRANSFLUX_Architecture.md) | Обзор верхнего уровня |
| [История](TRANSFLUX_History.md) | Как возник TRANSFLUX |
| [Changelog](CHANGELOG.md) | История изменений |
| [Roadmap](../ROADMAP.md) | Дорожная карта |
