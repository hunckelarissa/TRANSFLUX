> **Language:** English · [Русский](README.ru.md)

# TRANSFLUX

**Package: 0.5.0 · Specification: draft (August 2026 revision).**

A computational paradigm of **continuous becoming**: state as flow, value with uncertainty, survival under threat.

```
TRANSFLUX = Flow(State) · Uncertainty(Value) · Adaptation(Survival)
```

## Documentation

Every living document has a parallel English and Russian version. This file is the English default for Git. Russian twins use a `.ru.md` suffix at the repository root and live under `docs/ru/`. English documents live under `docs/en/`. The `research/` folder is a historical archive and is not translated.

| Document | Purpose |
|----------|---------|
| [One-pager](docs/en/TRANSFLUX_One_Pager.md) | One-page overview — start here |
| [Plain-language explanation](docs/en/TRANSFLUX_Simple_Explanation.md) | What TRANSFLUX is, without the jargon |
| [Specification](docs/en/TRANSFLUX_Specification.md) | Formal core: primitives, code, how the axes interact |
| [Paradigm](docs/en/TRANSFLUX_Paradigm.md) | For developers: analogies, examples, domains |
| [Manifesto](docs/en/TRANSFLUX_Manifesto.md) | Position and voice of the paradigm |
| [Use cases](docs/en/TRANSFLUX_Use_Cases.md) | Four worked examples |
| [Related paradigms](docs/en/TRANSFLUX_Related_Paradigms.md) | Comparison with fuzzy logic, reactive streams, probabilistic programming, and others |
| [Design rationale](docs/en/TRANSFLUX_Design_Rationale.md) | Why the key design decisions were made |
| [Formal invariants](docs/en/TRANSFLUX_Formal_Invariants.md) | Guarantees, properties, test specifications |
| [Anti-patterns](docs/en/TRANSFLUX_Anti_Patterns.md) | Typical mistakes: how not to use TRANSFLUX |
| [Glossary](docs/en/TRANSFLUX_Glossary.md) | Terms, invariants, and design records on one page |
| [API reference](docs/en/TRANSFLUX_API_Reference.md) | Compact reference for primitives and callbacks |
| [Architecture](docs/en/TRANSFLUX_Architecture.md) | High-level view: three axes and their interaction |
| [History](docs/en/TRANSFLUX_History.md) | How and why TRANSFLUX came to be |
| [Changelog](docs/en/CHANGELOG.md) | Version-by-version change history |
| [Decisions](docs/en/TRANSFLUX_Open_Questions.md) | Decisions already made, and what is deferred |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). A documentation change lands in both languages.

## Repository layout

- **`docs/en/`** — current documentation in English.
- **`docs/ru/`** — the same documents in Russian.
- **`docs/figures/synthetic/`** — charts for the synthetic scenarios (shared; labels follow the test text).
- **`src/transflux/`** — the Python library: primitives and the orchestrator.
- **`tests/`** — invariant tests and synthetic scenarios (`tests/synthetic/`).
- **`research/main/`** — historical versions (including early specs). Not part of the bilingual set.
- **`research/notes/`** — notes, diagrams, early experiments. Not translated.

## License

Apache 2.0 — see [LICENSE](LICENSE).

## Status

Draft / in development, October 2026. The carrier of the paradigm is the Python library in `src/transflux/`: the three axes, `FlowingTrit`, `weighted_mean`, `classify_jump`, `PolyphonicIdentity`, and an orchestrator with a backup mode. The concept has been run through synthetic scenarios. The API does not yet promise stability. Roadmap: [ROADMAP.md](ROADMAP.md). Decision journal: [docs/en/TRANSFLUX_Open_Questions.md](docs/en/TRANSFLUX_Open_Questions.md).

---

*TRANSFLUX is an epistemology of computation that can be embodied in any language or stack.*
