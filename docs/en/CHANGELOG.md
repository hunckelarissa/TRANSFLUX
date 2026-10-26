> **Language:** English · [Русский](../ru/CHANGELOG.md)

# TRANSFLUX Changelog

Every notable change in the project is recorded here.

---

## Unreleased

---

## v0.5 — October 2026

**The Python library becomes the carrier of the paradigm. Package version 0.5.0; one living specification document (no version in the filename).**

- Decisions on the open questions: confidence stays `min()`; `FluxVar` has no `constraints` layer; `FlowingTrit` is a continuous float (`-0.5` is allowed, the range is not clamped).
- `FlowingTrit` and `FluxVar.flow()` (the Python form of the `~>` operator) were added to the `transflux` package.
- `TransfluxSystem` stores the latest `NoisyFloat` and counts cycles; panic still moves state to `fallback`.
- A DSL / LUMEN, Rust, benchmarks, neuromorphic hardware, and the far research backlog are deferred. Synthetic scenarios are the current check of the concept.
- The reasons: DR-016…DR-019. The decision journal: `docs/en/TRANSFLUX_Open_Questions.md`.
- Ten synthetic scenarios in `tests/synthetic/`: a ward, a drone, air, a trit, the fading of threat. Charts: `docs/figures/synthetic/`.
- `weighted_mean`: the mean of independent readings with weight `1/σ²`. Confidence follows the weight, not `min` (DR-020). A faulty sensor no longer sets the city index.
- The orchestrator's backup mode: after panic the system holds `backup_value` and `backup_noisy`, if that pair was set in advance. `recover()` returns it to the input. Without the pair, panic does not latch (DR-021).
- `classify_jump`: a jump of one sensor (`alone`) is distinguished from a jump together with neighbors (`shared`). Confidence and the value do not change (DR-022).
- `PolyphonicIdentity`: several masks of one entity. `erase` and `rotate_all` remove the old hash from every reference in the book. Panic does this only if the callback itself asked for the rotation (DR-023).
- The roadmap, the decision journal, the status in the README, specification §7–§8, the one-pager, the history, and the use-case introduction were brought in line with the library as of October 2026.
- Living documentation is bilingual. `README.md` is English, because that is what Git shows by default. Russian twins: `README.ru.md`, `CONTRIBUTING.ru.md`, `ROADMAP.ru.md`, and `docs/ru/`. English documents: `docs/en/`. The `research/` folder is not translated. The rule for future changes is in CONTRIBUTING.
- Repository layout: living docs under `docs/en/` and `docs/ru/`; historical material under `research/`.
- Living specification: a single pair `docs/en|ru/TRANSFLUX_Specification.md` (previous v0.2 copies removed from `docs/`).
- Package version: **0.5.0**.

---

## v0.3 — August 2026

**A reference implementation and repository infrastructure.**

- A reference implementation of the primitives was added in `src/transflux/` (FluxVar, NoisyFloat, SurvivalState, TransfluxSystem) — the specification's code, with no change of semantics.
- Invariant tests INV/OP/CP were added (`tests/`, 24 tests, pytest), following Formal Invariants.
- Added: an API reference, an architecture overview, and a history. ROADMAP.md was taken out of specification §7.
- README: version and status, the current repository layout, links to the new documents.
- CONTRIBUTING: a "local check" section (install, run the tests).
- `pyproject.toml` and `.gitignore` were added; the repository was initialized in git.
- Package and specification version: **0.3.0** / **v0.3**.

---

## v0.2 — April 2026

**The first formal revision. The move from a set of ideas to a specified system.**

### Specification

- `NoisyFloat.__mul__` was fixed: the formula `σ_z = √(b²·σ_a² + a²·σ_b²)` is correct for zero values (the old formula divided by zero).
- `__sub__` and `__truediv__` were added for NoisyFloat, with correct error propagation.
- A `dt <= 0` guard was added to `FluxVar.update()`.
- `decay_rate` was added to `SurvivalState`, to model the fading of threat.
- `print()` was replaced by the `on_trauma` callback in FluxVar (the side effect was removed from the data model).
- The `on_panic` callback was added to SurvivalState.
- The Coupling Protocol (§4.2) was added: a formal description of how the three axes are orchestrated.
- The Event Model (§4.3) was added: callback signatures, semantics, the escalation pattern.
- A Mermaid diagram of how the axes interact.
- Terminology was unified (momentum, dispersion, NoisyFlow). Appendix A was extended.

### Documentation

- Added: a description of the paradigm (Paradigm) for developers.
- Added: a comparison with related paradigms (Related Paradigms).
- Added: four worked use cases.
- Added: Design Rationale (15 reasoned decisions).
- Added: Formal Invariants (invariants, operation properties, test specifications).
- Added: a one-pager (an elevator pitch).
- Added: anti-patterns (typical mistakes).
- Added: a glossary (a reference card).
- Added: CONTRIBUTING.md and LICENSE (Apache 2.0).
- Marketing claims without evidence were removed ("100× faster than a GPU").
- Every editorial marker was removed (`НОВОЕ:`, `<!-- из файла: ... -->`).

### Manifesto

- Rewritten: duplicated sections were removed, and content from the notes was integrated.
- The tone stays sharp, and formulations that would cut off potential allies were removed.

---

## v0.1 — March 2026

**The first draft of the specification.**

- Three axes: FluxVar, NoisyFloat, SurvivalState.
- Python prototypes of each primitive.
- The formula `TRANSFLUX = Flow(State) · Uncertainty(Value) · Adaptation(Survival)`.
- The decomposition from 7 concepts down to 3 axes (with derived concepts).
- The first manifesto.

---

## v0.0 — March 2026

**The idea.** Notes, discussions, early experiments (`research/notes/`).
