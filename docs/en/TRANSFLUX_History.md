> **Language:** English · [Русский](../ru/TRANSFLUX_History.md)

# TRANSFLUX: Project history

> A curated chronology: how and why TRANSFLUX came to be.
> Raw material (notes, discussions, experiments) is in `research/`.
> The detailed version-by-version history is in the [changelog](CHANGELOG.md).

## v0.0 — March 2026: the idea

The project began with notes and discussions (`research/notes/`): the observation that the classical paradigm answers "what is stored" and "what is true" as points — while real systems live in a flow, in uncertainty, and under threat.

Early experiments included a `Flow` prototype (`research/notes/TRANSFLUX.py`) — an alternative physical model of a variable, with spring dynamics and a target. The target model was later dropped: a primitive should not "strive" toward a value. That is the caller's responsibility (see DR-008).

<!-- TODO(Лариса): fill in from research/ — the key discussions, turns, and ideas that were discarded. -->

## v0.1 — March 2026: the first draft

- The formula `TRANSFLUX = Flow(State) · Uncertainty(Value) · Adaptation(Survival)` was stated.
- Decomposition: from seven initial concepts, **three orthogonal axes** were selected (FluxVar, NoisyFloat, SurvivalState). The rest were recognized as derived.
- Python prototypes of each primitive.
- The first manifesto.

## v0.2 — April 2026: a formal revision

The move from a set of ideas to a specified system:

- The mathematics was fixed (`NoisyFloat.__mul__` at zero values). `__sub__`, `__truediv__`, a `dt ≤ 0` guard, and `decay_rate` were added.
- Side effects were moved out of the data models into callbacks (`on_trauma`, `on_panic`).
- The Coupling Protocol (§4.2) and the Event Model (§4.3) were formalized.
- Marketing claims without evidence were removed.
- The documentation grew into a connected system: manifesto, specification, design rationale, invariants, anti-patterns, glossary.

## v0.3 — August 2026: a reference implementation

- A reference implementation appeared (`src/transflux/`) with invariant tests.
- Package infrastructure: `pyproject.toml`, pytest, CONTRIBUTING (a local check).
- Documentation gained an API reference, an architecture overview, and this history. The roadmap was taken out of the specification.
- Formal specification of that stage became the living document now kept as [TRANSFLUX_Specification.md](TRANSFLUX_Specification.md).

## v0.5 — October 2026: the library as the concept check

The reference code became the carrier of the paradigm (package **0.5.0**; formal core: [specification](TRANSFLUX_Specification.md)). Formalism questions were closed: `min()` for arithmetic, no `constraints`, `FlowingTrit` is a float. On top of the three axes came `weighted_mean`, `classify_jump`, the orchestrator's backup mode, and `PolyphonicIdentity`. The synthetic scenarios and their charts are in `tests/synthetic/` and `docs/figures/synthetic/`. Living documentation is bilingual under `docs/en/` and `docs/ru/`. A DSL, Rust, and validation on other hardware remain deferred.

## Lessons from the history

- **The 7 → 3 decomposition** was the main turn: the criterion "does this concept follow from the basis?" cut away the surplus.
- **From `Flow` to `FluxVar`** — dropping the target model in favor of a neutral primitive.
- **From `print()` to callbacks** — a data model should not have side effects by default (the forerunner of Consent-First).
