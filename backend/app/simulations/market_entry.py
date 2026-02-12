"""Market Entry Game — entry under demand uncertainty."""
from __future__ import annotations
import random, time, math
from app.models.schemas import GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium
from app.simulations.base import BaseGame


def _strat_always(_h, _cap, _cost):
    return True

def _strat_never(_h, _cap, _cost):
    return False

def _strat_threshold(_h, cap, cost):
    return cap / 3 > cost

def _strat_random(_h, _cap, _cost):
    return random.random() < 0.5

def _strat_adaptive(h, cap, cost):
    if not h:
        return True
    recent = h[-5:]
    avg_ent = sum(e["n_entrants"] for e in recent) / len(recent)
    return cap / max(1, 1 + avg_ent) > cost

def _strat_cautious(h, _cap, _cost):
    if not h:
        return True
    recent = h[-5:]
    return sum(e["profit"] for e in recent) / len(recent) > 0

ENTRY_STRATEGIES = {
    "always_enter": _strat_always,
    "never_enter": _strat_never,
    "threshold": _strat_threshold,
    "random_50": _strat_random,
    "adaptive": _strat_adaptive,
    "cautious": _strat_cautious,
}


class MarketEntry(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="market_entry", name="Market Entry Game", category="underrated", tier=2,
            short_description="Enter a crowded market under demand uncertainty?",
            long_description="N potential entrants simultaneously decide whether to enter a market with limited capacity. More entrants means lower per-firm profit. Entry costs are sunk. Explores excess entry and the role of uncertainty.",
            parameters=[
                ParameterSpec(name="simulations", type="int", default=300, min=10, max=5000, description="Market periods"),
                ParameterSpec(name="n_potential", type="int", default=10, min=2, max=50, description="Number of potential entrants"),
                ParameterSpec(name="market_capacity", type="float", default=100.0, min=10, max=1000, description="Total market revenue"),
                ParameterSpec(name="entry_cost", type="float", default=15.0, min=1, max=200, description="Fixed entry cost"),
                ParameterSpec(name="strategy", type="select", default="threshold", options=list(ENTRY_STRATEGIES), description="Entry strategy for each firm"),
            ],
            available=True, engine="server", tags=["entry", "uncertainty"],
            theory_card="## Excess Entry Theorem\nFree entry leads to **too many firms** relative to the social optimum — each entrant captures profit but also steals business from others.\n\n## Optimal Entry\nThe socially optimal number of entrants: n* = √(market_capacity / entry_cost).\n\n## Key Insight\nIndividual rationality leads to **crowding** — markets often have more entrants than is efficient.",
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        sims = config.get("simulations", 300)
        n_pot = config.get("n_potential", 10)
        cap = config.get("market_capacity", 100.0)
        cost = config.get("entry_cost", 15.0)
        strat = ENTRY_STRATEGIES.get(config.get("strategy", "threshold"), _strat_threshold)
        rd, history = [], []
        total_profit = 0.0
        entries_list = []
        for sim in range(1, sims + 1):
            market_var = cap * random.uniform(0.7, 1.3)
            entries = sum(1 for _ in range(n_pot) if strat(history, market_var, cost))
            entries = max(0, entries)
            rev_per_firm = market_var / max(1, entries) if entries > 0 else 0
            profit = rev_per_firm - cost if entries > 0 else 0
            total_profit += profit * entries
            entries_list.append(entries)
            entry = {"n_entrants": entries, "profit": profit, "market": market_var}
            history.append(entry)
            rd.append(RoundData(round_num=sim, actions=[entries], payoffs=[round(profit, 1)],
                state={"n_entrants": entries, "profit_per_firm": round(profit, 1),
                       "market_size": round(market_var, 1),
                       "avg_entrants": sum(entries_list) / sim,
                       "overcrowding": entries > cap / cost}))
        optimal_n = math.sqrt(cap / cost)
        avg_entries = sum(entries_list) / sims
        total_entries = sum(entries_list)
        return SimulationResult(game_id="market_entry", config=config, rounds=rd,
            equilibria=[Equilibrium(name="Free Entry Equilibrium", strategies=["Enter if profitable"],
                payoffs=[0], description=f"Entry drives profit toward zero. Optimal n ≈ {optimal_n:.1f}")],
            summary={"avg_entrants": avg_entries, "optimal_entrants": round(optimal_n, 1),
                     "excess_entry": round(avg_entries - optimal_n, 1),
                     "avg_profit_per_firm": total_profit / max(1, total_entries),
                     "overcrowding_rate": sum(1 for e in entries_list if e > int(optimal_n) + 1) / sims},
            metadata={"compute_time_ms": round((time.time() - t0) * 1000, 2), "engine": "server"})
