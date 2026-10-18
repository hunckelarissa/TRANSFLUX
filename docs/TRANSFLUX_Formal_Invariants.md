# TRANSFLUX: Формальные свойства и инварианты

> Гарантии, которые TRANSFLUX-совместимая реализация обязана обеспечить.  
> Каждое свойство формулируется как утверждение, которое можно проверить тестом.

---

## 1. Инварианты типов

Свойства, которые должны выполняться **всегда** для любого экземпляра.

### 1.1 NoisyFloat

| ID | Инвариант | Формулировка |
|---|---|---|
| INV-N1 | Неотрицательность uncertainty | `uncertainty ≥ 0` |
| INV-N2 | Ограниченность confidence | `0 ≤ confidence ≤ 1` |
| INV-N3 | Согласованность gradient_of_truth | `0 ≤ gradient_of_truth() ≤ confidence` |

**INV-N3 обоснование:** `gradient_of_truth() = confidence × (1 - e^(-SNR))`. Так как `0 ≤ (1 - e^(-SNR)) ≤ 1` для `SNR ≥ 0`, результат ограничен сверху confidence и снизу нулём.

### 1.2 FluxVar

| ID | Инвариант | Формулировка |
|---|---|---|
| INV-F1 | Ограниченность comfort | `-1 ≤ comfort ≤ 1` |
| INV-F2 | Ограниченность history | `len(history) ≤ maxlen` |
| INV-F3 | Согласованность trajectory | `trajectory() == list(history) + [value]` |
| INV-F4 | Обновление значения | После `update(v, dt)`: `value == v` |
| INV-F5 | Согласованность velocity | После `update(v, dt)`: `velocity == (v - old_value) / dt` |

**INV-F4 обоснование:** update всегда устанавливает новое значение. Trauma — сигнал, не блокировка. Это проектное решение (см. DR-013): callbacks могут логировать или эскалировать, но не могут отменить обновление.

### 1.3 SurvivalState

| ID | Инвариант | Формулировка |
|---|---|---|
| INV-S1 | Ограниченность threat_level | `0 ≤ threat_level ≤ 1` |
| INV-S2 | Сброс при panic | После `_panic()`: `threat_level == 0` |
| INV-S3 | Уникальность identity | После `_panic()`: `identity_hash ∉ {предыдущие identity_hash}` (с криптографической вероятностью) |
| INV-S4 | Монотонность panic_count | `_panic_count` не убывает |
| INV-S5 | Детерминизм panic | `threat_level ≥ panic_threshold` ↔ panic срабатывает |

### 1.4 FlowingTrit

| ID | Инвариант | Формулировка |
|---|---|---|
| INV-T1 | Значение не квантуется и не клампится | `FlowingTrit(x).value == x` и `float(FlowingTrit(x)) == x` |

**INV-T1 обоснование:** полюса `-1`, `0`, `+1` — ориентиры смысла, не множество допустимых состояний (DR-018). Промежуточное `-0.5` и значение вне `[-1, 1]` сохраняются как записаны (DR-017).

---

## 2. Свойства операций (Operation Properties)

Гарантии, обеспечиваемые арифметическими операциями над NoisyFloat.

### 2.1 Сложение и вычитание

Для `z = a ± b`:

| ID | Свойство | Формулировка | Доказательство |
|---|---|---|---|
| OP-1 | Uncertainty не убывает | `z.uncertainty ≥ max(a.uncertainty, b.uncertainty)` | `√(σ_a² + σ_b²) ≥ max(σ_a, σ_b)`, т.к. `x² + y² ≥ max(x, y)²` |
| OP-2 | Confidence не возрастает | `z.confidence ≤ min(a.confidence, b.confidence)` | По определению: `min(c_a, c_b) ≤ min(c_a, c_b)` |
| OP-3 | Значение точно | `z.value == a.value ± b.value` | Арифметика без округления (в пределах float precision) |

**OP-1 — ключевое свойство.** Оно гарантирует, что **неуверенность не может исчезнуть** при вычислениях. Система не теряет информацию о качестве данных.

### 2.2 Умножение

Для `z = a × b`:

| ID | Свойство | Формулировка |
|---|---|---|
| OP-4 | Формула uncertainty | `z.uncertainty == √(b²·σ_a² + a²·σ_b²)` |
| OP-5 | Корректность при нуле | Если `a.value == 0`: `z.uncertainty == |b| × σ_a` (формула остаётся корректной) |
| OP-6 | Верхняя граница относительной uncertainty | Для `a, b ≠ 0`: `z.σ_rel ≤ a.σ_rel + b.σ_rel`, где `σ_rel = uncertainty / |value|` |

**OP-6 обоснование:** `√(x² + y²) ≤ x + y` для `x, y ≥ 0` (следствие `(x+y)² = x² + 2xy + y² ≥ x² + y²`). Относительная uncertainty произведения ограничена суммой относительных uncertainties сомножителей.

### 2.3 Деление

Для `z = a / b` (при `b.value ≠ 0`):

| ID | Свойство | Формулировка |
|---|---|---|
| OP-7 | Формула uncertainty | `z.uncertainty == √((σ_a/b)² + (a·σ_b/b²)²)` |
| OP-8 | Деление на нулевое значение | `b.value ≈ 0` → `ZeroDivisionError` |

### 2.4 Взвешенное среднее

Для `weighted_mean` независимых измерений с `σ > 0`:

| ID | Свойство | Формулировка |
|---|---|---|
| OP-9 | Формула uncertainty | `σ = 1 / √(Σ 1/σ_i²)` |
| OP-10 | Точное измерение доминирует | Участник с `σ = 0` задаёт value; участники с `σ > 0` его не сдвигают |
| OP-11 | Пустой вход | Пустой список → `ValueError` |

Confidence здесь — взвешенное среднее confidence, не `min` (DR-020). Исключение: если значение определяют только измерения с `σ = 0`, confidence результата — `min` среди них.

---

## 3. Свойства связанной системы (Coupling Properties)

Гарантии поведения при взаимодействии осей.

| ID | Свойство | Формулировка |
|---|---|---|
| CP-1 | Монотонность uncertainty → threat | `update_from_uncertainty(noisy)`: `threat_delta = (1 - confidence) × sensitivity ≥ 0` при `sensitivity ≥ 0` |
| CP-2 | Монотонность velocity → threat | `update_from_flow(flux)`: `threat_delta = min(1, |velocity| × sensitivity) ≥ 0` при `sensitivity ≥ 0` |
| CP-3 | Panic → safe state | После panic: `threat_level == 0 ∧ identity изменён` |
| CP-4 | Нижняя uncertainty → ниже threat | Если `a.confidence > b.confidence`, то `update_from_uncertainty(a)` генерирует меньший `threat_delta`, чем `update_from_uncertainty(b)` |
| CP-5 | Ниже velocity → ниже threat | Если `|flux_a.velocity| < |flux_b.velocity|`, то `update_from_flow(flux_a)` генерирует меньший `threat_delta`, чем `update_from_flow(flux_b)` |

**CP-1 и CP-2 — свойство однонаправленности:** ненадёжность и нестабильность только повышают угрозу, никогда не снижают (при положительной sensitivity). Снижение threat_level происходит только через decay_rate.

---

## 4. Негативные свойства (что система НЕ гарантирует)

| ID | Не-гарантия | Почему |
|---|---|---|
| NEG-1 | Uncertainty не может уменьшиться через одну операцию | Это верно для +, -, × (OP-1, OP-6). Но для деления на значение с малой uncertainty результат может иметь *меньшую* uncertainty, чем делимое. Это корректное поведение: точный делитель снижает неопределённость. |
| NEG-2 | Panic не может быть отменён после достижения порога | Panic детерминирован и необратим в рамках одного цикла. Это сделано намеренно (DR-007). |
| NEG-3 | FluxVar не гарантирует сходимость к какому-либо значению | В отличие от target-based модели, FluxVar не «стремится» никуда. Это свойство вызывающей стороны, не примитива (DR-008). |

---

## 5. Тестируемые спецификации (Test Specifications)

Каждый инвариант и свойство можно превратить в конкретный тест.

### 5.1 Пример: OP-1 (uncertainty не убывает при сложении)

```
GIVEN a = NoisyFloat(value=5.0, uncertainty=0.3, confidence=0.9)
  AND b = NoisyFloat(value=2.0, uncertainty=0.1, confidence=0.85)
WHEN  z = a + b
THEN  z.uncertainty ≥ max(a.uncertainty, b.uncertainty)
  AND z.uncertainty ≈ √(0.3² + 0.1²) ≈ 0.3162
```

### 5.2 Пример: OP-5 (корректность при нулевом значении)

```
GIVEN a = NoisyFloat(value=0.0, uncertainty=0.5, confidence=0.9)
  AND b = NoisyFloat(value=3.0, uncertainty=0.1, confidence=0.8)
WHEN  z = a * b
THEN  z.value == 0.0
  AND z.uncertainty ≈ |3.0| × 0.5 = 1.5
  AND z.confidence == 0.8
```

### 5.3 Пример: INV-S5 (детерминизм panic)

```
GIVEN survival = SurvivalState(threat_level=0.0, panic_threshold=0.75)
WHEN  survival.update(threat_delta=0.8)
THEN  survival.threat_level == 0.0   (сброшен panic-ом)
  AND survival._panic_count == 1
  AND survival.identity_hash ≠ initial_hash
```

### 5.4 Пример: CP-1 (uncertainty порождает threat)

```
GIVEN survival = SurvivalState(threat_level=0.0, panic_threshold=0.75)
  AND noisy_reliable = NoisyFloat(5.0, 0.1, confidence=0.95)
  AND noisy_unreliable = NoisyFloat(5.0, 0.1, confidence=0.3)
WHEN  survival.update_from_uncertainty(noisy_reliable, sensitivity=0.5)
THEN  threat_after_reliable = survival.threat_level   # (1-0.95)*0.5 = 0.025

WHEN  survival_2.update_from_uncertainty(noisy_unreliable, sensitivity=0.5)
THEN  threat_after_unreliable = survival_2.threat_level  # (1-0.3)*0.5 = 0.35
  AND threat_after_unreliable > threat_after_reliable
```

### 5.5 Пример: INV-F4 (update всегда устанавливает значение)

```
GIVEN flux = FluxVar(value=0.0, trauma_threshold=1.0)
WHEN  flux.update(new_value=100.0, dt=0.001)
THEN  flux.value == 100.0   (trauma произошла, но значение установлено)
```

---

## 6. Открытые вопросы по формализму

- **Коммутативность.** Для NoisyFloat: `a + b == b + a` по value и uncertainty? Да (сложение коммутативно). По confidence (min) — тоже. Но для последовательности операций над FluxVar порядок update-ов существенен (history зависит от порядка).
- **Ассоциативность.** `(a + b) + c` vs `a + (b + c)`: value — да (с точностью float). uncertainty — да (√(σ_a² + σ_b² + σ_c²) в обоих случаях). confidence — да (min ассоциативен).
- **Транзитивность panic.** Должен ли panic в одном scope каскадироваться в другой? Текущая спецификация определяет scope, но не каскадирование. Это открытый вопрос дизайна.
