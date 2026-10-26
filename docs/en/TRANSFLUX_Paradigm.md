> **Language:** English · [Русский](../ru/TRANSFLUX_Paradigm.md)

# TRANSFLUX: The paradigm

> For developers, architects, and anyone who wants to understand —
> not what this does, but **why it thinks this way**

---

## Where it starts

Imagine a temperature-monitoring system in a hospital.

The classical approach: read the temperature, compare it with a threshold, and if it is higher, raise a signal. Simple. Clean. It works.

But what if the sensor returns `36.6` with an accuracy of plus or minus three degrees? What if the temperature jumped from 36 to 40 in a second — is that a real fever, or a sensor fault? What if the alarm has to be raised in a way that does not reveal the patient's identity in a system that outsiders can reach?

The classical paradigm is silent. It does not know what to do with **uncertainty**, **a history of change**, and **survival under threat**.

TRANSFLUX starts from a question: *what if uncertainty, change, and threat are not exceptions, but the norm?*

---

## Three questions of any system

Any computational system — from a microcontroller to a distributed AI — inevitably meets three fundamental questions:

**What do I have?**
How do you store a state that does not stand still? How do you account for a value that came from the past, is moving into the future, and has inertia?

**How exact is this?**
How do you work with knowledge that contains doubt? How do you stop pretending that `5.0` is exactly five, when it is really "somewhere around five, give or take one and a half"?

**What to do under threat?**
How do you behave when the system is under pressure? What matters more — keeping the data, or keeping yourself?

Three questions. Three axes. Three principles.

```
TRANSFLUX = Flow(State) · Uncertainty(Value) · Adaptation(Survival)
```

---

## Axis I — State Model: a variable as a channel

### How the classical world thinks

A variable is a **box**. You put a value in, you take a value out. The box does not remember what was in it before. The box does not know where it is "moving". The box simply stores.

```
x = 5    →    x = 10    →    x = 3
```

Three independent moments. No link between them.

### How TRANSFLUX thinks

A variable is the **channel of a river**. Water flows in it. It has a speed, a direction, a history of its banks. A sharp turn is not merely a new value. It is an event with consequences.

```
x ~> 5    →    x ~> 10    →    x ~> 3
```

Three points of one trajectory. The system knows where it came from and where it is going.

Every variable in TRANSFLUX has:

- **velocity** — how fast it is changing right now
- **acceleration** — how the rate of change is itself changing
- **history** — a memory of past states
- **comfort** — how "comfortable" the current state is for the system (from dysphoria to euphoria)
- **trauma threshold** — the threshold past which a sharp jump becomes an event

The last one is the key. If a value jumped too sharply, the system does not crash with an error. It signals: *this was the trauma of a transition* — and keeps working. The reaction to trauma is configurable: from a warning, to softening the jump, to an escalation into the survival model.

### An analogy

A hormone level on hormone replacement therapy does not change in an instant. It flows: slowly, with inertia, with a history of every dose. A sharp jump is a signal, not the norm. The body remembers the trajectory.

That is how a variable should work in a computational system that is honest about the nature of change.

---

## Axis II — Value Model: a value as a distribution

### How the classical world thinks

A value is a **point**. `3.14`. `true`. `"hello"`. A point either exists or it does not. It cannot be "a little bit true" or "about 3.14".

Uncertainty is an exception to be handled and removed. Noise is an error to be filtered out.

### How TRANSFLUX thinks

A value is a **distribution**. Not a point, but a cloud with a center, a width, and a degree of trust.

```
5.0                                          — the classical way: a pretense
NoisyFloat(5.0, uncertainty=0.3, conf=82%)   — TRANSFLUX: honest knowledge
```

When two values are added, their uncertainties are added too. This is **propagation of uncertainty**: doubt is carried forward through the whole chain of computation. A result always carries information about the quality of the data it was made from.

Out of this, **Gradient of Truth** grows naturally. Instead of a Boolean `True / False`, a condition has a degree: how strongly does it hold, given the uncertainty? A condition does not switch on sharply — it grows smoothly. The grey zone is not a bug. It is a normal place to work.

### An analogy

A doctor who says "you definitely do not have cancer" after one test is the classical way. A doctor who says "the probability of a malignant process is about 12%, come back in a month, because one reading was unstable" is TRANSFLUX.

The second doctor is more honest. And their decision system is more reliable, because it does not throw away the information about doubt.

---

## Axis III — Survival Model: safety through vulnerability

### How the classical world thinks

Safety is **protecting integrity**. Data must be preserved. The system must keep working. An error must be logged and handled. The main priority: do not lose the data.

### How TRANSFLUX thinks

The main priority: **survive**.

These are different things. Sometimes, in order to survive, you have to destroy data. Sometimes you have to change identity immediately. Sometimes you have to become a different system, leaving no trace of the previous state.

Panic-First architecture is built on three components:

**Threat level** — a continuous quantity from 0 to 1. Threat is not binary. It grows gradually. The system always knows how much pressure it is under.

**Panic threshold** — the threshold of a phase transition. Before it, adaptation is smooth. After it, there is a deterministic jump: identifiers change, links reset, a reserve state activates.

**Scope** — the reach of panic: local (one thread), process (the whole process), system (the whole infrastructure). Panic is not chaos. It is a controlled rebirth with stated boundaries.

Panic is a **concrete state transition**: a measurable trigger, a deterministic effect, and a way to test it. It can be reproduced, covered by tests, and integrated into CI.

### The link with the other axes

Threat comes from two sources:

- **From the Value Model:** a low `confidence` on a `NoisyFloat` is a signal of instability that raises `threat_level`. The system feels when its knowledge is unreliable.
- **From the State Model:** a sharp `velocity` on a `FluxVar` is a signal of "transition trauma", which also raises `threat_level`. The system feels when its state is changing too fast.

This makes TRANSFLUX a **self-observing system**: it generates threat from its own instability, without waiting for an outside signal.

### An analogy

A person who is being threatened does not wait until the threat becomes "official". They change their route, change their name in a messenger, delete the correspondence, and sign out of accounts. This is not panic in the sense of losing control. It is a **rational protocol of survival**, sharpened by experience.

A concrete scenario: a messenger that, on receiving a distress code, on one button press, or on a lost ping, immediately rotates identifiers, clears local data, and moves into a safe mode. This is not a metaphor. It is a testable requirement.

---

## Why three, and why orthogonal

The three axes cover three levels of any system:

| Level | Axis | Question |
|---|---|---|
| Primitive (how it is stored) | State Model | What do I have? |
| Value (how it is computed) | Value Model | How exact is this? |
| Architecture (how it survives) | Survival Model | What to do under threat? |

They are **orthogonal**: none is a part of another. You can use `NoisyFloat` without `FluxVar`. You can add `SurvivalState` to any existing project. You can adopt them one at a time.

Together they form a **closed system**: instability in Value raises threat in Survival. A sharp change in State also raises threat in Survival. When panic fires, it moves State to a safe value.

Every other TRANSFLUX concept is **derived** from these three:

| Derivative | From which axis | How it follows |
|---|---|---|
| Gradient of Truth | Value | degree of truth = f(confidence, uncertainty) |
| FlowingTrit | State | a continuous float; poles `-1`, `0`, `+1`; `-0.5` is an ordinary value |
| Continuous Becoming | State | computation = a flow, not a function call |
| Polyphonic Identity | Survival | `PolyphonicIdentity`: several masks; `in_group` does not name the role |
| Deadname Erasure | Survival | `erase` / `rotate_all` remove the old hash from the whole book |

This is the maturity criterion of the paradigm: if a new idea does not follow from the three axes, it is either surplus, or it is a reason to revisit the basis.

---

## Domains

TRANSFLUX is not a language and not a library. It is a way of thinking that can be embodied in any stack.

**Edge AI and neuromorphic systems.** The principle "a variable = a channel + velocity + noise" sits naturally on neuromorphic chips (Intel Hala Point, BrainChip Akida). Instead of discrete `if/else` — a smooth gradient and a continuous flow. The result: efficient work on batteries, in real time. Potential gains in performance need validation on specific hardware.

**Uncertainty quantification.** `NoisyFloat` with propagation of uncertainty is a ready layer on top of existing UQ methods (Bayesian NN, MC-Dropout, Laplace approximation). It is wanted in medicine, meteorology, molecular design, and autonomous transport.

**Safety in exposed contexts.** Panic-First architecture answers a real problem for the queer community, journalists, dissidents, and everyone who works in repressive jurisdictions. Edge AI in autonomous systems (transport, drones), where data cannot simply be "handed over", but can be destroyed on compromise.

**Self-adapting systems.** The principle "computation = a process, not a result" matches the trend of agentic AI and self-healing systems. TRANSFLUX gives a conceptual frame for architectures that refactor themselves without downtime.

**Neural networks and TRANSFLUX strengthen each other:**

- *Neural networks use TRANSFLUX* — wrapping weights and activations in a flow model gives inertia of transitions, noise as information, and a gradient of truth instead of hard thresholds.
- *TRANSFLUX uses neural networks* — learned predictors of an optimal dynamics, and comfort as a meta-layer over the library. This coupling is deferred together with the PyTorch / TensorFlow wrappers.

---

## What TRANSFLUX is not

**Not a programming language.** TRANSFLUX can be implemented in Python, Rust, Haskell, LUMEN. It is a paradigm, not a syntax.

**Not merely a philosophy.** Every principle is formalized: there are data structures, there are operations, there is testable behavior.

**Not fuzzy logic.** Gradient of Truth uses ideas from fuzzy logic, but it builds uncertainty into the data type as a first-class primitive, not into a conditional operator. These are different levels of abstraction.

**Not reactive programming.** `FluxVar` is conceptually close to a Signal from RxJS, but it has comfort, history, and trauma_threshold as first-class fields — not as patterns laid on top of a stream.

**Not probabilistic programming.** `NoisyFloat` is simpler than Pyro or Stan: it is a type primitive with propagation, not an inference system. In return it can be embedded in any stack without a specialized runtime.

A detailed comparison with existing paradigms is in a separate document (`TRANSFLUX_Related_Paradigms.md`).

---

## One line

> *TRANSFLUX is a paradigm of computation that does not pretend*
> *the world is stable, values are exact, and threats do not exist.*
