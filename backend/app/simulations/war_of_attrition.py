"""War of Attrition — escalation and timing game."""
from __future__ import annotations
import random, time
from app.models.schemas import GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium
from app.simulations.base import BaseGame

STRATEGIES = {
    "fixed_low": lambda _h, v, _c: max(1, int(v * 0.3)),
    "fixed_high": lambda _h, v, _c: max(1, int(v * 0.9)),
    "value_bid": lambda _h, v, _c: max(1, int(v)),
    "random": lambda _h, v, _c: max(1, int(random.uniform(0.1, 1.5) * v)),
    "escalate": lambda h, v, _c: max(1, int(v * 0.5 + len(h) * 2)),
    "mixed_optimal": lambda _h, v, c: max(1, int(random.expovariate(c / v) if c > 0 else v)),
}

class WarOfAttrition(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="war_of_attrition", name="War of Attrition", category="underrated", tier=2,
            short_description="Persist or quit? The escalation dilemma.",
            long_description="Two contestants compete for a prize by choosing how long to persist. Both pay costs proportional to the contest duration. The winner gets the prize minus costs. Demonstrates sunk cost escalation.",
            parameters=[
                ParameterSpec(name="simulations", type="int", default=500, min=10, max=5000, description="Number of contests"),
                ParameterSpec(name="prize_value", type="float", default=100.0, min=1, max=1000, description="Prize value"),
                ParameterSpec(name="cost_per_round", type="float", default=1.0, min=0.1, max=50, description="Cost per time unit"),
                ParameterSpec(name="strategy_p1", type="select", default="mixed_optimal", options=list(STRATEGIES), description="Player 1 strategy"),
                ParameterSpec(name="strategy_p2", type="select", default="escalate", options=list(STRATEGIES), description="Player 2 strategy"),
            ],
            available=True, engine="server", tags=["escalation", "timing"],
            theory_card="## Mixed-Strategy Equilibrium\nThe unique symmetric NE involves **randomized persistence times** drawn from an exponential distribution.\n\n## Sunk Cost Trap\nRational agents should ignore sunk costs, but the contest structure creates **escalation commitment** — a pattern seen in dollar auctions, patent races, and wars.\n\n## Key Insight\nThe expected profit in equilibrium is **zero** — all surplus is dissipated by competition costs.",
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        sims = config.get("simulations", 500)
        prize = config.get("prize_value", 100.0)
        cost = config.get("cost_per_round", 1.0)
        s1 = STRATEGIES.get(config.get("strategy_p1", "mixed_optimal"), STRATEGIES["random"])
        s2 = STRATEGIES.get(config.get("strategy_p2", "escalate"), STRATEGIES["random"])
        rd, history = [], []
        tot1 = tot2 = p1_wins = 0
        durations = []
        for sim in range(1, sims + 1):
            bid1 = s1(history, prize, cost)
            bid2 = s2(history, prize, cost)
            duration = min(bid1, bid2)
            if bid1 > bid2:
                pay1 = prize - duration * cost
                pay2 = -duration * cost
                p1_wins += 1
            elif bid2 > bid1:
                pay1 = -duration * cost
                pay2 = prize - duration * cost
            else:
                pay1 = prize / 2 - duration * cost
                pay2 = prize / 2 - duration * cost
            tot1 += pay1; tot2 += pay2
            durations.append(duration)
            history.append({"bid1": bid1, "bid2": bid2})
            rd.append(RoundData(round_num=sim, actions=[bid1, bid2], payoffs=[pay1, pay2],
                state={"duration": duration, "avg_duration": sum(durations)/sim, "p1_win_rate": p1_wins/sim}))
        return SimulationResult(game_id="war_of_attrition", config=config, rounds=rd,
            equilibria=[Equilibrium(name="Symmetric Mixed NE", strategies=["Exp(c/V)","Exp(c/V)"], payoffs=[0,0], description="Both randomize persistence time from exponential distribution; expected profit is zero.")],
            summary={"p1_win_rate": p1_wins/sims, "avg_duration": sum(durations)/sims, "avg_payoff_p1": tot1/sims, "avg_payoff_p2": tot2/sims, "total_cost_dissipated": sum(min(h["bid1"],h["bid2"])*cost for h in history)/sims},
            metadata={"compute_time_ms": round((time.time()-t0)*1000, 2), "engine": "server"})
