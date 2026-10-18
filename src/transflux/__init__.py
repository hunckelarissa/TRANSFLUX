"""TRANSFLUX — Python-библиотека парадигмы непрерывного становления.

TRANSFLUX = Flow(State) · Uncertainty(Value) · Adaptation(Survival)

Три ортогональные оси:
- FluxVar        — State Model  (что у меня есть?)
- NoisyFloat     — Value Model  (насколько это точно?)
- SurvivalState  — Survival Model (что делать под угрозой?)

FlowingTrit — непрерывный трит: полюса -1, 0, +1, промежуточные float допустимы.
TransfluxSystem — оркестратор, который связывает три оси в одном цикле.

Источник истины: docs/TRANSFLUX_Specification_v0.3.md
"""

from .flowing_trit import FlowingTrit
from .flux_var import FluxVar, classify_jump
from .identity import PolyphonicIdentity
from .noisy_float import NoisyFloat, weighted_mean
from .survival import SurvivalState
from .system import TransfluxSystem

__version__ = "0.3.0"

__all__ = [
    "FlowingTrit",
    "FluxVar",
    "classify_jump",
    "PolyphonicIdentity",
    "NoisyFloat",
    "weighted_mean",
    "SurvivalState",
    "TransfluxSystem",
    "__version__",
]
