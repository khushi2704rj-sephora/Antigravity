"""Colonel Blotto Game — resource allocation across battlefields."""
from __future__ import annotations
import random
import time
import numpy as np
from app.models.schemas import (
    GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium,
)
from app.simulations.base import BaseGame


def _random_allocation(troops: int, fields: int) -> list[int]:
    """Generate a random allocation of troops across battlefields (uniform Dirichlet)."""
    cuts = sorted(random.sample(range(1, troops + fields), fields - 1))
    alloc = [cuts[0]]
    for i in range(1, len(cuts)):
        alloc.append(cuts[i] - cuts[i - 1])
    alloc.append(troops + fields - 1 - cuts[-1])
    return [max(0, a - 1) for a in alloc]


class ColonelBlotto(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="colonel_blotto",
            name="Colonel Blotto",
            category="underrated",
            tier=2,
            short_description="Allocate limited troops across multiple battlefields.",
            long_description=(
                "Two colonels independently distribute their armies across N battlefields. "
                "Whoever has more troops on a battlefield wins it. The player who wins the "
                "majority of battlefields wins the war. No pure-strategy Nash equilibrium exists "
                "for symmetric Blotto — optimal play requires randomization. Applications include "
                "political campaign spending, R&D budgets, and cybersecurity resource allocation."
            ),
            parameters=[
                ParameterSpec(name="n_battlefields", type="int", default=5, min=3, max=15,
                              description="Number of battlefields"),
                ParameterSpec(name="troops_p1", type="int", default=100, min=10, max=1000,
                              description="Total troops for Player 1"),
                ParameterSpec(name="troops_p2", type="int", default=100, min=10, max=1000,
                              description="Total troops for Player 2"),
                ParameterSpec(name="n_simulations", type="int", default=1000, min=100, max=10000,
                              description="Monte Carlo simulations to run"),
            ],
            available=True,
            engine="server",
            tags=["resource-allocation", "military", "political", "no-pure-NE"],
            theory_card=(
                "## Borel's Game (1921)\n"
                "Colonel Blotto was introduced by Émile Borel. It has NO pure-strategy Nash "
                "equilibrium for symmetric resource budgets.\n\n"
                "## Optimal Randomization\n"
                "Roberson (2006) fully solved the two-player case: players should use a "
                "joint-uniform distribution across battlefields.\n\n"
                "## Real-World Use\n"
                "- **Political campaigns**: allocating ad spending across swing states\n"
                "- **Cybersecurity**: distributing defenders across attack surfaces\n"
                "- **Sports**: allocating star players across games/positions"
            ),
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        fields = config.get("n_battlefields", 5)
        t1 = config.get("troops_p1", 100)
        t2 = config.get("troops_p2", 100)
        n_sims = config.get("n_simulations", 1000)

        p1_wins = 0
        p2_wins = 0
        draws = 0
        battlefield_wins_p1 = [0] * fields
        round_data: list[RoundData] = []

        # Sample rounds to include in the response (max 200 for payload size)
        sample_indices = set(
            sorted(random.sample(range(n_sims), min(200, n_sims)))
        )

        for sim in range(n_sims):
            a1 = _random_allocation(t1, fields)
            a2 = _random_allocation(t2, fields)

            wins_1 = sum(1 for x, y in zip(a1, a2) if x > y)
            wins_2 = sum(1 for x, y in zip(a1, a2) if y > x)

            for f in range(fields):
                if a1[f] > a2[f]:
                    battlefield_wins_p1[f] += 1

            if wins_1 > wins_2:
                p1_wins += 1
            elif wins_2 > wins_1:
                p2_wins += 1
            else:
                draws += 1

            if sim in sample_indices:
                round_data.append(RoundData(
                    round_num=sim + 1,
                    actions=[a1, a2],
                    payoffs=[float(wins_1), float(wins_2)],
                    state={
                        "p1_war_win": wins_1 > wins_2,
                        "margin": wins_1 - wins_2,
                    },
                ))

        bf_rates = [round(w / n_sims, 3) for w in battlefield_wins_p1]

        return SimulationResult(
            game_id="colonel_blotto",
            config=config,
            rounds=round_data,
            equilibria=[
                Equilibrium(
                    name="No Pure-Strategy NE",
                    strategies=["mixed (uniform Dirichlet)"],
                    description=(
                        "For symmetric Blotto, no pure-strategy equilibrium exists. "
                        "Optimal play randomizes across allocations."
                    ),
                )
            ],
            summary={
                "p1_win_rate": round(p1_wins / n_sims, 3),
                "p2_win_rate": round(p2_wins / n_sims, 3),
                "draw_rate": round(draws / n_sims, 3),
                "battlefield_win_rates_p1": bf_rates,
                "troops_ratio": round(t1 / t2, 2),
            },
            metadata={"compute_time_ms": round((time.time() - t0) * 1000, 2), "engine": "server"},
        )
