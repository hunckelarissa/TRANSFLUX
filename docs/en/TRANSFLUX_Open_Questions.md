> **Language:** English · [Русский](../ru/TRANSFLUX_Open_Questions.md)

# TRANSFLUX: decisions, and what is deferred

A journal as of October 2026. The reasons are DR-016…DR-023 in `TRANSFLUX_Design_Rationale.md`.

There are no open questions that block writing the library. The concept has been run through synthetic scenarios (`tests/synthetic/`, charts in `docs/figures/synthetic/`). Other stacks remain deferred.

---

## Decided

### 1.1 Confidence propagates through `min()`

On addition, subtraction, multiplication, and division of `NoisyFloat`, the result's confidence equals the confidence of the weakest operand.

Multiplicative and Bayesian formulas are not in the library. They can be revisited only if, on live scenarios, `min()` turns out to be too coarse.

### 1.2 `FluxVar` does not check whether a value is allowed

There will be no `constraints` field. The programmer decides which `value` to write. The library computes velocity, acceleration, and history, and it does not stop the write.

This is a deliberately hard position: a wrong value is the fault of whoever passed it. The `comfort` field still lies on the segment from `-1` to `+1` — that is how the field itself is defined, not a check of the payload.

### 1.3 `FlowingTrit` is a floating-point number

The poles `-1`, `0`, and `+1` give the meaning: negation, threshold, affirmation. The state itself is a `float`. `-0.5` is an ordinary value. The library does not round it to the nearest label and does not clip numbers outside `[-1, 1]`.

The trajectory comes from a `FluxVar` that holds a `FlowingTrit`. The rate of change is the transition vector.

### 2.1 The orchestrator exists

`TransfluxSystem.tick()` does this in one cycle:

1. if backup mode is on, it substitutes the input with `backup_value` and `backup_noisy`;
2. it moves state to the new value (`flow`);
3. it stores the latest `NoisyFloat`;
4. it raises threat from a sharp velocity and from low confidence;
5. if panic happened and `fallback` is set, it moves state to that fallback;
6. if panic happened and the backup pair was set in advance, it leaves `degraded` on.

`recover()` listens to the input again. Without a complete pair the mode does not latch (DR-021). The primitives still do not reference each other.

### 2.2 The carrier of the paradigm is the Python library

The `transflux` package. Flow is written like this:

```python
from transflux import FluxVar, FlowingTrit, NoisyFloat, SurvivalState, TransfluxSystem

flux = FluxVar(value=FlowingTrit(0.0))
flux.flow(FlowingTrit(-0.5))
```

`flow()` is the Python form of the `~>` operator. A separate syntax is not being built.

There is nowhere to go without this library: it is what checks whether the concept is alive.

### What has already grown on top of these decisions

The synthetic scenarios, and the code that grew out of them:

- `weighted_mean` — weight `1/σ²`; the mean's confidence follows the weight, not `min` (DR-020);
- the orchestrator's backup mode (DR-021);
- `classify_jump` — `calm` / `alone` / `shared`, without editing confidence (DR-022);
- `PolyphonicIdentity` — masks, `erase`, `rotate_all`; panic does not rotate them until a callback asks (DR-023).

---

## Deferred

The synthetic check exists. Other hardware and other syntax are still not in the work.

### Syntax and other languages

- The `~>` operator as part of a language, a DSL, and a LUMEN variant.
- A Rust implementation.

If the synthetic check is enough, the likely next horizon is embedding and microcontrollers. The stack there will be decided then, not from today's list.

### Research and validation

- Benchmarks against "ordinary" computation.
- Porting the primitives onto neuromorphic chips.
- Wrappers for PyTorch and TensorFlow.

It is early to measure performance and to think about neurochips: the check is still synthetic, not on the target hardware.

### The far backlog

Not in the near work, and not in the core:

- Grief-Driven GC — garbage collection as a protocol of loss;
- Scar Memory — stronger checks where panic has already happened;
- Dysphoric Compiler — diagnosing the "discomfort" of code;
- Time-Native Programming — time as a language object;
- and the other ideas on the roadmap (Chosen Family Topology, Body-Budget Scheduler, Liminal Type Inference, Euphoria-Driven Optimization, Algebra of Change).
