# TRANSFLUX

**Версия спецификации: v0.3 (август 2026) — черновик.**

Вычислительная парадигма **непрерывного становления**: состояние как поток, значение с неопределённостью, выживание под угрозой.

```
TRANSFLUX = Flow(State) · Uncertainty(Value) · Adaptation(Survival)
```

## Документация

| Документ | Назначение |
|----------|------------|
| [One-pager](docs/TRANSFLUX_One_Pager.md) | Обзор на одну страницу — начни здесь |
| [Спецификация v0.3](docs/TRANSFLUX_Specification_v0.3.md) | Формальное ядро: примитивы, код, взаимодействие осей |
| [Описание парадигмы](docs/TRANSFLUX_Paradigm.md) | Для разработчиков: аналогии, примеры, области применения |
| [Манифест](docs/TRANSFLUX_Manifesto.md) | Позиция и призыв: голос парадигмы |
| [Сценарии применения](docs/TRANSFLUX_Use_Cases.md) | Четыре проработанных use case |
| [Смежные парадигмы](docs/TRANSFLUX_Related_Paradigms.md) | Сравнение с fuzzy logic, reactive streams, probabilistic programming и др. |
| [Design Rationale](docs/TRANSFLUX_Design_Rationale.md) | Обоснование ключевых проектных решений |
| [Формальные инварианты](docs/TRANSFLUX_Formal_Invariants.md) | Гарантии, свойства, тестовые спецификации |
| [Anti-patterns](docs/TRANSFLUX_Anti_Patterns.md) | Типичные ошибки: как НЕ надо использовать TRANSFLUX |
| [Глоссарий](docs/TRANSFLUX_Glossary.md) | Термины, инварианты, DR — всё на одной странице |
| [API Reference](docs/TRANSFLUX_API_Reference.md) | Компактный справочник по примитивам и callbacks |
| [Архитектура](docs/TRANSFLUX_Architecture.md) | Обзор верхнего уровня: три оси и их взаимодействие |
| [История](docs/TRANSFLUX_History.md) | Как и почему возник TRANSFLUX |
| [Changelog](docs/CHANGELOG.md) | История изменений по версиям |
| [Открытые вопросы](docs/TRANSFLUX_Open_Questions.md) | Принятые решения и то, что отложено |

## Участие

См. [CONTRIBUTING.md](CONTRIBUTING.md).

## Структура репозитория

- **`docs/`** — актуальная документация (источник истины).
- **`src/transflux/`** — Python-библиотека примитивов и оркестратора.
- **`tests/`** — тесты инвариантов и синтетические сценарии (`tests/synthetic/`).
- **`docs/figures/synthetic/`** — графики этих сценариев.
- **`research/main/`** — исторические версии (v0.1).
- **`docs/TRANSFLUX_Specification_v0.2.md`** — предыдущая спецификация (v0.2).
- **`research/notes/`** — заметки, диаграммы, ранние эксперименты.

## Лицензия

Apache 2.0 — см. [LICENSE](LICENSE).

## Статус

Черновик / в разработке, октябрь 2026. Носитель парадигмы — Python-библиотека в `src/transflux/`: три оси, `FlowingTrit`, `weighted_mean`, `classify_jump`, `PolyphonicIdentity`, оркестратор с запасным режимом. Концепция прогнана на синтетических сценариях. API ещё не обещает стабильность. Дорожная карта — [ROADMAP.md](ROADMAP.md), журнал решений — [docs/TRANSFLUX_Open_Questions.md](docs/TRANSFLUX_Open_Questions.md).

---

*TRANSFLUX — эпистемология вычислений, которую можно воплотить в любом языке или стеке.*
