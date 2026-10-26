> **Language:** English · [Русский](ROADMAP.ru.md)

# TRANSFLUX Roadmap

> Status as of October 2026. The formal decisions are [docs/en/TRANSFLUX_Open_Questions.md](docs/en/TRANSFLUX_Open_Questions.md) and DR-016…DR-023. The specification is [docs/en/TRANSFLUX_Specification.md](docs/en/TRANSFLUX_Specification.md).

## Already in the Python library

The carrier of the paradigm is the package `src/transflux/`.

| Component | What it does |
|---|---|
| `FluxVar`, `flow()` | state as a channel; `flow` is the Python form of the `~>` operator |
| `NoisyFloat` | arithmetic that carries σ; confidence through `min` |
| `weighted_mean` | mean of independent readings, weight `1/σ²` |
| `FlowingTrit` | a continuous trit; `-0.5` is stored as itself |
| `classify_jump` | `calm` / `alone` / `shared`; does not change confidence |
| `SurvivalState` | threat, panic, rotation of its own `identity_hash` |
| `PolyphonicIdentity` | several masks; `erase` and `rotate_all` inside one book |
| `TransfluxSystem` | one cycle of the three axes, `peak_threat`, backup mode `degraded` |
| Synthetic scenarios | `tests/synthetic/`, charts in `docs/figures/synthetic/` |

## Nearest work, if the library is deepened

These are gaps between the scenarios and the code. Some behavior is deliberately left to the caller (DR-017, DR-021, DR-022, DR-023).

- `scope` (`local` / `process` / `system`) is only stored: panic does the same thing at every scale.
- `erase` sees references inside one `PolyphonicIdentity`. A hash outside the book is not erased.
- `comfort` does not itself react to trauma or to a calm run.
- `NoisyFlow` is the convention `FluxVar[NoisyFloat]`; there is no separate type.
- `weighted_mean` assumes the readings are independent.
- An uncertainty safety margin and a "no signal for a while" timer are not separate functions: they are inputs to `tick` and `threat_delta`.

## Deferred

While the concept check is synthetic scenarios, not other hardware:

- the `~>` operator as language syntax, a DSL, and a LUMEN variant;
- a Rust implementation;
- benchmarks, neuromorphic chips, PyTorch / TensorFlow wrappers.

If the library is accepted as a sufficient check, the likely next horizon is embedding and microcontrollers. The stack for that moment is chosen then, not from today's list.

## Research backlog (far, not Core)

The ideas are written down. They are not in the current work:

| Idea | Axis | Hypothesis |
|---|---|---|
| Grief-Driven GC | State | GC as a protocol of loss, with a history of references |
| Dysphoric Compiler | Value | diagnosing "discomfort" in code instead of dry errors |
| Chosen Family Topology | State | a dependency graph as relationships with history and trust |
| Body-Budget Scheduler | State | a scheduler with a model of "energy" and "fatigue" |
| Liminal Type Inference | Value | intermediate types as valid states |
| Scar Memory | Survival | stronger checks in places where failures already happened |
| Euphoria-Driven Optimization | Value | maximizing comfort instead of minimizing loss |
| Algebra of Change | State | operations on changes, composition of transformations |
| Time-Native Programming | State | time and causality as first-class |
