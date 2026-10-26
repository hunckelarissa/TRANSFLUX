> **Language:** English · [Русский](CONTRIBUTING.ru.md)

# Contributing to TRANSFLUX

Thank you for your interest. TRANSFLUX is an open paradigm, and a contribution can take several forms.

---

## Languages

Living documentation is bilingual. `README.md` is English, because that is what Git shows by default. Write the Russian twin in parallel:

| English | Russian |
|---|---|
| `README.md`, `CONTRIBUTING.md`, `ROADMAP.md` | `README.ru.md`, `CONTRIBUTING.ru.md`, `ROADMAP.ru.md` |
| `docs/en/<name>.md` | `docs/ru/<name>.md` |

A pull request that changes a document updates both versions in the same change. Do not translate `research/`: it is a historical archive. Shared charts stay in `docs/figures/`. The Apache 2.0 text in `LICENSE` stays in its official English wording.

Each document starts with a link to its twin. Keep identifiers (`FluxVar`, `DR-016`, `INV-F1`) the same in both languages.

---

## Kinds of contribution

### Documentation and concepts

- **A new use case** — a worked scenario that applies the three axes to a concrete problem. Format: see `docs/en/TRANSFLUX_Use_Cases.md` and `docs/ru/TRANSFLUX_Use_Cases.md`.
- **A design rationale** — the reason for a new design decision, or a revision of an existing one. Format: DR-NNN in the design-rationale document, both languages.
- **A formal invariant** — a new provable or testable property. Format: INV-X / OP-X / CP-X in the formal-invariants document, both languages.
- **A comparison with a paradigm** — an honest comparison of TRANSFLUX with a paradigm or technology not yet covered. Format: a section in the related-paradigms document, both languages.

### Specification

- **A tighter formalism** — a stricter statement, a fix to a formula, a clearer semantics.
- **A new derived concept** — if it follows from the three axes (completeness criterion, specification §6).
- **A revision of the basis** — if you find a fundamental question the three axes do not cover. That is a serious proposal and needs an argument.

### Implementation

- **A prototype in another language** — Rust, Haskell, Julia, and others. These are welcome as experiments; the current carrier of the paradigm is the Python library.
- **A library** — `NoisyFloat`, `FluxVar`, or `SurvivalState` as its own package.
- **An integration** — wrappers for PyTorch, TensorFlow, or edge-AI frameworks. These are deferred on the roadmap until the concept check asks for them.
- **Tests** — implementations of the test specifications in the formal-invariants document.

---

## Quality bar

### Documentation

- No marketing claims without evidence. Not allowed: "100× faster". Allowed: "in theory this can be more efficient — it needs validation".
- Keep the registers apart: the manifesto is voice, the specification is formalism, the paradigm document is explanation. Do not mix them.
- Say explicitly whether an idea is Core or research backlog.
- Ship both languages together.

### Code

- Code inside the specification is illustrative (Python; readability over speed).
- Implementation code comes with tests that cover the invariants in Formal Invariants.
- The canonical API is what the `transflux` package exports (`FluxVar`, `NoisyFloat`, `SurvivalState`, `TransfluxSystem`, `FlowingTrit`, `weighted_mean`, `classify_jump`, `PolyphonicIdentity`). Other names are aliases or experiments.

### Local check

The library is in `src/transflux/`. Tests are in `tests/` (invariants and `tests/synthetic/`):

```
pip install -e .[dev]
pytest
```

A pull request that changes the implementation must pass every test. A pull request that changes an invariant must update the matching tests.

---

## Process

1. Open an issue that describes the contribution.
2. Discuss the approach before the work starts, especially for specification changes.
3. Open a pull request.
4. Every pull request updates the documents it affects, in both languages. A specification change updates the invariants. A new use case stays consistent with the current specification.

---

## What we do not accept

- Changes that break the orthogonality of the three axes without an argument for revising the basis.
- Irreversible or destructive operations without an explicit Consent-First policy.
- Performance claims without benchmarks.

---

## License

Contributions fall under the project license, Apache 2.0 (see `LICENSE`).
