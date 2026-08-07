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

## Участие

См. [CONTRIBUTING.md](CONTRIBUTING.md).

## Структура репозитория

- **`docs/`** — актуальная документация (источник истины).
- **`src/transflux/`** — референсная реализация примитивов (ранний прототип).
- **`tests/`** — тесты по спецификациям из [Formal Invariants](docs/TRANSFLUX_Formal_Invariants.md).
- **`research/main/`** — исторические версии (v0.1).
- **`docs/TRANSFLUX_Specification_v0.2.md`** — предыдущая спецификация (v0.2).
- **`research/notes/`** — заметки, диаграммы, ранние эксперименты.

## Лицензия

Apache 2.0 — см. [LICENSE](LICENSE).

## Статус

Черновик / в разработке. Референсная реализация в `src/` — ранний прототип: примитивы из спецификации без гарантий стабильности API. Дорожная карта — [ROADMAP.md](ROADMAP.md), открытые вопросы — §8 спецификации.

---

*TRANSFLUX — эпистемология вычислений, которую можно воплотить в любом языке или стеке.*
