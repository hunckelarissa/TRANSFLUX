> **Language:** English · [Русский](../ru/TRANSFLUX_Anti_Patterns.md)

# TRANSFLUX: Anti-patterns

> How **not** to use TRANSFLUX.
> Typical mistakes and traps when working with the paradigm.

---

## AP-01. Wrapping everything in NoisyFloat

**The mistake.** Applying NoisyFloat to values that are known exactly:

```python
pi = NoisyFloat(3.14159, uncertainty=0.0, confidence=1.0)
```

**Why this is bad.** A NoisyFloat with `uncertainty=0` and `confidence=1.0` is an ordinary float with extra fields. There is overhead and no gain. NoisyFloat matters when a value really carries uncertainty: sensor readings, model outputs, external data.

**Rule.** Use NoisyFloat only for values whose exactness is in doubt.

---

## AP-02. Setting trauma_threshold = 0

**The mistake.** Setting the trauma threshold to zero in order to "catch every change":

```python
flux = FluxVar(value=0.0, trauma_threshold=0.0)
```

**Why this is bad.** Any non-zero update fires the trauma callback. At a high update rate (IoT, streaming) this produces thousands of false signals per second — the analogue of alarm fatigue in medicine.

**Rule.** `trauma_threshold` should reflect a real anomaly threshold for the specific domain. If you do not know what to set, start from the median of the velocities you expect.

---

## AP-03. Using panic as control flow

**The mistake.** Deliberately driving the system into panic in order to "reboot":

```python
survival.update(threat_delta=1.0)  # force panic to "reset"
```

**Why this is bad.** Panic is an **emergency** phase transition for a real threat. It rotates `identity_hash` (cryptographically expensive), resets state, and increments `panic_count`. Using it as a stand-in for `restart()`:

- wipes identity for no reason;
- makes `panic_count` meaningless;
- trains the system (and the developer) not to distinguish "a normal reset" from "a real threat".

**Rule.** For a normal reset, use `flux.update(initial_value)` and `survival.threat_level = 0`. Panic is only for an actual panic.

---

## AP-04. Ignoring confidence when deciding

**The mistake.** Using `NoisyFloat.value` without checking `confidence`:

```python
if sensor.value > threshold:  # bad: confidence ignored
    activate_alarm()
```

**Why this is bad.** This destroys the point of NoisyFloat. The whole Value Model is built on decisions that scale with trust. A binary comparison is a return to the classical world.

**Rule.** Use `gradient_of_truth()` or an explicit confidence check:

```python
if sensor.gradient_of_truth() > 0.7:
    activate_alarm()
# or
if sensor.value > threshold and sensor.is_reliable():
    activate_alarm()
```

---

## AP-05. Coupling the axes without an orchestrator

**The mistake.** Calling `survival.update_from_flow(flux)` from FluxVar's own callback, which creates recursion:

```python
def on_trauma(flux, velocity):
    survival.update_from_flow(flux)       # may cause panic
    if panicked:
        flux.update(survival.fallback)    # calls update → may call on_trauma again
```

**Why this is bad.** Cyclic calls, loss of control over update order, behavior that cannot be reproduced.

**Rule.** Use the orchestrator pattern (`TransfluxSystem` or an explicit cycle). Callbacks are for logging and notification, not for mutating state.

---

## AP-06. Forgetting about decay_rate

**The mistake.** Leaving `decay_rate = 0` in a long-lived system without noticing the consequence.

**Why this is bad.** With `decay_rate = 0`, `threat_level` grows monotonically. Any system with non-zero uncertainty **will** enter panic — only the time is in question. That is fine for tests. It is often wrong for production.

**Rule.** Choose `decay_rate` deliberately for the context:

- 0 — for paranoid systems (messaging, cryptography);
- 0.01–0.05 — for steady systems (monitoring, IoT);
- tuned by experiment — there is no universal value.

---

## AP-07. Confusing Panic-First with Consent-First

**The mistake.** Treating Panic-First as "destroy data at any alarm".

**Why this is bad.** Panic-First is a principle of **priorities**: survival over integrity. Consent-First is a principle of the **API**: destructive actions require an explicit policy. They do not contradict each other:

- Panic-First says: *if the choice is between losing data and losing the system, lose the data*.
- Consent-First says: *that choice must be configured explicitly by the developer, not made by default*.

**Rule.** Always configure `fallback`, `scope`, and the data-destruction policy **before** the system can enter panic.

---

## AP-08. Computing uncertainty by hand instead of propagating it

**The mistake.** Computing the result's uncertainty by hand instead of using NoisyFloat operations:

```python
result_value = a.value + b.value
result_uncertainty = a.uncertainty + b.uncertainty  # wrong formula!
```

**Why this is bad.** The formula `σ_a + σ_b` is an upper bound, not the exact value. The correct formula is `√(σ_a² + σ_b²)`. A manual calculation bypasses propagation and introduces errors.

**Rule.** Treat NoisyFloat as a type. Use the operators `+`, `-`, `*`, `/`. If you need a non-standard operation, compute the propagation through partial derivatives.

---

## A meta-rule

> If you use TRANSFLUX but call `.value` at every step
> in order to get "an ordinary float", you are using TRANSFLUX wrong.

The value of the paradigm is that uncertainty, history, and threat **travel** through the whole computation. Every `.value` is a point where that information is thrown away.
