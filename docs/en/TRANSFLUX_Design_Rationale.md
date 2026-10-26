> **Language:** English · [Русский](../ru/TRANSFLUX_Design_Rationale.md)

# TRANSFLUX: Design Rationale

> The reasons behind the key design decisions.
> For each decision: the context, the alternatives, the argument.

---

## DR-001. Three axes, not two and not four

**Context.** Why exactly three axes — State, Value, Survival? Why not add Logic, Identity, and Time as axes of their own?

**Decision.** Three axes = a minimally complete basis.

**Argument.**

*Orthogonality:* no axis reduces to another. FluxVar can work without NoisyFloat (an exact value with history). NoisyFloat can work without FluxVar (a point value with uncertainty). SurvivalState can work without either (an external threat_level).

*Completeness:* every proposed fourth axis follows from the existing three:

- Logic (Gradient of Truth) → derived from NoisyFloat.gradient_of_truth()
- Identity (Polyphonic Identity) → derived from SurvivalState.identity_hash
- Time → built into FluxVar.history and FluxVar.velocity

*Necessity:* removing any axis leaves a fundamental question unanswered:

- Without State → there is no model of change
- Without Value → there is no model of uncertainty
- Without Survival → there is no model of behavior under threat

**Status.** A working hypothesis. If a question appears that the three axes do not cover and that does not follow from them, the basis must be revisited.

---

## DR-002. min() for propagation of confidence

**Context.** When operating on NoisyFloat, how should the confidence of the two operands be combined?

**Decision.** `result.confidence = min(a.confidence, b.confidence)`.

**Alternatives.**

| Strategy | Formula | Advantages | Disadvantages |
|---|---|---|---|
| min (weakest link) | min(c₁, c₂) | Conservative, simple | Can be too pessimistic |
| Multiplicative | c₁ × c₂ | Accounts for independence | Assumes an independence that is not always there; collapses toward 0 quickly |
| Bayesian | f(c₁, c₂, prior) | The most correct | Needs a prior; too complex for a primitive |

**Argument.** For a type primitive, predictability and safety matter more than precision. min() guarantees that the result's confidence never exceeds the confidence of the worse operand — this is conservative, and it does not lie. In a specific domain implementation the strategy can be overridden.

---

## DR-003. decay_rate defaults to 0

**Context.** Without decay, threat_level grows monotonically. The system will enter panic under any non-zero threat — this is a "paranoid" mode.

**Decision.** By default decay_rate = 0. Decay is turned on explicitly.

**Argument.** In a survival model it is safer to err toward too much vigilance. An optimistic default (threat dissolves by itself) can let a real threat "leak" through small deltas and never reach the threshold. A paranoid default forces the developer to choose, deliberately, a decay_rate that fits their context.

---

## DR-004. comfort is a scalar [-1, +1], not a vector

**Context.** Comfort reflects the system's "well-being". It could be a multidimensional quantity: comfort of speed, of stability, of load.

**Decision.** A scalar ∈ [-1, +1]. -1 = dysphoria, 0 = neutral, +1 = euphoria.

**Argument.** For a Core primitive a scalar is enough: it allows threshold decisions (`if comfort < -0.5: ...`) and a hand-off to the other axes. A multidimensional comfort adds complexity (which dimension? which normalization? which measurements?) without solving problems the scalar does not already solve at the level of the core. Extending it to a `ComfortVector` is a matter for later versions, if practice shows the need.

---

## DR-005. trauma_threshold is one number, not a function of context

**Context.** The "trauma" threshold is the rate of change at which the system signals an anomaly. The threshold can depend on context: one value by day, another by night.

**Decision.** One number (a float), modifiable at runtime.

**Argument.** Simplicity, determinism, testability. One threshold is easy to verify: "when velocity > 10.0 → trauma". A contextual function (`trauma_threshold = f(time, load, history)`) can be implemented by the caller, who updates the threshold before each cycle. The basic primitive should not contain logic that is simpler to express outside it.

---

## DR-006. A ring buffer of maxlen=32 for history

**Context.** FluxVar stores a history of states in a ring buffer. What size?

**Decision.** 32 elements by default, configurable.

**Argument.** A trade-off: the memory is enough to detect patterns (a trend, an oscillation, a return to a previous state) in most time series. At an update rate of 1/s this is 32 seconds of context. At 1/min, about 30 minutes. A power of two is not essential in Python, but it is convenient if the code is later moved to embedded systems or Rust. For a specific domain, maxlen is set when the FluxVar is created.

---

## DR-007. Panic is deterministic, not probabilistic

**Context.** Could panic be probabilistic: "at threat=0.8, a 30% chance of panic"?

**Decision.** No. Panic is strictly deterministic: threat ≥ threshold → panic. Always.

**Argument.** Panic is a **safety guarantee**. It must be:

- *Reproducible* — the same input → the same result;
- *Testable* — a unit test can check that at threat=0.75 and threshold=0.75 panic fires;
- *Predictable* — in a real threat you cannot depend on a random-number generator.

A probabilistic panic turns a safety guarantee into a gamble. That contradicts the basic principle of the Survival Model.

---

## DR-008. FluxVar.update takes new_value, not a target

**Context.** An early experiment (`research/notes/TRANSFLUX.py`) used a spring model: FluxVar had a `target` field, and the value "strove" toward the goal through spring dynamics with acceleration and damping.

**Decision.** Specification v0.2 uses a direct `update(new_value)`: the caller passes the new value, and FluxVar records the delta, the velocity, and the acceleration.

**Alternative.** Target-based: `set_target(target)` + `tick(dt)` — FluxVar itself moves smoothly toward the goal.

**Argument.** `update(new_value)` is the more general model. It does not impose a physics of convergence (a spring, a damper, an exponential). The caller decides what the trajectory is. A target-based model is a special case that can be built on top of `update()`:

```python
def tick_towards_target(flux, target, dt, spring_k=0.5):
    error = target - flux.value
    new_value = flux.value + spring_k * error * dt
    flux.update(new_value, dt)
```

The basic primitive should not restrict the space of possible dynamics.

---

## DR-009. NoisyFloat stores σ (std dev), not σ² (variance)

**Context.** Uncertainty can be stored as a standard deviation (σ) or as a variance (σ²).

**Decision.** σ (std dev) is stored.

**Argument.**

| Storage | Advantages | Disadvantages |
|---|---|---|
| σ (std dev) | Readable: "5.0 ± 0.3" is intuitive; the units match value | Propagation through addition and subtraction needs σ² → one squaring |
| σ² (variance) | Propagation is cheaper: σ²_z = σ²_a + σ²_b, no sqrt | Unreadable: "5.0 ± 0.09" — in which units? The units do not match value |

For a conceptual primitive, readability matters more than micro-optimizations. `NoisyFloat(5.0 ± 0.3)` is a statement that is clear without an explanation.

---

## DR-010. The axes are orthogonal, and they are coupled

**Context.** Orthogonality usually implies independence. In TRANSFLUX the axes interact: uncertainty affects threat, velocity affects threat, panic resets state.

**Decision.** Orthogonality is not independence. The axes are orthogonal by definition (they do not reduce to each other), and they are coupled in behavior (coupling rules).

**Argument.** An analogy: in physics the electric and magnetic fields are orthogonal components, and they are coupled through Maxwell's equations. A change in one produces the other. It is the coupling that produces emergent behavior (an electromagnetic wave).

In TRANSFLUX the coupling of the axes produces a self-observing system: instability on one axis (high uncertainty, a sharp velocity) automatically raises vigilance on another (threat_level). Without the coupling, the axes are simply three independent libraries. With the coupling, they are a dynamical system.

The coupling rules are fixed in specification §4 and are as much a part of the core as the axes themselves.

---

## DR-011. Consent-First for destructive operations

**Context.** Panic can destroy data and change identity. Should that happen automatically?

**Decision.** Destructive operations require an explicit policy. There is no default "yes".

**Argument.** Destroying data automatically, without an explicit policy, is a side effect disguised as safety. In a real system, destroying data can be a catastrophe (medical records, legal documents). Consent-First means: the developer explicitly defines what is destroyed on panic, in which scope, and at which threshold — and takes responsibility for that decision.

---

## DR-012. One formula for the paradigm

**Context.** Is "one line" that describes the whole paradigm needed?

**Decision.** `TRANSFLUX = Flow(State) · Uncertainty(Value) · Adaptation(Survival)`

**Argument.** The formula does three jobs:

1. *A mnemonic* — it is remembered from one reading.
2. *A completeness criterion* — any new idea can be checked: does it follow from one of the three terms?
3. *The operator · (a product)* — not +, but ·. The axes are not added (additivity = optionality). They are multiplied (multiplicativity = each one is necessary). A system missing any of the three factors goes to zero.

The choice of the symbol · is deliberate: it stresses that removing one axis zeroes the whole paradigm.

---

## DR-013. Trauma and panic are advisory, not blocking

**Context.** Can trauma_threshold or the on_trauma callback block `FluxVar.update()`? Can panic be cancelled?

**Decision.** No. Both events are **advisory**: they signal, and they do not cancel the operation.

**Argument.**

- `FluxVar.update()` **always** sets the new value. The trauma callback is called before the assignment, and it cannot prevent it. This guarantees INV-F4: `value == new_value` after update.
- `SurvivalState._panic()` **always** resets threat and rotates identity. The on_panic callback is called after the rebirth, and it cannot cancel it. This guarantees INV-S2 and INV-S5.

If a callback could block the operation, the primitive would stop being predictable: behavior would depend on outside code. That breaks the principle of determinism (DR-007) and makes the invariants unprovable.

Callbacks **may** have side effects (logging, escalation into SurvivalState, notifying the orchestrator), but the control flow inside the primitive is unconditional.

---

## DR-014. An orchestrator pattern for coupling the axes

**Context.** How are the three axes coupled? Automatically (internal references) or explicitly (an external orchestrator)?

**Decision.** An explicit orchestrator. The primitives do not know about each other.

**Argument.**

*Orthogonality:* if SurvivalState holds a reference to FluxVar, they stop being orthogonal — Survival depends on State.

*Testability:* each primitive is tested in isolation. FluxVar does not need SurvivalState for a unit test.

*Flexibility:* the orchestrator decides:

- which axes to couple (not every system uses all three);
- in which order to update;
- what to do with fallback after panic;
- which sensitivity parameters to use.

The `TransfluxSystem` pattern (specification §4.2) is recommended, not required. Calling code may couple the axes directly.

---

## DR-015. Package layout: one module with three classes

**Context.** How should the implementation code be organized?

**Decision.** One package, `transflux`, with submodules:

```
transflux/
├── __init__.py          # re-export: FluxVar, NoisyFloat, SurvivalState
├── state.py             # FluxVar
├── value.py             # NoisyFloat
├── survival.py          # SurvivalState
└── system.py            # TransfluxSystem (orchestrator)
```

**Argument.**

- One package (`pip install transflux`) — a low barrier to entry.
- Submodules by axis — a clean split; orthogonality is reflected in the structure.
- `system.py` is separate from the primitives — the orchestrator is optional.
- `__init__.py` re-exports the three classes: `from transflux import FluxVar, NoisyFloat, SurvivalState`.

**Alternative.** Three separate packages (`transflux-state`, `transflux-value`, `transflux-survival`). Rejected: it complicates installation and versioning, and it breaks the coupling protocol.

---

## DR-016. min() stays the library's strategy

**Context.** Open question §8: keep `min`, or move to a multiplicative or Bayesian transfer of confidence.

**Decision.** The Python library keeps `min`. Other strategies are not implemented until practice with the library shows that the weakest link is not enough.

**Argument.** Simplicity and predictability matter more than a finer formula that there is nothing yet to check it against. This does not cancel DR-002. It closes it as a question.

---

## DR-017. FluxVar has no constraints layer

**Context.** Drafts recorded state as `(value, velocity, history, constraints)` and asked whether the primitive itself should reject values that are not allowed.

**Decision.** It should not. Whether `value` is allowed is decided by the programmer.

**Argument.** A check inside the channel would make the primitive a guardian of the calling code. On this point TRANSFLUX is closer to assembly: a wrong value is the fault of whoever wrote it. The library computes velocity and stores history. It does not decide whether a number "has the right" to be what it is.

The `comfort` field still lies in `[-1, +1]` — that is the definition of the field itself (INV-F1), not a policy of allowed payload values.

---

## DR-018. FlowingTrit is a float, not a discrete triple

**Context.** The trit could have stayed the set `{-1, 0, +1}`, with the transition between labels drawn separately.

**Decision.** The state itself is a floating-point number. `-1`, `0`, and `+1` are poles of meaning. `-0.5` is a full value. There is no clamp to the segment `[-1, 1]` (see DR-017).

**Argument.** A discrete triple pretends again that the space between "no", "maybe", and "yes" is empty. A continuous trit is exactly about that "between". The transition vector is the `velocity` of `FluxVar[FlowingTrit]`, not a hidden coordinate sitting next to a label.

---

## DR-019. The Python library comes first

**Context.** The roadmap used to call for a DSL/LUMEN, Rust, and neuromorphic hardware all at once.

**Decision.** The carrier of the paradigm right now is the Python package `transflux` and the orchestrator `TransfluxSystem`. The `~>` operator is not made into language syntax: in the library it is the method `flow()`. A DSL, LUMEN, and Rust are deferred. Benchmarks, neurochips, and the research backlog are deferred too — the concept is not yet checked by code one can use.

**Argument.** Until the three axes can be assembled in ordinary Python and one can see that the system really flows, doubts, and enters panic, any other stack is discussing the form and not the idea. If the library confirms the concept, the next horizon is more likely embedding and microcontrollers; the concrete tools are chosen again at that time.

By October 2026 that run exists: the synthetic scenarios in `tests/synthetic/`. A DSL, Rust, benchmarks, and neuromorphic hardware remain deferred.

---

## DR-020. The confidence of a mean of readings is weighted, not taken as min

**Context.** The air-sensor network scenario needs a weight of `1/σ²`: a precise sensor matters more than a noisy one. The arithmetic of `+` and `/` does not do that. If `min` is still applied to the confidence of a weighted mean, a sensor with a huge `σ` and a low confidence would veto the result, even though it barely moved the value.

**Decision.** `weighted_mean` computes value and uncertainty by inverse variance. Confidence is the mean of the confidences with the same weights. `min` remains the rule for `+`, `-`, `*`, `/` (DR-016).

**Argument.** These are different operations. Addition carries the doubt of the weakest link, because both summands enter the result in full. In a mean of independent readings, a noisy one almost drops out of the sum of weights, and honesty is that confidence follows the weight, not the weakest instrument on the list.

---

## DR-021. Backup mode only from an explicit pair

**Context.** After panic the orchestrator rolls state back to `fallback` for one cycle, and the next `tick` listens to the input again. If the input is still bad, panic repeats. The ward scenario wants something else: switch to a backup sensor and stay with it.

**Decision.** The `degraded` mode turns on at the moment of panic and then substitutes the input, but only when both fields were set in advance: `backup_value` and `backup_noisy`. `recover()` turns the mode off. A pair that is only half set does not arm the mode.

**Argument.** A spontaneous "I am in safe mode now" would be a hidden policy. The orchestrator has no backup sensor until one is named. Until the pair is set, a repeated panic is honest behavior: the threat has not gone away.

---

## DR-022. Classifying a jump does not touch confidence

**Context.** The air scenario distinguishes a fault in one sensor from a cloud that the neighbors also see. `weighted_mean` does not help with that: if the lie has a small σ, its weight is large.

**Decision.** `classify_jump` answers `calm`, `alone`, or `shared`, and does nothing else. The threshold is the same as trauma: strictly greater than `trauma_threshold`.

**Argument.** "This is a fault, lower its trust" is a decision of the scenario, not a law of the channel. The library shows whether one sensor jerked or several did. How far to widen uncertainty after that is decided by the calling code.

---

## DR-023. Masks do not rotate together with panic by themselves

**Context.** An entity can have several names: a public one, a newsroom one, a name for a source. Under threat the old names have to be removed from every reference at once. If that is wired into `SurvivalState._panic()`, any alarm will tear the masks off, even when the calling code did not ask for it.

**Decision.** The book of masks is a separate object, `PolyphonicIdentity`. `erase` replaces one hash everywhere inside the book. `rotate_all` does this for every mask. `SurvivalState` does not hold them. The link to panic is only a callback that itself calls `rotate_all`.

**Argument.** Erasing a name is irreversible. Consent-First already requires that such an action be an explicit policy. A book that was not passed into the callback keeps its hashes: an alarm in one circuit does not burn out the neighboring one.
