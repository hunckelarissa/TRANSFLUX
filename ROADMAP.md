# TRANSFLUX Roadmap

> Вынесено из спецификации (§7). Источник истины по статусу компонентов — [docs/TRANSFLUX_Specification_v0.2.md](docs/TRANSFLUX_Specification_v0.2.md).

## Текущий статус реализации

| Компонент | Статус | Язык |
|---|---|---|
| `FluxVar<T>` | референсная реализация в `src/transflux/` | Python |
| `NoisyFloat` | референсная реализация в `src/transflux/` | Python |
| `SurvivalState` | референсная реализация в `src/transflux/` | Python |
| `TransfluxSystem` (orchestrator) | референсная реализация в `src/transflux/` | Python |
| Тесты INV / OP / CP | реализованы в `tests/` | Python (pytest) |
| Оператор `~>` | не реализован | LUMEN (планируется) |

## Ближайшие шаги (Core)

1. **TRANSFLUX Runtime v0.1** — один исполняемый модуль, где три оси реально связаны и демонстрируют emergent-поведение (базовый цикл уже доступен как `TransfluxSystem.tick()`).
2. **NoisyFloat как отдельная библиотека** — pip-пакет с тестами, документацией и примерами для научных вычислений.

## Среднесрочные (расширения)

3. Mapping примитивов TRANSFLUX на нейроморфное железо (Intel Hala Point, BrainChip Akida и др.) — требует инженерной валидации.
4. Реализация ядра на Rust для performance-critical сценариев.
5. Интеграция с PyTorch / TensorFlow (обёртки весов и активаций в FluxVar / NoisyFloat).

## Исследовательский бэклог (не Core)

Идеи зафиксированы как исследовательские, без обязательства войти в ядро:

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

## Открытые вопросы

См. §8 спецификации: формализм ядра (constraints, Trit, стратегия propagation of confidence), валидация (нейроморфный PoC, бенчмарки).
