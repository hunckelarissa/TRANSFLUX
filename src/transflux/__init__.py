"""TRANSFLUX — Python-библиотека парадигмы непрерывного становления.

TRANSFLUX = Flow(State) · Uncertainty(Value) · Adaptation(Survival)

Три ортогональные оси:
- FluxVar        — State Model  (что у меня есть?)
- NoisyFloat     — Value Model  (насколько это точно?)
- SurvivalState  — Survival Model (что делать под угрозой?)

FlowingTrit — непрерывный трит: полюса -1, 0, +1, промежуточные float допустимы.
NoisyFlow — алиас FluxVar[NoisyFloat] (пересечение осей I и II).
ScarMemory — шрамы мест, где уже был сбой (производная Survival).
TransfluxSystem — оркестратор, который связывает три оси в одном цикле.

Источник истины: docs/en/TRANSFLUX_Specification.md
и docs/ru/TRANSFLUX_Specification.md
"""

from .flowing_trit import FlowingTrit
from .flux_var import FluxVar, classify_jump
from .identity import IdentityLedger, PolyphonicIdentity
from .noisy_float import NoisyFloat, weighted_mean
from .scar import ScarMemory
from .survival import SurvivalState, stale_threat, uncertainty_margin_threat
from .system import TransfluxSystem

NoisyFlow = FluxVar[NoisyFloat]

__version__ = "0.5.0"

__all__ = [
    "FlowingTrit",
    "FluxVar",
    "classify_jump",
    "IdentityLedger",
    "PolyphonicIdentity",
    "NoisyFloat",
    "NoisyFlow",
    "ScarMemory",
    "weighted_mean",
    "SurvivalState",
    "stale_threat",
    "uncertainty_margin_threat",
    "TransfluxSystem",
    "__version__",
]
