"""Multi-Agent Negotiation — multi-item bargaining with private valuations."""
from __future__ import annotations
import random, time
from app.models.schemas import GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium
from app.simulations.base import BaseGame


class MultiAgentNegotiation(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="multi_agent_negotiation", name="Multi-Agent Negotiation", category="innovation", tier=3,
            short_description="Multi-item negotiation with private valuations.",
            long_description="Multiple agents negotiate over multiple items. Each agent has private valuations. Agents make and respond to offers. Explores efficiency, fairness, and strategic revelation of preferences.",
            parameters=[
                ParameterSpec(name="rounds", type="int", default=50, min=5, max=500, description="Negotiation rounds"),
                ParameterSpec(name="n_agents", type="int", default=4, min=2, max=10, description="Number of negotiating agents"),
                ParameterSpec(name="n_items", type="int", default=5, min=2, max=20, description="Number of items to allocate"),
                ParameterSpec(name="patience", type="float", default=0.95, min=0.5, max=1.0, description="Discount factor (patience level)"),
                ParameterSpec(name="strategy", type="select", default="concession", options=["greedy", "concession", "fair", "random", "tit_for_tat"], description="Negotiation strategy"),
            ],
            available=True, engine="server", tags=["negotiation", "mechanism-design"],
            theory_card="## Multi-Issue Bargaining\nWith multiple items and different valuations, **logrolling** (trading concessions across items) can make everyone better off.\n\n## Rubinstein Bargaining\nWith discounting, the patient player gets a larger share. The equilibrium split depends on the **ratio of discount factors**.\n\n## Key Insight\nEfficiency requires **preference revelation**, but agents have incentives to misrepresent. Mechanism design addresses this tension.",
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        rounds = config.get("rounds", 50)
        n_agents = config.get("n_agents", 4)
        n_items = config.get("n_items", 5)
        patience = config.get("patience", 0.95)
        strategy = config.get("strategy", "concession")

        # Generate private valuations
        valuations = [[random.uniform(1, 20) for _ in range(n_items)] for _ in range(n_agents)]

        # Track allocation: which agent gets which item (-1 = unallocated)
        allocation = [-1] * n_items
        rd = []
        offers_made = 0
        agreements = 0

        for r in range(1, rounds + 1):
            discount = patience ** r
            # Each round: a random proposer makes an offer
            proposer = (r - 1) % n_agents
            # Proposer decides which unallocated items to claim
            unallocated = [i for i in range(n_items) if allocation[i] == -1]
            if not unallocated:
                # All allocated — renegotiate
                rd.append(RoundData(round_num=r, actions=["all_allocated"], payoffs=[0] * n_agents,
                    state={"allocated": n_items - len(unallocated), "total_items": n_items,
                           "efficiency": _efficiency(allocation, valuations, n_agents, n_items),
                           "agreements": agreements}))
                continue

            # Propose: claim most valued unallocated items
            if strategy == "greedy":
                desired = sorted(unallocated, key=lambda i: -valuations[proposer][i])[:max(1, len(unallocated) // 2)]
            elif strategy == "concession":
                # Start greedy, concede over time
                claim_frac = max(0.2, 1.0 - r / rounds * 0.8)
                n_claim = max(1, int(len(unallocated) * claim_frac / n_agents))
                desired = sorted(unallocated, key=lambda i: -valuations[proposer][i])[:n_claim]
            elif strategy == "fair":
                n_claim = max(1, len(unallocated) // n_agents)
                desired = sorted(unallocated, key=lambda i: -valuations[proposer][i])[:n_claim]
            elif strategy == "tit_for_tat":
                n_claim = max(1, len(unallocated) // n_agents)
                desired = sorted(unallocated, key=lambda i: -valuations[proposer][i])[:n_claim]
            else:
                desired = random.sample(unallocated, max(1, random.randint(1, len(unallocated))))

            offers_made += 1

            # Other agents vote: accept if they don't value items too highly
            accept_votes = 0
            for agent in range(n_agents):
                if agent == proposer:
                    continue
                # Agent accepts if their best unallocated item isn't in the proposal
                agent_top = max(unallocated, key=lambda i: valuations[agent][i])
                if agent_top not in desired:
                    accept_votes += 1
                elif random.random() < discount * 0.3:
                    accept_votes += 1  # Reluctant acceptance due to time pressure

            # Majority acceptance
            if accept_votes >= (n_agents - 1) / 2:
                for item in desired:
                    allocation[item] = proposer
                agreements += 1

            allocated_count = sum(1 for a in allocation if a >= 0)
            rd.append(RoundData(round_num=r, actions=[proposer, len(desired), accept_votes],
                payoffs=[round(_agent_value(allocation, valuations, a, n_items) * discount, 2) for a in range(n_agents)],
                state={"proposer": proposer, "items_claimed": len(desired), "accepted": accept_votes >= (n_agents - 1) / 2,
                       "allocated_ratio": allocated_count / n_items,
                       "efficiency": round(_efficiency(allocation, valuations, n_agents, n_items), 3),
                       "agreements": agreements}))

        # Final payoffs
        final_payoffs = [round(_agent_value(allocation, valuations, a, n_items), 2) for a in range(n_agents)]
        max_possible = sum(max(valuations[a][i] for a in range(n_agents)) for i in range(n_items))

        return SimulationResult(game_id="multi_agent_negotiation", config=config, rounds=rd,
            equilibria=[Equilibrium(name="Efficient Allocation", strategies=["Optimal assignment"],
                payoffs=[], description=f"Maximum total value = {max_possible:.1f} (assign each item to highest-valuation agent)")],
            summary={"efficiency": round(_efficiency(allocation, valuations, n_agents, n_items), 3),
                     "items_allocated": sum(1 for a in allocation if a >= 0),
                     "total_value_captured": sum(final_payoffs),
                     "max_possible_value": round(max_possible, 1),
                     "agreements_reached": agreements,
                     "avg_payoff": round(sum(final_payoffs) / n_agents, 2)},
            metadata={"compute_time_ms": round((time.time() - t0) * 1000, 2), "engine": "server"})


def _agent_value(allocation, valuations, agent, n_items):
    return sum(valuations[agent][i] for i in range(n_items) if allocation[i] == agent)


def _efficiency(allocation, valuations, n_agents, n_items):
    actual = sum(valuations[allocation[i]][i] for i in range(n_items) if allocation[i] >= 0)
    optimal = sum(max(valuations[a][i] for a in range(n_agents)) for i in range(n_items))
    return actual / optimal if optimal > 0 else 0
