> **Язык:** русский · [English](README.md)

# TRANSFLUX

**Пакет: 0.5.0 · Спецификация: черновик (ревизия август 2026).**

Вычислительная парадигма **непрерывного становления**: состояние как поток, значение с неопределённостью, выживание под угрозой.

```
TRANSFLUX = Flow(State) · Uncertainty(Value) · Adaptation(Survival)
```

## Документация

Каждый живой документ существует параллельно на русском и на английском. Файл `README.md` — английский: его показывает Git по умолчанию. Русские пары в корне имеют суффикс `.ru.md`, остальные лежат в `docs/ru/`. Английские документы — в `docs/en/`. Папка `research/` — исторический архив и не переводится.

| Документ | Назначение |
|----------|------------|
| [One-pager](docs/ru/TRANSFLUX_One_Pager.md) | Обзор на одну страницу — начни здесь |
| [Простыми словами](docs/ru/TRANSFLUX_Simple_Explanation.md) | Что такое TRANSFLUX, без жаргона |
| [Спецификация](docs/ru/TRANSFLUX_Specification.md) | Формальное ядро: примитивы, код, взаимодействие осей |
| [Описание парадигмы](docs/ru/TRANSFLUX_Paradigm.md) | Для разработчиков: аналогии, примеры, области применения |
| [Манифест](docs/ru/TRANSFLUX_Manifesto.md) | Позиция и призыв: голос парадигмы |
| [Сценарии применения](docs/ru/TRANSFLUX_Use_Cases.md) | Четыре проработанных use case |
| [Смежные парадигмы](docs/ru/TRANSFLUX_Related_Paradigms.md) | Сравнение с fuzzy logic, reactive streams, probabilistic programming и др. |
| [Design Rationale](docs/ru/TRANSFLUX_Design_Rationale.md) | Обоснование ключевых проектных решений |
| [Формальные инварианты](docs/ru/TRANSFLUX_Formal_Invariants.md) | Гарантии, свойства, тестовые спецификации |
| [Anti-patterns](docs/ru/TRANSFLUX_Anti_Patterns.md) | Типичные ошибки: как НЕ надо использовать TRANSFLUX |
| [Глоссарий](docs/ru/TRANSFLUX_Glossary.md) | Термины, инварианты, DR — всё на одной странице |
| [API Reference](docs/ru/TRANSFLUX_API_Reference.md) | Компактный справочник по примитивам и callbacks |
| [Архитектура](docs/ru/TRANSFLUX_Architecture.md) | Обзор верхнего уровня: три оси и их взаимодействие |
| [История](docs/ru/TRANSFLUX_History.md) | Как и почему возник TRANSFLUX |
| [Changelog](docs/ru/CHANGELOG.md) | История изменений по версиям |
| [Открытые вопросы](docs/ru/TRANSFLUX_Open_Questions.md) | Принятые решения и то, что отложено |

## Участие

См. [CONTRIBUTING.ru.md](CONTRIBUTING.ru.md). Изменение документации попадает в обе языковые версии.

## Структура репозитория

- **`docs/en/`** — актуальная документация на английском.
- **`docs/ru/`** — те же документы на русском.
- **`docs/figures/synthetic/`** — графики синтетических сценариев (общие; подписи следуют тексту тестов).
- **`src/transflux/`** — Python-библиотека примитивов и оркестратора.
- **`tests/`** — тесты инвариантов и синтетические сценарии (`tests/synthetic/`).
- **`research/main/`** — исторические версии (включая ранние спецификации). Не входят в билингвальный набор.
- **`research/notes/`** — заметки, диаграммы, ранние эксперименты. Не переводятся.

## Лицензия

Apache 2.0 — см. [LICENSE](LICENSE).

## Статус

Черновик / в разработке, октябрь 2026. Носитель парадигмы — Python-библиотека в `src/transflux/`: три оси, `FlowingTrit`, `weighted_mean`, `classify_jump`, `PolyphonicIdentity`, оркестратор с запасным режимом. Концепция прогнана на синтетических сценариях. API ещё не обещает стабильность. Дорожная карта — [ROADMAP.ru.md](ROADMAP.ru.md), журнал решений — [docs/ru/TRANSFLUX_Open_Questions.md](docs/ru/TRANSFLUX_Open_Questions.md).

---

*TRANSFLUX — эпистемология вычислений, которую можно воплотить в любом языке или стеке.*
