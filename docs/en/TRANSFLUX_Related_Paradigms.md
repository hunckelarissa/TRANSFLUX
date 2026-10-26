> **Language:** English · [Русский](../ru/TRANSFLUX_Related_Paradigms.md)

# TRANSFLUX and related paradigms

> Honest positioning: what TRANSFLUX borrows,
> what it rethinks, and what it proposes for the first time.

---

## Overview

TRANSFLUX does not exist in a vacuum. Many of its individual ideas have predecessors in industry and in academia. What is unique about TRANSFLUX is not each concept on its own, but their particular combination, the model of interaction between the axes, and the epistemological frame that produces engineering decisions from an experience mainstream engineering usually does not have.

Below is an honest map of the overlaps and the differences.

---

## Summary table

| TRANSFLUX concept | Nearest analogue | The kinship | The difference |
|---|---|---|---|
| NoisyFloat, propagation | UQ, Bayesian ML, MC-Dropout | Working with uncertainty | Uncertainty is built into a type primitive, not into a separate library or an inference system |
| Gradient of Truth | Fuzzy logic (Zadeh, 1965) | A degree of truth ∈ [0, 1] | The degree is derived from the value's own uncertainty, not assigned by hand on a set |
| FluxVar / channel | Reactive Streams (RxJS, Signals, Svelte stores) | Reactivity, observable values | FluxVar stores velocity, history, comfort, and trauma_threshold as first-class fields |
| Continuous Becoming | Dataflow architectures, streaming | Computation as a continuous process | An entity "lives while there is a flow" — closer to a neuromorphic intuition than to a pull/push stream model |
| Panic-First, SurvivalState | Zero-trust, self-destruct | An assumption of compromise | Threat as a continuous metric, coupled to the instability of the system itself (not only to an outside attacker) |
| Polyphonic Identity | ZKP, DID, SSI | Proof without disclosure | Identity as a dynamic, layered process, driven by a survival model |

---

## Detailed comparisons

### 1. Fuzzy logic (Lotfi Zadeh, 1965)

**What it is.** A logic that allows degrees of membership in a set: `x ∈ A` with strength `μ(x) ∈ [0, 1]`. Used in control, decision-making, and linguistic variables.

**Kinship with TRANSFLUX.** Gradient of Truth also works with a continuous degree of truth instead of a binary `True/False`.

**The key difference.** In fuzzy logic the degree of membership is a property of a value's **relation** to a set. It is given by a membership function that the designer defines. In TRANSFLUX the degree of truth is a **derivative** of the value's own uncertainty and confidence. It is computed, not assigned. The value "knows" how reliable it is, and a condition "gains strength" automatically as confidence grows.

**Where TRANSFLUX adds something.** A sensor returns a temperature of 37.5°C. In fuzzy logic the designer defines the membership function "fever" in advance (for example, linear from 37.0 to 38.5). In TRANSFLUX the value `NoisyFloat(37.5, uncertainty=1.2, confidence=0.6)` itself carries the information about unreliability, and the decision is automatically weakened by the low confidence — without anyone having to tune a function by hand.

---

### 2. Reactive streams (RxJS, Signals, Svelte stores)

**What it is.** A pattern of observable values: when a source changes, dependent computations update automatically. Observable, Signal, and Store are variants of the implementation.

**Kinship with TRANSFLUX.** `FluxVar` is also an observable value with a history of change.

**The key difference.** Reactive streams store the current value and the dependencies. They do not know:

- **how fast** the value is changing (velocity);
- **how it changed** before (history as a ring buffer);
- **how comfortable** the current state is (comfort);
- **when** a change becomes traumatic (trauma_threshold).

FluxVar models not merely the fact of change, but the **physics of change**: inertia, acceleration, trajectory.

**Where TRANSFLUX adds something.** Accelerometer readings on an IoT device. An RxJS Signal updates instantly on every tick. FluxVar knows that a jump from 0 g to 50 g in 1 ms is an anomaly (velocity crosses `trauma_threshold`), and it can soften the transition or escalate into SurvivalState.

---

### 3. Probabilistic programming (Pyro, Stan, Gen, Edward)

**What it is.** Languages and frameworks for defining probabilistic models and running Bayesian inference: you state a prior and a likelihood, and you get a posterior.

**Kinship with TRANSFLUX.** `NoisyFloat` also works with uncertainty and propagates it through computation.

**The key difference.** Probabilistic programming is an **inference system**: it solves the inverse problem (from observations to parameters). `NoisyFloat` is a **type primitive**: it solves the forward problem (from inputs to outputs, with propagation of uncertainty). NoisyFloat is much simpler than a full inference system, and in return it can be embedded in any stack without a specialized runtime.

**When to use which.** If you need to compute a posterior distribution from data, use Pyro or Stan. If you need every value in the system to carry information about its own reliability, use NoisyFloat. They are not competitors. They work at different levels of abstraction.

---

### 4. Neuromorphic computing (SNN, Intel Hala Point, BrainChip Akida)

**What it is.** A computational paradigm inspired by neural architectures: spiking neural networks (SNN), event-driven computation, memory and processor in the same place.

**Kinship with TRANSFLUX.** The continuous dynamics of FluxVar, "an entity lives while there is a flow", panic as an analogue of a neural spike — all of this is conceptually close to neuromorphic principles.

**The key difference.** Neuromorphic computing is a **hardware paradigm**. TRANSFLUX is a **software model** that can map onto that hardware in a natural way. TRANSFLUX offers an abstraction that hides the difference between a classical CPU and a neuromorphic processor behind one API of primitives.

**An open question.** A concrete mapping of TRANSFLUX primitives onto the instructions of neuromorphic hardware needs an engineering proof of concept. Without it, the link stays conceptual. That proof is deferred: see the roadmap.

---

### 5. Zero-knowledge proofs / decentralized identity (ZKP, DID, SSI)

**What it is.** Cryptographic methods for proving a claim without revealing the data underneath. DID (Decentralized Identifiers) and SSI (Self-Sovereign Identity) are W3C standards for managing identity oneself.

**Kinship with TRANSFLUX.** Polyphonic identity — one key, many masks — is conceptually close to ZKP and DID.

**The key difference.** ZKP is a cryptographic technique. DID is a standard for identifiers. In TRANSFLUX identity is a **dynamic process**, driven by a survival model: it can change instantly on panic, it can have several layers at once, and it can be erased completely (Deadname Erasure). ZKP and DID can be an **implementation** layer under Polyphonic Identity, but they do not define its semantics.

---

### 6. Zero-trust and self-destruct systems

**What it is.** Zero-trust: an architecture in which no component is trusted by default. Self-destruct: mechanisms that destroy data on compromise (Signal, Wickr, hardware HSMs).

**Kinship with TRANSFLUX.** Panic-First includes self-destruct as a special case. Polyphonic identity overlaps with zero-trust.

**The key difference.** Zero-trust and self-destruct are **external** mechanisms: they react to a compromise that has been detected. In TRANSFLUX threat is an **internal continuous metric**, coupled to the instability of the system itself: high uncertainty produces threat, a sharp velocity produces threat. The system does not wait for an outside signal that says "you have been breached". It feels its own instability and can be reborn in advance.

---

## What holds TRANSFLUX together

None of the paradigms above offers **all of these at once**:

1. Uncertainty as a first-class type primitive (not a library, not an inference system).
2. State with a physics of change (velocity, comfort, trauma) as the basic model of storage.
3. Survival as a priority above data integrity, with threat produced from the system's own instability.

TRANSFLUX is a **synthesis**, and its value is that the three axes interact as a closed system, rather than merely sitting next to each other.

---

## Bibliography (key works)

- Zadeh, L.A. (1965). *Fuzzy Sets*. Information and Control, 8(3), 338–353.
- ReactiveX / RxJS. [reactivex.io](http://reactivex.io)
- Pyro: Deep Universal Probabilistic Programming. [pyro.ai](https://pyro.ai)
- Stan Development Team. [mc-stan.org](https://mc-stan.org)
- W3C DID Core. [w3.org/TR/did-core](https://www.w3.org/TR/did-core/)
- Intel Hala Point — Neuromorphic Research. [intel.com/loihi](https://www.intel.com/content/www/us/en/research/neuromorphic-computing.html)
- BrainChip Akida. [brainchip.com](https://brainchip.com)
