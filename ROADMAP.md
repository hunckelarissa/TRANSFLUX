# TRANSFLUX Roadmap

> Статус на октябрь 2026. Формальные решения — [docs/TRANSFLUX_Open_Questions.md](docs/TRANSFLUX_Open_Questions.md) и DR-016…DR-023. Спецификация — [docs/TRANSFLUX_Specification_v0.3.md](docs/TRANSFLUX_Specification_v0.3.md).

## Уже в Python-библиотеке

Носитель парадигмы — пакет `src/transflux/`.

| Компонент | Что делает |
|---|---|
| `FluxVar`, `flow()` | состояние как русло; `flow` — Python-форма оператора `~>` |
| `NoisyFloat` | арифметика с переносом σ; confidence через `min` |
| `weighted_mean` | среднее независимых измерений, вес `1/σ²` |
| `FlowingTrit` | непрерывный трит; `-0.5` хранится как есть |
| `classify_jump` | `calm` / `alone` / `shared`; confidence не меняет |
| `SurvivalState` | угроза, panic, смена своего `identity_hash` |
| `PolyphonicIdentity` | несколько масок; `erase` и `rotate_all` внутри одной книги |
| `TransfluxSystem` | цикл трёх осей, `peak_threat`, запасной режим `degraded` |
| Синтетические сценарии | `tests/synthetic/`, графики в `docs/figures/synthetic/` |

## Ближайшее, если углублять библиотеку

Это разрывы между сценариями и кодом. Часть поведения специально оставлена вызывающему коду (DR-017, DR-021, DR-022, DR-023).

- `scope` (`local` / `process` / `system`) только хранится: panic при любом масштабе делает одно и то же.
- `erase` видит ссылки внутри одной `PolyphonicIdentity`. Хеш вне книги не стирается.
- `comfort` само не реагирует на травму и на спокойный ход.
- `NoisyFlow` — договорённость `FluxVar[NoisyFloat]`, отдельного типа нет.
- `weighted_mean` предполагает независимость измерений.
- Запас прочности от uncertainty и таймер «давно не было сигнала» не выделены в отдельные функции: это вход `tick` и `threat_delta`.

## Отложено

Пока проверка концепции — синтетические сценарии, не другое железо:

- оператор `~>` как синтаксис языка, DSL и вариант для LUMEN;
- реализация на Rust;
- бенчмарки, нейроморфные чипы, обёртки PyTorch / TensorFlow.

Если библиотеку признают достаточной проверкой, вероятное продолжение — эмбеддинг и микроконтроллеры. Стек к тому моменту выбирается заново.

## Исследовательский бэклог (далеко, не Core)

Идеи записаны, в работу не входят:

| Идея | К какой оси | Гипотеза |
|---|---|---|
| Grief-Driven GC | State | GC как протокол утраты с историей ссылок |
| Dysphoric Compiler | Value | Диагностика «дискомфорта» в коде вместо сухих ошибок |
| Chosen Family Topology | State | Граф зависимостей как отношения с историей и доверием |
| Body-Budget Scheduler | State | Планировщик с моделью «энергии» и «усталости» |
| Liminal Type Inference | Value | Промежуточные типы как валидные состояния |
| Scar Memory | Survival | Усиленные проверки в местах прошлых сбоев |
| Euphoria-Driven Optimization | Value | Максимизация comfort вместо минимизации loss |
| Algebra of Change | State | Операции над изменениями, композиция трансформаций |
| Time-Native Programming | State | Время и причинность как first-class |
