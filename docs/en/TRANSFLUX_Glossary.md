> **Language:** English · [Русский](../ru/TRANSFLUX_Glossary.md)

# TRANSFLUX: Glossary and reference card

> Fast navigation across terms, invariants, and decisions.

---

## The formula

```
TRANSFLUX = Flow(State) · Uncertainty(Value) · Adaptation(Survival)
```

---

## Primitives

| Primitive | Axis | Key fields | Description |
|---|---|---|---|
| `FluxVar<T>` | State | value, velocity, acceleration, comfort, history, trauma_threshold | A variable as a channel |
| `NoisyFloat` | Value | value, uncertainty, confidence | A value as a distribution |
| `SurvivalState` | Survival | threat_level, panic_threshold, identity_hash, scope, decay_rate, fallback | A model of survival |
| `TransfluxSystem` | Orchestrator | state, value, survival, sensitivities | The coupling cycle of the three axes |

---

## Derived concepts

| Concept | Source | Description |
|---|---|---|
| Gradient of Truth | NoisyFloat | A degree of truth: f(confidence, SNR) |
| NoisyFlow | FluxVar × NoisyFloat | `FluxVar[NoisyFloat]` |
| FlowingTrit | FluxVar | A continuous trit: a float, poles `-1`, `0`, `+1`; `-0.5` is allowed |
| Continuous Becoming | FluxVar | Computation = a flow, not a call |
| Polyphonic Identity | SurvivalState | `PolyphonicIdentity`: masks; `in_group` does not name the role |
| Deadname Erasure | SurvivalState | `erase` / `rotate_all`: the old hash does not remain in the book |
| Consent-First | SurvivalState | Destructive operations require explicit consent |

---

## Key terms

| Term | Meaning |
|---|---|
| **Panic-First** | An architectural principle: survival has priority over data integrity |
| **Consent-First** | An API principle: destructive operations do not run without an explicit policy |
| **trauma** | An event: velocity crossed `trauma_threshold` (advisory, not blocking) |
| **classify_jump** | `calm` / `alone` / `shared`: this sensor's jump against its neighbors |
| **panic** | A phase transition: threat ≥ threshold → identity rotation, threat reset |
| **decay_rate** | How fast `threat_level` fades under stable conditions |
| **momentum** | An image of inertia from the manifesto; in code it is velocity + acceleration |
| **dispersion** | An obsolete synonym of uncertainty |
| **coupling** | A link between axes: orthogonal by definition, coupled in behavior |

---

## Callbacks

| Callback | Primitive | Signature | When |
|---|---|---|---|
| `on_trauma` | FluxVar | `(flux, velocity) → None` | velocity > trauma_threshold |
| `on_panic` | SurvivalState | `(survival, old_hash) → None` | threat ≥ panic_threshold |

---

## Invariants (INV)

| ID | Primitive | Statement |
|---|---|---|
| INV-N1 | NoisyFloat | uncertainty ≥ 0 |
| INV-N2 | NoisyFloat | 0 ≤ confidence ≤ 1 |
| INV-N3 | NoisyFloat | 0 ≤ gradient_of_truth() ≤ confidence |
| INV-F1 | FluxVar | -1 ≤ comfort ≤ 1 |
| INV-F2 | FluxVar | len(history) ≤ maxlen |
| INV-F3 | FluxVar | trajectory() == list(history) + [value] |
| INV-F4 | FluxVar | After update(v): value == v (trauma is advisory) |
| INV-F5 | FluxVar | velocity == (new - old) / dt |
| INV-S1 | SurvivalState | 0 ≤ threat_level ≤ 1 |
| INV-S2 | SurvivalState | After panic: threat_level == 0 |
| INV-S3 | SurvivalState | After panic: identity_hash is unique |
| INV-S4 | SurvivalState | panic_count grows monotonically |
| INV-S5 | SurvivalState | threat ≥ threshold → panic (determinism) |

## Operation properties (OP)

| ID | Operation | Property |
|---|---|---|
| OP-1 | a ± b | uncertainty ≥ max(σ_a, σ_b) |
| OP-2 | a ± b | confidence ≤ min(c_a, c_b) |
| OP-3 | a ± b | value = a.value ± b.value (exact) |
| OP-4 | a × b | σ_z = √(b²σ_a² + a²σ_b²) |
| OP-5 | a × b | Correct at zero values |
| OP-6 | a × b | σ_rel ≤ σ_rel_a + σ_rel_b |
| OP-7 | a / b | σ_z = √((σ_a/b)² + (aσ_b/b²)²) |
| OP-8 | a / b | b ≈ 0 → ZeroDivisionError |

## Coupling properties (CP)

| ID | Coupling | Property |
|---|---|---|
| CP-1 | Value → Survival | Lower confidence → higher threat (monotonic) |
| CP-2 | State → Survival | Higher velocity → higher threat (monotonic) |
| CP-3 | Survival → State | Panic → threat=0, identity changed |
| CP-4 | Value → Survival | A more reliable value → less threat |
| CP-5 | State → Survival | A more stable state → less threat |

---

## Design rationale (DR)

| ID | Decision | The point |
|---|---|---|
| DR-001 | Three axes | A minimally complete orthogonal basis |
| DR-002 | min() for confidence | A conservative strategy (weakest link) |
| DR-003 | decay_rate = 0 | A paranoid default is safer than an optimistic one |
| DR-004 | comfort is a scalar | Simplicity is enough for Core |
| DR-005 | trauma_threshold is a number | Simplicity, testability, determinism |
| DR-006 | history maxlen=32 | A memory / context trade-off |
| DR-007 | Panic is deterministic | A safety guarantee is not a gamble |
| DR-008 | update(value), not target | Generality over a specific physics |
| DR-009 | σ, not σ² | Readability over a micro-optimization |
| DR-010 | Orthogonal, but coupled | Coupling produces emergent behavior |
| DR-011 | Consent-First | Destruction requires an explicit policy |
| DR-012 | One formula (·) | A mnemonic plus a completeness criterion |
| DR-013 | Advisory callbacks | Trauma/panic are a signal, not a block |
| DR-014 | Orchestrator pattern | Primitives do not know about each other |
| DR-015 | One package, submodules | A low barrier to entry |
| DR-016 | min() stays | Other confidence strategies are deferred |
| DR-017 | No constraints | Whether value is allowed is the programmer's concern |
| DR-018 | FlowingTrit = float | Poles are landmarks, not a closed set |
| DR-019 | Python first | DSL, Rust, and validation are deferred |
| DR-020 | weighted_mean | Weight 1/σ²; confidence follows the weight, not min |
| DR-021 | Backup mode | Panic latches only if a backup pair was set in advance |
| DR-022 | classify_jump | alone / shared / calm; does not change confidence |
| DR-023 | Masks apart from panic | Names are erased only by an explicit call |

---

## Project documents

| Document | For whom |
|---|---|
| [One-pager](TRANSFLUX_One_Pager.md) | A first look (2 min) |
| [Plain-language explanation](TRANSFLUX_Simple_Explanation.md) | What this is, without the jargon |
| [Manifesto](TRANSFLUX_Manifesto.md) | Position and voice |
| [Paradigm](TRANSFLUX_Paradigm.md) | Developers, architects |
| [Specification](TRANSFLUX_Specification.md) | The formal core |
| [Use cases](TRANSFLUX_Use_Cases.md) | Concrete examples |
| [Related paradigms](TRANSFLUX_Related_Paradigms.md) | Honest positioning |
| [Design rationale](TRANSFLUX_Design_Rationale.md) | Why the decisions were made |
| [Formal invariants](TRANSFLUX_Formal_Invariants.md) | Guarantees and tests |
| [Anti-patterns](TRANSFLUX_Anti_Patterns.md) | How not to |
| [API reference](TRANSFLUX_API_Reference.md) | Primitives and callbacks |
| [Architecture](TRANSFLUX_Architecture.md) | A high-level overview |
| [History](TRANSFLUX_History.md) | How TRANSFLUX came to be |
| [Changelog](CHANGELOG.md) | Change history |
| [Roadmap](../../ROADMAP.md) | The roadmap |
| [Decisions](TRANSFLUX_Open_Questions.md) | Decisions, and what is deferred |
