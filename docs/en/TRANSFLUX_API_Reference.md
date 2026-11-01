> **Language:** English · [Русский](../ru/TRANSFLUX_API_Reference.md)

# TRANSFLUX API Reference

> A compact reference for the Python library (`src/transflux/`), October 2026.
> Full semantics and the reasons behind them are in the [specification](TRANSFLUX_Specification.md).

```python
from transflux import (
    FluxVar, FlowingTrit, NoisyFloat, NoisyFlow,
    IdentityLedger, PolyphonicIdentity, ScarMemory,
    SurvivalState, TransfluxSystem, classify_jump, weighted_mean,
    stale_threat, uncertainty_margin_threat,
)
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
| `comfort` | `float` | `0.0` | `[-1.0, +1.0]`: dysphoria ↔ euphoria; moves on trauma/calm (DR-024) |
| `history` | `deque` | `maxlen=32` | previous values |
| `trauma_threshold` | `float` | `10.0` | trauma threshold on \|velocity\| |
| `trauma_comfort_cost` | `float` | `0.25` | how far comfort drops on trauma |
| `calm_comfort_gain` | `float` | `0.02` | how far comfort rises on a calm step |
| `on_trauma` | `Callable \| None` | `None` | callback `(flux, velocity) → None` |

### Methods

| Method | Returns | Description |
|---|---|---|
| `update(new_value, dt=1.0)` | `FluxVar[T]` | update the state; `dt ≤ 0` → `ValueError`; \|velocity\| > `trauma_threshold` → call `on_trauma` and lower comfort; otherwise raise comfort (the value is always set, INV-F4) |
| `flow(new_value, dt=1.0)` | `FluxVar[T]` | the same as `update`. The Python form of the `~>` operator; the operator itself is deferred together with the DSL |
| `trajectory()` | `List[T]` | history plus the current value |

There is no `constraints` layer: whether `value` is allowed is decided by the caller (DR-017). Rates of `0` freeze comfort as before.

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
| `float(noisy)` | `float` | the center (`value`); lets `FluxVar` / `NoisyFlow` compute velocity |

`NoisyFlow` — alias `FluxVar[NoisyFloat]`.

`weighted_mean(readings, *, correlation=0.0, covariance=None) → NoisyFloat` — the mean of readings of one quantity. Weight `1/σ²`. When every `σ > 0` and `correlation=0`: `uncertainty = 1/√(Σ 1/σ²)`, confidence is the weighted mean of confidences (DR-020). With `correlation=ρ ∈ [0,1]`, uncertainty becomes `σ_indep·√(1+(n−1)ρ)` and confidence blends toward `min` (DR-027). With `covariance=Σ` (n×n, diagonal = `σ²`), the GLS mean is used (DR-029); not together with `correlation ≠ 0`; not with exact `σ = 0` readings. `σ = 0` without covariance takes all the weight; if the exact readings disagree, uncertainty is their root-mean-square spread and confidence is the `min` among them. Bad shape / singular Σ / empty list / `ρ` outside `[0,1]` → `ValueError`. The arithmetic of `+` and `/` does not give this weight.

`stale_threat(elapsed, timeout, sensitivity=1.0) → float` — threat delta when a signal has been missing longer than `timeout`; `0` before the timeout; clipped to `1.0`.

`uncertainty_margin_threat(noisy, max_uncertainty, sensitivity=1.0) → float` — threat delta when `σ` exceeds the safety margin; `0` while within the limit.

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
| `on_panic_local` / `on_panic_process` / `on_panic_system` | `Callable \| None` | `None` | scope hook after `on_panic` (DR-025) |

### Methods

| Method | Returns | Description |
|---|---|---|
| `update(threat_delta)` | `bool` | apply decay and delta; `True` if panic fired |
| `update_from_uncertainty(noisy, sensitivity=0.5)` | `bool` | `threat_delta = (1 − confidence) × sensitivity` |
| `update_from_flow(flux, sensitivity=0.1)` | `bool` | `threat_delta = min(1, \|velocity\| × sensitivity)` |
| `is_safe()` | `bool` | `threat_level < panic_threshold × 0.5` |

Panic (internal `_panic()`): increment the counter, rotate `identity_hash`, reset `threat_level` to 0, call `on_panic`, then the matching scope hook if set. Callbacks cannot cancel it (DR-013). It does not touch the masks of a `PolyphonicIdentity`.

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
| `live()` (classmethod) | `list` | reachable books in the process (weak registry, DR-030) |
| `erase_live(old_hash)` (classmethod) | `str` | rewrite the hash in every live book that holds it; unknown → `KeyError` |

## IdentityLedger — several books (DR-026, DR-030)

Named books registered explicitly. An unregistered book is invisible to ordinary `erase`.

| Method | Returns | Description |
|---|---|---|
| `register(name, book=None)` | `PolyphonicIdentity` | add a book; a repeated name → `ValueError`; `book=None` creates an empty one |
| `book(name)` | `PolyphonicIdentity` | the book; missing name → `KeyError` |
| `names()` | `list` | registered names in insertion order |
| `holds(identity_hash)` | `bool` | whether any registered book contains the hash |
| `erase(old_hash, *, discovered=False)` | `str` | rewrite in registered books; with `discovered=True` also in live unregistered books (DR-030); unknown → `KeyError` |
| `rotate_all()` | `dict` | `{book_name: mapping}` for each book |

## ScarMemory — scars (DR-028)

Named places where a failure already hurt. Panic does not mark them; the caller does.

| Field / method | Default / returns | Description |
|---|---|---|
| `boost_factor` | `1.0` | how strongly intensity scales `amplify` |
| `max_scar` | `1.0` | cap on intensity per site |
| `mark(site, amount=0.25)` | `float` | accumulate scar; returns new intensity |
| `intensity(site)` | `float` | current depth; unknown site → `0` |
| `sites()` | `list` | sites with intensity `> 0` |
| `amplify(site, base)` | `float` | `base × (1 + boost_factor × intensity)` |
| `fade(amount=0.05)` | `None` | peel the same layer from every scar; zeros drop |

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
| `signal_timeout` | `None` | if set with `signal_age` on `tick`, apply `stale_threat` |
| `stale_sensitivity` | `1.0` | sensitivity of the stale helper |
| `uncertainty_limit` | `None` | if set, apply `uncertainty_margin_threat` to the observation |
| `margin_sensitivity` | `1.0` | sensitivity of the margin helper |

`tick(new_value, noisy_value, dt=1.0, *, signal_age=None) → bool` — one cycle. If `degraded` and the backup pair is set, the input is substituted before `state.flow`. Then: store `value` → coupling → optional stale/margin threat → on panic, `state.flow(fallback)`. If this cycle panicked and the pair is set, `degraded` becomes `True`. Returns `True` if there was a panic.

`backup_armed() → bool` — both `backup_value` and `backup_noisy` are set. `recover()` clears `degraded`; the pair itself stays. Without an armed pair, panic does not latch (DR-021).

---

## Callbacks (Event Model, specification §4.3)

| Primitive | Callback | Signature | When |
|---|---|---|---|
| `FluxVar` | `on_trauma` | `(flux, velocity) → None` | \|velocity\| > `trauma_threshold` |
| `SurvivalState` | `on_panic` | `(survival, old_hash) → None` | `threat_level ≥ panic_threshold` |
| `SurvivalState` | `on_panic_local` / `process` / `system` | `(survival, old_hash) → None` | after `on_panic`, only the hook matching `scope` |

They are called synchronously, they cannot cancel the operation, and when they are `None` the event is swallowed in silence.

---

Implementation guarantees: [Formal Invariants](TRANSFLUX_Formal_Invariants.md) (INV/OP/CP), checked by the tests in `tests/`.
