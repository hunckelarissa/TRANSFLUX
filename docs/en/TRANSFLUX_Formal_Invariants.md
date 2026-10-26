> **Language:** English · [Русский](../ru/TRANSFLUX_Formal_Invariants.md)

# TRANSFLUX: Formal properties and invariants

> Guarantees that a TRANSFLUX-compatible implementation must provide.
> Each property is stated as a claim that a test can check.

---

## 1. Type invariants

Properties that must hold **always**, for any instance.

### 1.1 NoisyFloat

| ID | Invariant | Statement |
|---|---|---|
| INV-N1 | Non-negative uncertainty | `uncertainty ≥ 0` |
| INV-N2 | Bounded confidence | `0 ≤ confidence ≤ 1` |
| INV-N3 | Consistency of gradient_of_truth | `0 ≤ gradient_of_truth() ≤ confidence` |

**Why INV-N3:** `gradient_of_truth() = confidence × (1 - e^(-SNR))`. Since `0 ≤ (1 - e^(-SNR)) ≤ 1` for `SNR ≥ 0`, the result is bounded above by confidence and below by zero.

### 1.2 FluxVar

| ID | Invariant | Statement |
|---|---|---|
| INV-F1 | Bounded comfort | `-1 ≤ comfort ≤ 1` |
| INV-F2 | Bounded history | `len(history) ≤ maxlen` |
| INV-F3 | Consistency of trajectory | `trajectory() == list(history) + [value]` |
| INV-F4 | The value is updated | After `update(v, dt)`: `value == v` |
| INV-F5 | Consistency of velocity | After `update(v, dt)`: `velocity == (v - old_value) / dt` |

**Why INV-F4:** update always sets the new value. Trauma is a signal, not a block. This is a design decision (see DR-013): callbacks may log or escalate, and they cannot cancel the update.

### 1.3 SurvivalState

| ID | Invariant | Statement |
|---|---|---|
| INV-S1 | Bounded threat_level | `0 ≤ threat_level ≤ 1` |
| INV-S2 | Reset on panic | After `_panic()`: `threat_level == 0` |
| INV-S3 | Uniqueness of identity | After `_panic()`: `identity_hash ∉ {previous identity_hash}` (with cryptographic probability) |
| INV-S4 | Monotonic panic_count | `_panic_count` does not decrease |
| INV-S5 | Determinism of panic | `threat_level ≥ panic_threshold` ↔ panic fires |

### 1.4 FlowingTrit

| ID | Invariant | Statement |
|---|---|---|
| INV-T1 | The value is not quantized and not clamped | `FlowingTrit(x).value == x` and `float(FlowingTrit(x)) == x` |

**Why INV-T1:** the poles `-1`, `0`, `+1` are landmarks of meaning, not the set of allowed states (DR-018). An intermediate `-0.5` and a value outside `[-1, 1]` are kept as written (DR-017).

---

## 2. Operation properties

Guarantees provided by the arithmetic operations on NoisyFloat.

### 2.1 Addition and subtraction

For `z = a ± b`:

| ID | Property | Statement | Proof |
|---|---|---|---|
| OP-1 | Uncertainty does not decrease | `z.uncertainty ≥ max(a.uncertainty, b.uncertainty)` | `√(σ_a² + σ_b²) ≥ max(σ_a, σ_b)`, because `x² + y² ≥ max(x, y)²` |
| OP-2 | Confidence does not increase | `z.confidence ≤ min(a.confidence, b.confidence)` | By definition: `min(c_a, c_b) ≤ min(c_a, c_b)` |
| OP-3 | The value is exact | `z.value == a.value ± b.value` | Arithmetic without rounding (within float precision) |

**OP-1 is the key property.** It guarantees that **uncertainty cannot disappear** during computation. The system does not lose information about the quality of the data.

### 2.2 Multiplication

For `z = a × b`:

| ID | Property | Statement |
|---|---|---|
| OP-4 | The uncertainty formula | `z.uncertainty == √(b²·σ_a² + a²·σ_b²)` |
| OP-5 | Correctness at zero | If `a.value == 0`: `z.uncertainty == |b| × σ_a` (the formula stays correct) |
| OP-6 | An upper bound on relative uncertainty | For `a, b ≠ 0`: `z.σ_rel ≤ a.σ_rel + b.σ_rel`, where `σ_rel = uncertainty / |value|` |

**Why OP-6:** `√(x² + y²) ≤ x + y` for `x, y ≥ 0` (because `(x+y)² = x² + 2xy + y² ≥ x² + y²`). The relative uncertainty of a product is bounded by the sum of the relative uncertainties of the factors.

### 2.3 Division

For `z = a / b` (when `b.value ≠ 0`):

| ID | Property | Statement |
|---|---|---|
| OP-7 | The uncertainty formula | `z.uncertainty == √((σ_a/b)² + (a·σ_b/b²)²)` |
| OP-8 | Division by a zero value | `b.value ≈ 0` → `ZeroDivisionError` |

### 2.4 Weighted mean

For `weighted_mean` of independent readings with `σ > 0`:

| ID | Property | Statement |
|---|---|---|
| OP-9 | The uncertainty formula | `σ = 1 / √(Σ 1/σ_i²)` |
| OP-10 | An exact reading dominates | A participant with `σ = 0` sets the value; participants with `σ > 0` do not move it |
| OP-11 | Empty input | An empty list → `ValueError` |

Confidence here is a weighted mean of the confidences, not `min` (DR-020). The exception: if the value is determined only by readings with `σ = 0`, the result's confidence is the `min` among them.

---

## 3. Coupling properties

Guarantees of behavior when the axes interact.

| ID | Property | Statement |
|---|---|---|
| CP-1 | Monotonicity of uncertainty → threat | `update_from_uncertainty(noisy)`: `threat_delta = (1 - confidence) × sensitivity ≥ 0` when `sensitivity ≥ 0` |
| CP-2 | Monotonicity of velocity → threat | `update_from_flow(flux)`: `threat_delta = min(1, |velocity| × sensitivity) ≥ 0` when `sensitivity ≥ 0` |
| CP-3 | Panic → a safe state | After panic: `threat_level == 0 ∧ identity has changed` |
| CP-4 | Higher confidence → lower threat | If `a.confidence > b.confidence`, then `update_from_uncertainty(a)` generates a smaller `threat_delta` than `update_from_uncertainty(b)` |
| CP-5 | Lower velocity → lower threat | If `|flux_a.velocity| < |flux_b.velocity|`, then `update_from_flow(flux_a)` generates a smaller `threat_delta` than `update_from_flow(flux_b)` |

**CP-1 and CP-2 are a one-direction property:** unreliability and instability only raise threat, they never lower it (at a positive sensitivity). `threat_level` falls only through `decay_rate`.

---

## 4. Negative properties (what the system does NOT guarantee)

| ID | Non-guarantee | Why |
|---|---|---|
| NEG-1 | Uncertainty cannot decrease through a single operation | This is true for +, -, × (OP-1, OP-6). For division by a value with a small uncertainty, the result can have a *smaller* uncertainty than the dividend. This is correct behavior: a precise divisor reduces uncertainty. |
| NEG-2 | Panic cannot be cancelled after the threshold is reached | Panic is deterministic and irreversible within one cycle. This is intentional (DR-007). |
| NEG-3 | FluxVar does not guarantee convergence to any value | Unlike a target-based model, FluxVar does not "strive" anywhere. That is a property of the caller, not of the primitive (DR-008). |

---

## 5. Test specifications

Every invariant and property can be turned into a concrete test.

### 5.1 Example: OP-1 (uncertainty does not decrease on addition)

```
GIVEN a = NoisyFloat(value=5.0, uncertainty=0.3, confidence=0.9)
  AND b = NoisyFloat(value=2.0, uncertainty=0.1, confidence=0.85)
WHEN  z = a + b
THEN  z.uncertainty ≥ max(a.uncertainty, b.uncertainty)
  AND z.uncertainty ≈ √(0.3² + 0.1²) ≈ 0.3162
```

### 5.2 Example: OP-5 (correctness at a zero value)

```
GIVEN a = NoisyFloat(value=0.0, uncertainty=0.5, confidence=0.9)
  AND b = NoisyFloat(value=3.0, uncertainty=0.1, confidence=0.8)
WHEN  z = a * b
THEN  z.value == 0.0
  AND z.uncertainty ≈ |3.0| × 0.5 = 1.5
  AND z.confidence == 0.8
```

### 5.3 Example: INV-S5 (determinism of panic)

```
GIVEN survival = SurvivalState(threat_level=0.0, panic_threshold=0.75)
WHEN  survival.update(threat_delta=0.8)
THEN  survival.threat_level == 0.0   (reset by panic)
  AND survival._panic_count == 1
  AND survival.identity_hash ≠ initial_hash
```

### 5.4 Example: CP-1 (uncertainty produces threat)

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

### 5.5 Example: INV-F4 (update always sets the value)

```
GIVEN flux = FluxVar(value=0.0, trauma_threshold=1.0)
WHEN  flux.update(new_value=100.0, dt=0.001)
THEN  flux.value == 100.0   (trauma happened, and the value was set)
```

---

## 6. Open questions of the formalism

- **Commutativity.** For NoisyFloat: does `a + b == b + a` in value and uncertainty? Yes (addition is commutative). In confidence (`min`) — also yes. For a sequence of operations on FluxVar, the order of updates matters (history depends on order).
- **Associativity.** `(a + b) + c` versus `a + (b + c)`: value — yes (within float precision). uncertainty — yes (`√(σ_a² + σ_b² + σ_c²)` in both cases). confidence — yes (`min` is associative).
- **Transitivity of panic.** Should panic in one scope cascade into another? The current specification defines scope, and it does not define cascading. This is an open design question.
