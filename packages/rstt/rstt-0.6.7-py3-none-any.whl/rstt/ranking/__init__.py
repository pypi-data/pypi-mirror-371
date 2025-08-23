"""Modules for ranking purposes
"""

from . import rating

from .standing import Standing
from .ranking import Ranking

from .datamodel import KeyModel, GaussianModel

from .observer import (
    GameByGame, BatchGame,
    PlayerChecker, NoHandling
)
from .inferer import (
    Elo, Glicko,
    PlayerLevel, PlayerWinPRC, EventScoring
)

from .standard import (
    BTRanking, WinRate, SuccessRanking,
    BasicElo, BasicGlicko, BasicOS,
)

__all__ = [
    "rating",
    "Standing",
    "Ranking",
    "KeyModel",
    "GaussianModel",
    "GameByGame",
    "BatchGame",
    "PlayerChecker",
    "NoHandling",
    "Elo",
    "Glicko",
    "PlayerLevel",
    "PlayerWinPRC",
    "EventScoring",
    "BTRanking",
    "WinRate",
    "SuccessRanking",
    "BasicElo",
    "BasicGlicko",
    "BasicOS",
]
