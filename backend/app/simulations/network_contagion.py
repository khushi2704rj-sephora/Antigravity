"""Network Contagion — strategy/behavior spread on configurable graph topologies."""
from __future__ import annotations
import random
import time
from app.models.schemas import (
    GameInfo, ParameterSpec, SimulationResult, RoundData, Equilibrium,
)
from app.simulations.base import BaseGame


def _generate_graph(n: int, topology: str) -> dict[int, list[int]]:
    """Generate an adjacency list for the given topology."""
    adj: dict[int, list[int]] = {i: [] for i in range(n)}

    if topology == "random_erdos_renyi":
        p = min(1.0, 6.0 / n)  # average degree ~6
        for i in range(n):
            for j in range(i + 1, n):
                if random.random() < p:
                    adj[i].append(j)
                    adj[j].append(i)
    elif topology == "small_world":
        # Watts-Strogatz: ring lattice with k=4, rewire p=0.1
        k = 4
        for i in range(n):
            for j in range(1, k // 2 + 1):
                neighbor = (i + j) % n
                adj[i].append(neighbor)
                adj[neighbor].append(i)
        # Rewire
        for i in range(n):
            for idx in range(len(adj[i])):
                if random.random() < 0.1:
                    new_target = random.randint(0, n - 1)
                    if new_target != i and new_target not in adj[i]:
                        old = adj[i][idx]
                        adj[i][idx] = new_target
                        if i in adj[old]:
                            adj[old].remove(i)
                        adj[new_target].append(i)
    elif topology == "scale_free":
        # Barabási-Albert: start with m0=3 fully connected, attach m=2 per step
        m = 2
        for i in range(min(3, n)):
            for j in range(i + 1, min(3, n)):
                adj[i].append(j)
                adj[j].append(i)
        degree_sum = [len(adj[i]) for i in range(n)]
        for i in range(3, n):
            targets: set[int] = set()
            total_deg = sum(degree_sum[:i]) or 1
            while len(targets) < min(m, i):
                r = random.random() * total_deg
                cumulative = 0
                for j in range(i):
                    cumulative += degree_sum[j]
                    if cumulative >= r:
                        targets.add(j)
                        break
            for t in targets:
                adj[i].append(t)
                adj[t].append(i)
                degree_sum[i] += 1
                degree_sum[t] += 1
    else:  # grid
        side = int(n ** 0.5)
        for i in range(n):
            r, c = divmod(i, side)
            if c + 1 < side:
                adj[i].append(i + 1)
                adj[i + 1].append(i)
            if r + 1 < side and i + side < n:
                adj[i].append(i + side)
                adj[i + side].append(i)

    # Deduplicate
    for k_ in adj:
        adj[k_] = list(set(adj[k_]))
    return adj


class NetworkContagion(BaseGame):
    def info(self) -> GameInfo:
        return GameInfo(
            id="network_contagion",
            name="Network Contagion",
            category="innovation",
            tier=3,
            short_description="Watch strategies spread through a network like wildfire.",
            long_description=(
                "Place agents on a configurable network topology (random, small-world, "
                "scale-free, or grid). Each agent plays a 2×2 coordination game with its "
                "neighbors and adopts the strategy that would have earned the highest payoff. "
                "Observe how tipping points, cascades, and stable coexistence emerge from "
                "local interactions on global structures."
            ),
            parameters=[
                ParameterSpec(name="n_nodes", type="int", default=100, min=20, max=500,
                              description="Number of agents in the network"),
                ParameterSpec(name="topology", type="select", default="small_world",
                              options=["random_erdos_renyi", "small_world", "scale_free", "grid"],
                              description="Network topology"),
                ParameterSpec(name="initial_adopters", type="float", default=0.1, min=0.01, max=0.5,
                              description="Fraction of initial adopters (strategy B)"),
                ParameterSpec(name="rounds", type="int", default=50, min=10, max=200,
                              description="Number of update rounds"),
                ParameterSpec(name="payoff_AA", type="float", default=3.0, min=0, max=10,
                              description="Payoff when both play A (incumbent)"),
                ParameterSpec(name="payoff_BB", type="float", default=4.0, min=0, max=10,
                              description="Payoff when both play B (innovation)"),
                ParameterSpec(name="payoff_AB", type="float", default=0.0, min=0, max=10,
                              description="Payoff when A meets B"),
            ],
            available=True,
            engine="server",
            tags=["network", "contagion", "cascade", "topology", "innovation"],
            theory_card=(
                "## Network Effects in Game Theory\n"
                "Morris (2000) showed that in network coordination games, adoption cascades "
                "depend on a critical threshold q = (payoff_AA - payoff_AB) / "
                "(payoff_AA - payoff_AB + payoff_BB - payoff_AB).\n\n"
                "## Tipping Points\n"
                "When the fraction of B-adopters crosses ~q in a node's neighborhood, "
                "switching to B becomes rational — triggering a cascade.\n\n"
                "## Topology Matters\n"
                "- **Scale-free**: hubs accelerate or block cascades\n"
                "- **Small-world**: short paths enable rapid diffusion\n"
                "- **Grid**: slow, wave-like propagation"
            ),
        )

    def compute(self, config: dict) -> SimulationResult:
        t0 = time.time()
        n = config.get("n_nodes", 100)
        topology = config.get("topology", "small_world")
        init_frac = config.get("initial_adopters", 0.1)
        rounds = config.get("rounds", 50)
        pAA = config.get("payoff_AA", 3.0)
        pBB = config.get("payoff_BB", 4.0)
        pAB = config.get("payoff_AB", 0.0)

        adj = _generate_graph(n, topology)

        # Initialize strategies: 0 = A (incumbent), 1 = B (innovation)
        strategies = [0] * n
        adopters = random.sample(range(n), max(1, int(n * init_frac)))
        for a in adopters:
            strategies[a] = 1

        round_data: list[RoundData] = []
        edges = []
        for node, neighbors in adj.items():
            for nb in neighbors:
                if node < nb:
                    edges.append([node, nb])

        for r in range(1, rounds + 1):
            new_strategies = list(strategies)
            switches = 0

            for node in range(n):
                neighbors = adj[node]
                if not neighbors:
                    continue
                # Count neighbor strategies
                n_A = sum(1 for nb in neighbors if strategies[nb] == 0)
                n_B = sum(1 for nb in neighbors if strategies[nb] == 1)

                # Expected payoff of each strategy
                payoff_if_A = n_A * pAA + n_B * pAB
                payoff_if_B = n_A * pAB + n_B * pBB

                best = 0 if payoff_if_A >= payoff_if_B else 1
                if best != strategies[node]:
                    switches += 1
                new_strategies[node] = best

            strategies = new_strategies
            adoption_rate = sum(strategies) / n

            round_data.append(RoundData(
                round_num=r,
                actions=list(strategies),
                payoffs=[0.0],  # aggregate
                state={
                    "adoption_rate": round(adoption_rate, 4),
                    "switches": switches,
                    "node_strategies": list(strategies),
                },
            ))

            # Early termination if stable
            if switches == 0 and r > 3:
                break

        # Compute edges for frontend network graph (only once)
        final_adoption = sum(strategies) / n

        # Threshold prediction
        denom = (pAA - pAB + pBB - pAB)
        threshold = (pAA - pAB) / denom if denom != 0 else 0.5

        return SimulationResult(
            game_id="network_contagion",
            config=config,
            rounds=round_data,
            equilibria=[
                Equilibrium(
                    name="Contagion Threshold",
                    strategies=[f"q = {threshold:.3f}"],
                    description=(
                        f"Cascade occurs when neighborhood adoption > {threshold:.1%}. "
                        f"Final adoption: {final_adoption:.1%}."
                    ),
                )
            ],
            summary={
                "final_adoption_rate": round(final_adoption, 4),
                "cascade_occurred": final_adoption > 0.5,
                "rounds_to_stable": len(round_data),
                "predicted_threshold": round(threshold, 4),
                "topology": topology,
                "network": {"nodes": n, "edges": edges},
            },
            metadata={"compute_time_ms": round((time.time() - t0) * 1000, 2), "engine": "server"},
        )
