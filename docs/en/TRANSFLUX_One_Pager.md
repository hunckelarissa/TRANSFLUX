> **Language:** English · [Русский](../ru/TRANSFLUX_One_Pager.md)

# TRANSFLUX

**A computational paradigm of continuous becoming**

---

## The problem

Classical computation is built on three illusions: state is stable, values are exact, and threats do not exist. In the real world sensors are noisy, data drifts, and systems come under pressure. Tools that ignore this are lying.

## The answer

```
TRANSFLUX = Flow(State) · Uncertainty(Value) · Adaptation(Survival)
```

| Axis | Question | Primitive | What it gives |
|---|---|---|---|
| **State** | What do I have? | `FluxVar<T>` | A value with velocity, history, and comfort. A sharp jump is a signal, not silence. |
| **Value** | How exact is this? | `NoisyFloat` | A value with uncertainty and confidence. Noise is not discarded — it is carried forward. |
| **Survival** | What to do under threat? | `SurvivalState` | Survival over data integrity. Panic is a controlled rebirth. |

The three axes are orthogonal (none reduces to another), and they are coupled: instability on one automatically raises vigilance on another.

## Where it applies

- Edge AI and neuromorphic systems — continuous values with uncertainty
- Medicine and autonomous systems — where a mistake is life or death
- Safety in exposed contexts — instant rotation of identity
- Scientific computing — uncertainty quantification built in

## What this is not

Not a language. Not a framework. It is an **epistemology**, realizable in Python, Rust, Haskell, any stack.

## Status

Draft specification. A Python library of the primitives and the orchestrator, plus synthetic scenarios. Open source (Apache 2.0).

## Links

- [Specification](TRANSFLUX_Specification.md) — the formal core
- [Use cases](TRANSFLUX_Use_Cases.md) — four worked examples
- [Manifesto](TRANSFLUX_Manifesto.md) — position and voice
- [Related paradigms](TRANSFLUX_Related_Paradigms.md) — an honest comparison with fuzzy logic, reactive streams, and others

---

> *TRANSFLUX is a paradigm of computation that does not pretend*  
> *the world is stable, values are exact, and threats do not exist.*
