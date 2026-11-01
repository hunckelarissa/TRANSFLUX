> **Language:** English · [Русский](ROADMAP.ru.md)

# TRANSFLUX Roadmap

> Status as of October 2026. The formal decisions are [docs/en/TRANSFLUX_Open_Questions.md](docs/en/TRANSFLUX_Open_Questions.md) and DR-016…DR-030. The specification is [docs/en/TRANSFLUX_Specification.md](docs/en/TRANSFLUX_Specification.md).

## Already in the Python library

The carrier of the paradigm is the package `src/transflux/`.

| Component | What it does |
|---|---|
| `FluxVar`, `flow()` | state as a channel; `flow` is the Python form of the `~>`; comfort reacts to trauma/calm |
| `NoisyFloat` | arithmetic that carries σ; confidence through `min` |
| `weighted_mean` | mean of independent readings, weight `1/σ²` |
| `FlowingTrit` | a continuous trit; `-0.5` is stored as itself |
| `classify_jump` | `calm` / `alone` / `shared`; does not change confidence |
| `SurvivalState` | threat, panic, rotation of its own `identity_hash`, scope hooks |
| `PolyphonicIdentity` | several masks; `erase` and `rotate_all` inside one book |
| `IdentityLedger` | registered books; cross-book `erase` with one shared new hash |
| `TransfluxSystem` | one cycle of the three axes, `peak_threat`, backup mode `degraded`, optional stale/margin threat |
| `NoisyFlow` | alias `FluxVar[NoisyFloat]` |
| `stale_threat` / `uncertainty_margin_threat` | helpers for silence and an σ safety margin |
| `weighted_mean(..., correlation= / covariance=)` | scalar ρ or full GLS matrix |
| `PolyphonicIdentity.live` / `erase_live` | weak live registry; opt-in process-wide erase |
| `ScarMemory` | named scars; `amplify` / `fade`; panic does not mark them alone |
| Synthetic scenarios | `tests/synthetic/`, charts in `docs/figures/synthetic/` |

## Nearest work, if the library is deepened

These are gaps between the scenarios and the code. Some behavior is deliberately left to the caller (DR-017, DR-021, DR-022, DR-023).

- Other research-backlog ideas (Grief-Driven GC, Algebra of Change, …) are still hypotheses, not library types.
- A DSL / other runtimes stay deferred (see below).

## Deferred

While the concept check is synthetic scenarios, not other hardware:

- the `~>` operator as language syntax, a DSL, and a LUMEN variant;
- a Rust implementation;
- benchmarks, neuromorphic chips, PyTorch / TensorFlow wrappers.

If the library is accepted as a sufficient check, the likely next horizon is embedding and microcontrollers. The stack for that moment is chosen then, not from today's list.

## Research backlog (far, not Core)

The ideas are written down. `ScarMemory` has a light check in the library (DR-028). The rest are not in the current work:

| Idea | Axis | Hypothesis |
|---|---|---|
| Grief-Driven GC | State | GC as a protocol of loss, with a history of references |
| Dysphoric Compiler | Value | diagnosing "discomfort" in code instead of dry errors |
| Chosen Family Topology | State | a dependency graph as relationships with history and trust |
| Body-Budget Scheduler | State | a scheduler with a model of "energy" and "fatigue" |
| Liminal Type Inference | Value | intermediate types as valid states |
| ~~Scar Memory~~ | Survival | **in library as `ScarMemory`** — stronger checks where failures already happened |
| Euphoria-Driven Optimization | Value | maximizing comfort instead of minimizing loss |
| Algebra of Change | State | operations on changes, composition of transformations |
| Time-Native Programming | State | time and causality as first-class |
