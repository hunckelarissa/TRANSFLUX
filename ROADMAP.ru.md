> **Язык:** русский · [English](ROADMAP.md)

# TRANSFLUX Roadmap

> Статус на октябрь 2026. Формальные решения — [docs/ru/TRANSFLUX_Open_Questions.md](docs/ru/TRANSFLUX_Open_Questions.md) и DR-016…DR-030. Спецификация — [docs/ru/TRANSFLUX_Specification.md](docs/ru/TRANSFLUX_Specification.md).

## Уже в Python-библиотеке

Носитель парадигмы — пакет `src/transflux/`.

| Компонент | Что делает |
|---|---|
| `FluxVar`, `flow()` | состояние как русло; `flow` — Python-форма оператора `~>`; comfort реагирует на trauma/calm |
| `NoisyFloat` | арифметика с переносом σ; confidence через `min` |
| `weighted_mean` | среднее независимых измерений, вес `1/σ²` |
| `FlowingTrit` | непрерывный трит; `-0.5` хранится как есть |
| `classify_jump` | `calm` / `alone` / `shared`; confidence не меняет |
| `SurvivalState` | угроза, panic, смена своего `identity_hash`, scope-хуки |
| `PolyphonicIdentity` | несколько масок; `erase` и `rotate_all` внутри одной книги |
| `IdentityLedger` | зарегистрированные книги; `erase` между книгами одним новым хешем |
| `TransfluxSystem` | цикл трёх осей, `peak_threat`, запасной режим `degraded`, опциональная угроза stale/margin |
| `NoisyFlow` | алиас `FluxVar[NoisyFloat]` |
| `stale_threat` / `uncertainty_margin_threat` | хелперы тишины и запаса по σ |
| `weighted_mean(..., correlation= / covariance=)` | скалярное ρ или полная матрица GLS |
| `PolyphonicIdentity.live` / `erase_live` | weak-реестр живых книг; opt-in стирание по процессу |
| `ScarMemory` | именованные шрамы; `amplify` / `fade`; panic сам их не ставит |
| Синтетические сценарии | `tests/synthetic/`, графики в `docs/figures/synthetic/` |

## Ближайшее, если углублять библиотеку

Это разрывы между сценариями и кодом. Часть поведения специально оставлена вызывающему коду (DR-017, DR-021, DR-022, DR-023).

- Остальные идеи исследовательского бэклога (Grief-Driven GC, Algebra of Change, …) — по-прежнему гипотезы, не типы библиотеки.
- DSL / другие рантаймы остаются отложенными (см. ниже).

## Отложено

Пока проверка концепции — синтетические сценарии, не другое железо:

- оператор `~>` как синтаксис языка, DSL и вариант для LUMEN;
- реализация на Rust;
- бенчмарки, нейроморфные чипы, обёртки PyTorch / TensorFlow.

Если библиотеку признают достаточной проверкой, вероятное продолжение — эмбеддинг и микроконтроллеры. Стек к тому моменту выбирается заново.

## Исследовательский бэклог (далеко, не Core)

Идеи записаны. У `ScarMemory` есть лёгкая проверка в библиотеке (DR-028). Остальное не в текущей работе:

| Идея | К какой оси | Гипотеза |
|---|---|---|
| Grief-Driven GC | State | GC как протокол утраты с историей ссылок |
| Dysphoric Compiler | Value | Диагностика «дискомфорта» в коде вместо сухих ошибок |
| Chosen Family Topology | State | Граф зависимостей как отношения с историей и доверием |
| Body-Budget Scheduler | State | Планировщик с моделью «энергии» и «усталости» |
| Liminal Type Inference | Value | Промежуточные типы как валидные состояния |
| ~~Scar Memory~~ | Survival | **в библиотеке как `ScarMemory`** — усиленные проверки в местах прошлых сбоев |
| Euphoria-Driven Optimization | Value | Максимизация comfort вместо минимизации loss |
| Algebra of Change | State | Операции над изменениями, композиция трансформаций |
| Time-Native Programming | State | Время и причинность как first-class |
