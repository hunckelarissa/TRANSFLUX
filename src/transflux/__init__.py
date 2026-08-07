"""TRANSFLUX — референсная реализация примитивов спецификации v0.2.

TRANSFLUX = Flow(State) · Uncertainty(Value) · Adaptation(Survival)

Три ортогональные оси:
- FluxVar        — State Model  (что у меня есть?)
- NoisyFloat     — Value Model  (насколько это точно?)
- SurvivalState  — Survival Model (что делать под угрозой?)

TransfluxSystem — рекомендуемый паттерн оркестрации (не часть ядра).

Источник истины: docs/TRANSFLUX_Specification_v0.2.md
"""

from .flux_var import FluxVar
from .noisy_float import NoisyFloat
from .survival import SurvivalState
from .system import TransfluxSystem

__version__ = "0.2.0"

__all__ = ["FluxVar", "NoisyFloat", "SurvivalState", "TransfluxSystem", "__version__"]
