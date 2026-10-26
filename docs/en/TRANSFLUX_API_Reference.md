> **Language:** English · [Русский](../ru/TRANSFLUX_API_Reference.md)

# TRANSFLUX API Reference

> A compact reference for the Python library (`src/transflux/`), October 2026.
> Full semantics and the reasons behind them are in the [specification](TRANSFLUX_Specification.md).

```python
from transflux import FluxVar, FlowingTrit, NoisyFloat, PolyphonicIdentity, SurvivalState, TransfluxSystem, classify_jump, weighted_mean
```

---

## FluxVar\<T\> — State Model (specification §1)

A variable as a channel: a value in motion, with history and inertia.

### Fields

| Field | Type | Default | Description |
|---|---|---|---|
| `value` | `T` | — | the current value |
| `velocity` | `float` | `0.0` | rate of change |
| `acceleration` | `float` | `0.0` | acceleration |
| `comfort` | `float` | `0.0` | `[-1.0, +1.0]`: dysphoria ↔ euphoria |
| `history` | `deque` | `maxlen=32` | previous values |
| `trauma_threshold` | `float` | `10.0` | trauma threshold on \|velocity\| |
| `on_trauma` | `Callable \| None` | `None` | callback `(flux, velocity) → None` |

### Methods

| Method | Returns | Description |
|---|---|---|
| `update(new_value, dt=1.0)` | `FluxVar[T]` | update the state; `dt ≤ 0` → `ValueError`; \|velocity\| > `trauma_threshold` → call `on_trauma` (the value is always set, INV-F4) |
| `flow(new_value, dt=1.0)` | `FluxVar[T]` | the same as `update`. The Python form of the `~>` operator; the operator itself is deferred together with the DSL |
| `trajectory()` | `List[T]` | history plus the current value |

There is no `constraints` layer: whether `value` is allowed is decided by the caller (DR-017).

`classify_jump(sensor, neighbors) → "calm" | "alone" | "shared"` — a jump relative to neighbors. A jump is `|velocity| > trauma_threshold` of that sensor. `alone` means there is a jump and no other sensor in the list confirms it. `sensor` itself does not count as a neighbor. State does not change (DR-022).

---

## FlowingTrit — a continuous trit (specification §1.4)

Poles `FlowingTrit.NEGATIVE` (`-1`), `LIMINAL` (`0`), `POSITIVE` (`+1`). The field `value: float` is stored as it is: `-0.5` is allowed, and a value outside `[-1, 1]` is not clipped (INV-T1).

| Method | Returns | Description |
|---|---|---|
| `float(trit)` | `float` | `value` itself |
| `nearest_pole()` | `float` | the nearest pole; on a tie, the earlier of `-1`, `0`, `+1`. Does not change the value |

Trajectory: `FluxVar(value=FlowingTrit(...))` and then `flow()`. `float(trit)` is what lets `FluxVar` compute velocity.

---

## NoisyFloat — Value Model (specification §2)

A value as a distribution: a center, an uncertainty, a trust.

### Fields

| Field | Type | Default | Description |
|---|---|---|---|
| `value` | `float` | — | center of the distribution (mean) |
| `uncertainty` | `float` | `0.0` | standard deviation (σ) |
| `confidence` | `float` | `1.0` | `[0.0, 1.0]`: degree of trust |

### Operations (propagation of uncertainty, first-order Taylor)

| Operation | Result σ | confidence |
|---|---|---|
| `a + b`, `a - b` | `√(σ_a² + σ_b²)` | `min(c_a, c_b)` |
| `a * b` | `√(b²·σ_a² + a²·σ_b²)` | `min(c_a, c_b)` |
| `a / b` | `√((σ_a/b)² + (a·σ_b/b²)²)`; `b.value ≈ 0` → `ZeroDivisionError` | `min(c_a, c_b)` |

### Methods

| Method | Returns | Description |
|---|---|---|
| `is_reliable(min_confidence=0.7)` | `bool` | `confidence ≥ min_confidence` |
| `gradient_of_truth()` | `float` | `confidence × (1 − e^(−SNR))`; when σ = 0 → `confidence` |

`weighted_mean(readings) → NoisyFloat` — the mean of independent readings of one quantity. Weight `1/σ²`. When every `σ > 0`: `uncertainty = 1/√(Σ 1/σ²)`, and confidence is the mean of the confidences with the same weights (DR-020). `σ = 0` takes all the weight; if the exact readings disagree, uncertainty is their root-mean-square spread and confidence is the `min` among them. An empty list → `ValueError`. The arithmetic of `+` and `/` does not give this weight.

---

## SurvivalState — Survival Model (specification §3)

A model of survival: continuous threat → a discrete rebirth (panic).

### Fields

| Field | Type | Default | Description |
|---|---|---|---|
| `threat_level` | `float` | `0.0` | `[0.0, 1.0]` |
| `panic_threshold` | `float` | `0.75` | threshold of the phase transition |
| `fallback` | `Any` | `None` | a safe state to fall back to |
| `scope` | `"local" \| "process" \| "system"` | `"local"` | the scale of panic effects |
| `identity_hash` | `str` | random SHA-256 | the current identity |
| `decay_rate` | `float` | `0.0` | threat decay per cycle |
| `on_panic` | `Callable \| None` | `None` | callback `(survival, old_hash) → None` |

### Methods

| Method | Returns | Description |
|---|---|---|
| `update(threat_delta)` | `bool` | apply decay and delta; `True` if panic fired |
| `update_from_uncertainty(noisy, sensitivity=0.5)` | `bool` | `threat_delta = (1 − confidence) × sensitivity` |
| `update_from_flow(flux, sensitivity=0.1)` | `bool` | `threat_delta = min(1, \|velocity\| × sensitivity)` |
| `is_safe()` | `bool` | `threat_level < panic_threshold × 0.5` |

Panic (internal `_panic()`): increment the counter, rotate `identity_hash`, reset `threat_level` to 0, call `on_panic`. Callbacks cannot cancel it (DR-013). It does not touch the masks of a `PolyphonicIdentity`.

---

## PolyphonicIdentity — masks (specification §3.4)

Several hashes of one entity. Panic does not rotate them until a callback asks (DR-023).

| Method | Returns | Description |
|---|---|---|
| `add(role)` | `str` | a new mask; a repeated role → `ValueError` |
| `alias(role, source)` | `str` | another reference to the hash of `source` |
| `present(role)` | `str` | the hash of that role |
| `grant(role, group)` | `None` | the role's current hash joins the group |
| `in_group(group)` | `bool` | whether a living mask is in the group; the role is not named |
| `holds(identity_hash)` | `bool` | whether any mask shows this hash |
| `erase(old_hash)` | `str` | every reference to the old hash becomes one new hash; an unknown hash → `KeyError` |
| `rotate_all()` | `dict` | each distinct hash is replaced; the old ones are gone from the book |

---

## TransfluxSystem — orchestrator (specification §4.2)

A recommended pattern, not part of the core. It couples the three axes in an explicit cycle.

| Field | Default | Description |
|---|---|---|
| `state: FluxVar` | — | the State axis |
| `survival: SurvivalState` | — | the Survival axis |
| `flow_sensitivity` | `0.1` | sensitivity of the State → Survival coupling |
| `uncertainty_sensitivity` | `0.5` | sensitivity of the Value → Survival coupling |
| `value: NoisyFloat \| None` | `None` | the latest Value observation, written in `tick` |
| `ticks` | `0` | how many times `tick` has been called |
| `peak_threat` | `0` | the greatest threat inside the cycle, before panic zeroes `threat_level` |
| `backup_value` | `None` | a reserve state; together with `backup_noisy` it arms the mode |
| `backup_noisy` | `None` | a reserve Value observation |
| `degraded` | `False` | the system listens to the backup pair, not to the `tick` input |

`tick(new_value, noisy_value, dt=1.0) → bool` — one cycle. If `degraded` and the backup pair is set, the input is substituted before `state.flow`. Then: store `value` → coupling → on panic, `state.flow(fallback)`. If this cycle panicked and the pair is set, `degraded` becomes `True`. Returns `True` if there was a panic.

`backup_armed() → bool` — both `backup_value` and `backup_noisy` are set. `recover()` clears `degraded`; the pair itself stays. Without an armed pair, panic does not latch (DR-021).

---

## Callbacks (Event Model, specification §4.3)

| Primitive | Callback | Signature | When |
|---|---|---|---|
| `FluxVar` | `on_trauma` | `(flux, velocity) → None` | \|velocity\| > `trauma_threshold` |
| `SurvivalState` | `on_panic` | `(survival, old_hash) → None` | `threat_level ≥ panic_threshold` |

They are called synchronously, they cannot cancel the operation, and when they are `None` the event is swallowed in silence.

---

Implementation guarantees: [Formal Invariants](TRANSFLUX_Formal_Invariants.md) (INV/OP/CP), checked by the tests in `tests/`.
