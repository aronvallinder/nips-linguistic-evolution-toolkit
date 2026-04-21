"""
Public Goods Game Implementation

N-player simultaneous contribution game for studying cooperation dynamics.
This removes the sequential asymmetry of the trust game.

Game mechanics:
- Each player receives an endowment each round
- All players simultaneously decide how much to contribute to a public pool
- The pool is multiplied by MPCR (marginal per capita return) and divided equally
- Payoff = endowment - contribution + (pool * MPCR / n_players)

Nash equilibrium: Contribute 0 (defect)
Social optimum: Contribute everything (cooperate)
"""

import re
from games.base_game import Game


class PublicGoodsGame(Game):
    """N-player public goods game with simultaneous contributions"""

    def __init__(self, endowment, mpcr, n_players=2,
                 system_prompt_template=None, contribution_prompt_template=None,
                 personas=None):
        """
        Initialize Public Goods Game.

        Args:
            endowment: Amount each player receives per round
            mpcr: Marginal Per Capita Return (multiplier for the pool, divided by n)
                  For cooperation to be beneficial: mpcr > 1
                  For defection to be individually rational: mpcr < n
            n_players: Number of players (default 2)
            system_prompt_template: System prompt explaining the game
            contribution_prompt_template: Per-round prompt for contributions
            personas: Dict mapping agent_id to persona config
        """
        super().__init__()
        self.endowment = endowment
        self.mpcr = mpcr
        self.n_players = n_players
        self.system_prompt_template = system_prompt_template
        self.contribution_prompt_template = contribution_prompt_template
        self.personas = personas or {}

        # Generate agent IDs
        self.agent_ids = [f"Agent_{i+1}" for i in range(n_players)]

    def get_move_order(self, turn, sim_data):
        """All players move simultaneously (return all agents)"""
        return self.agent_ids

    def get_system_prompt(self, agent_id, agent):
        """System prompt explaining the public goods game"""
        if self.system_prompt_template:
            base_prompt = self.system_prompt_template.format(
                endowment=self.endowment,
                mpcr=self.mpcr,
                n_players=self.n_players
            )
        else:
            base_prompt = f"""You are playing a Public Goods Game with {self.n_players} players.

GAME RULES:
- Each round, you receive ${self.endowment}
- You decide how much to CONTRIBUTE to a shared pool ($0-${self.endowment})
- All contributions are summed, multiplied by {self.mpcr}, then divided equally among all players
- Your payoff = ${self.endowment} - contribution + (pool share)

STRATEGY:
- Contributing more benefits the group but costs you individually
- If everyone contributes nothing, everyone gets ${self.endowment}
- If everyone contributes everything, everyone gets ${self.endowment * self.mpcr / self.n_players:.2f}

RESPONSE FORMAT: {{'contribute': <amount>}}
"""

        # Add persona if specified
        if agent_id in self.personas and self.personas[agent_id].get('system_addition'):
            base_prompt += f"\n\n{self.personas[agent_id]['system_addition']}"

        return base_prompt

    def get_game_prompt_round_1(self, agent_id, agent, turn):
        """First round prompt"""
        if self.contribution_prompt_template:
            return self.contribution_prompt_template.format(
                turn=1,
                endowment=self.endowment,
                n_players=self.n_players
            )
        return f"Round 1: You have ${self.endowment}. How much do you contribute to the public pool? (0-{self.endowment})"

    def get_game_prompt_later_round(self, agent_id, turn, sim_data, last_responses):
        """Later round prompt with history"""
        # Find last round data
        last_round = None
        for entry in reversed(sim_data.conversation_history):
            if entry.get('contributions') is not None:
                last_round = entry
                break

        if last_round is None:
            return self.get_game_prompt_round_1(agent_id, None, turn)

        # Build history summary
        contributions = last_round['contributions']
        total_pool = last_round['total_pool']
        pool_share = last_round['pool_share']
        my_contribution = contributions.get(agent_id, 0)
        my_payoff = last_round['payoffs'].get(agent_id, 0)

        others_contributions = [f"Player {aid}: ${c}" for aid, c in contributions.items() if aid != agent_id]
        others_str = ", ".join(others_contributions)

        prompt = f"""Round {turn}

Last round results:
- You contributed: ${my_contribution}
- Others contributed: {others_str}
- Total pool: ${total_pool:.2f}
- Pool was multiplied to ${total_pool * self.mpcr:.2f} and divided {self.n_players} ways
- Your share from pool: ${pool_share:.2f}
- Your payoff: ${my_payoff:.2f}
- Your total earnings: ${sim_data.game_data['balances'][agent_id]:.2f}

You have ${self.endowment} this round. How much do you contribute? (0-{self.endowment})"""

        return prompt

    def process_intermediate_response(self, agent_id, response, turn, sim_data):
        """Store contribution as it comes in (since moves are simultaneous, we wait for all)"""
        if "pending_contributions" not in sim_data.game_data:
            sim_data.game_data["pending_contributions"] = {}

        contribution = self._extract_amount(response, "contribute")
        contribution = max(0, min(contribution, self.endowment))  # Clamp to valid range
        sim_data.game_data["pending_contributions"][agent_id] = contribution

    def process_turn(self, turn, agent_responses, sim_data):
        """Process complete turn after all players have contributed"""
        # Initialize on first turn
        if "balances" not in sim_data.game_data:
            sim_data.game_data["balances"] = {aid: 0 for aid in self.agent_ids}
            sim_data.game_data["pending_contributions"] = {}

        # Extract all contributions
        contributions = {}
        for agent_id in self.agent_ids:
            if agent_id in agent_responses:
                contribution = self._extract_amount(agent_responses[agent_id], "contribute")
                contribution = max(0, min(contribution, self.endowment))
                contributions[agent_id] = contribution
            else:
                # Fallback to pending if available
                contributions[agent_id] = sim_data.game_data.get("pending_contributions", {}).get(agent_id, 0)

        # Calculate pool and payoffs
        total_pool = sum(contributions.values())
        multiplied_pool = total_pool * self.mpcr
        pool_share = multiplied_pool / self.n_players

        payoffs = {}
        for agent_id in self.agent_ids:
            payoffs[agent_id] = self.endowment - contributions[agent_id] + pool_share
            sim_data.game_data["balances"][agent_id] += payoffs[agent_id]

        # Clear pending contributions
        sim_data.game_data["pending_contributions"] = {}

        # Fill in the entry for this round
        for entry in sim_data.conversation_history:
            if entry["round"] == turn:
                entry["contributions"] = contributions
                entry["total_pool"] = total_pool
                entry["multiplied_pool"] = multiplied_pool
                entry["pool_share"] = pool_share
                entry["payoffs"] = payoffs
                entry["balances"] = dict(sim_data.game_data["balances"])
                entry["actions"] = {
                    aid: {"action": "contributed", "amount": contributions[aid]}
                    for aid in self.agent_ids
                }
                break

        return {aid: {"contributed": contributions[aid]} for aid in self.agent_ids}

    def _extract_amount(self, response_data, key):
        """Extract contribution amount from response"""
        if isinstance(response_data, str):
            content = response_data
        else:
            content = response_data.get("content", "")

        # Parse JSON format: {'contribute': 5} or {"contribute": 5}
        pattern = rf"'{key}':\s*(\d+\.?\d*)|" + rf'"{key}":\s*(\d+\.?\d*)'
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return float(match.group(1) or match.group(2))
        raise ValueError(f"Could not extract {key} from: {content[:200]}")

    def print_turn_summary(self, turn, agent_responses, sim_data):
        """Print round summary"""
        entry = sim_data.conversation_history[-1]

        print(f"\n{'*' * 80}")
        print(f"ROUND {turn} COMPLETE")

        contributions = entry['contributions']
        for aid in self.agent_ids:
            print(f"  {aid}: contributed ${contributions[aid]:.2f}, "
                  f"payoff ${entry['payoffs'][aid]:.2f}, "
                  f"total ${entry['balances'][aid]:.2f}")

        print(f"  Pool: ${entry['total_pool']:.2f} -> ${entry['multiplied_pool']:.2f} "
              f"(${entry['pool_share']:.2f} each)")
        print(f"{'*' * 80}")

    def print_game_summary(self, sim_data):
        """Final game summary"""
        total_rounds = max((entry.get("round", 0) for entry in sim_data.conversation_history), default=0)

        print("\n" + "=" * 80)
        print("PUBLIC GOODS GAME SUMMARY")
        print("=" * 80)

        # Filter for game rounds
        game_rounds = [r for r in sim_data.conversation_history if r.get("contributions") is not None]
        actual_game_rounds = len(game_rounds)

        if actual_game_rounds > 0:
            # Calculate averages per player
            for aid in self.agent_ids:
                avg_contribution = sum(r["contributions"][aid] for r in game_rounds) / actual_game_rounds
                avg_payoff = sum(r["payoffs"][aid] for r in game_rounds) / actual_game_rounds
                final_balance = sim_data.game_data["balances"][aid]
                print(f"\n{aid}:")
                print(f"  Avg contribution: ${avg_contribution:.2f}/{self.endowment}")
                print(f"  Avg payoff: ${avg_payoff:.2f}")
                print(f"  Final earnings: ${final_balance:.2f}")

            # Overall cooperation rate
            total_contributions = sum(
                r["contributions"][aid] for r in game_rounds for aid in self.agent_ids
            )
            max_possible = self.endowment * self.n_players * actual_game_rounds
            cooperation_rate = total_contributions / max_possible if max_possible > 0 else 0

            print(f"\nOverall:")
            print(f"  Total rounds: {total_rounds}")
            print(f"  Game rounds: {actual_game_rounds}")
            print(f"  Cooperation rate: {cooperation_rate:.1%}")
            print(f"  Avg pool per round: ${sum(r['total_pool'] for r in game_rounds) / actual_game_rounds:.2f}")
