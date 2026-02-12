"""Game registry — maps game IDs to simulation instances."""
from __future__ import annotations
from app.simulations.base import BaseGame
from app.simulations.prisoners_dilemma import PrisonersDilemma
from app.simulations.public_goods import PublicGoodsGame
from app.simulations.colonel_blotto import ColonelBlotto
from app.simulations.auction_mechanisms import AuctionMechanisms
from app.simulations.network_contagion import NetworkContagion
from app.simulations.stag_hunt import StagHunt
from app.simulations.battle_of_sexes import BattleOfSexes
from app.simulations.matching_pennies import MatchingPennies
from app.simulations.rock_paper_scissors import RockPaperScissors
from app.simulations.ultimatum import UltimatumGame
from app.simulations.centipede import CentipedeGame
from app.simulations.ess_module import ESSModule
from app.simulations.war_of_attrition import WarOfAttrition
from app.simulations.bayesian_signaling import BayesianSignaling
from app.simulations.supply_chain import SupplyChain
from app.simulations.stackelberg import Stackelberg
from app.simulations.cournot_bertrand import CournotBertrand
from app.simulations.reputation_trust import ReputationTrust
from app.simulations.market_entry import MarketEntry
from app.simulations.coordination_general import CoordinationGeneral
from app.simulations.coalition_formation import CoalitionFormation
from app.simulations.multi_agent_negotiation import MultiAgentNegotiation
from app.models.schemas import GameInfo

# All 22 active game instances
_GAMES: dict[str, BaseGame] = {
    # Tier 1 — Classical
    "prisoners_dilemma": PrisonersDilemma(),
    "public_goods": PublicGoodsGame(),
    "stag_hunt": StagHunt(),
    "battle_of_sexes": BattleOfSexes(),
    "matching_pennies": MatchingPennies(),
    "rock_paper_scissors": RockPaperScissors(),
    "ultimatum": UltimatumGame(),
    "centipede": CentipedeGame(),
    "ess_module": ESSModule(),
    # Tier 2 — Underrated
    "colonel_blotto": ColonelBlotto(),
    "auction_mechanisms": AuctionMechanisms(),
    "network_contagion": NetworkContagion(),
    "war_of_attrition": WarOfAttrition(),
    "bayesian_signaling": BayesianSignaling(),
    "supply_chain": SupplyChain(),
    "stackelberg": Stackelberg(),
    "cournot_bertrand": CournotBertrand(),
    "reputation_trust": ReputationTrust(),
    "market_entry": MarketEntry(),
    "coordination_general": CoordinationGeneral(),
    # Tier 3 — Innovation
    "coalition_formation": CoalitionFormation(),
    "multi_agent_negotiation": MultiAgentNegotiation(),
}


def get_game(game_id: str) -> BaseGame | None:
    return _GAMES.get(game_id)


def get_all_game_info() -> list[GameInfo]:
    return [g.info() for g in _GAMES.values()]


def get_game_info(game_id: str) -> GameInfo | None:
    if game_id in _GAMES:
        return _GAMES[game_id].info()
    return None
