"""
Trust Game with Noise and Asymmetric Naming Support

This module extends the standard trust game with:
1. Amount noise: Distort communicated amounts vs actual amounts
2. Asymmetric naming: The OTHER player's role is presented with a mythological name

Noise types:
- uniform: Add random noise from uniform distribution
- probabilistic: With probability p, replace amount with random/zero/max value
- decay: Information becomes less accurate over time (future extension)

Asymmetric naming:
- YOUR role stays generic ("You are the INVESTOR")
- The OTHER player's role can be mythological ("Prometheus sent you $3...")
"""

import random
import re
from games.base_game import Game


# ============================================================================
# OTHER PLAYER NAMES - Mythological names for the OTHER player
# ============================================================================

OTHER_PLAYER_NAMES = {
    "default": {"investor": "The investor", "trustee": "the trustee"},
    "prosocial": {"investor": "Prometheus", "trustee": "Orpheus"},
    "trickster": {"investor": "Coyote", "trustee": "Anansi"},
    "exchange": {"investor": "Persephone", "trustee": "Yggdrasil"},
    "neutral_myth": {"investor": "The Wanderer", "trustee": "The Guardian"},
}


# ============================================================================
# TRUST GAME WITH NOISE IMPLEMENTATION
# ============================================================================

class TrustGameNoisy(Game):
    """Trust/Investment game with noise and asymmetric naming support"""

    def __init__(self, endowment, multiplier, system_prompt_template=None, personas=None,
                 round1_investor_template=None, round1_trustee_template=None,
                 later_investor_template=None, later_trustee_template=None,
                 noise_config=None, other_player_names="default"):
        """
        Initialize Trust Game with noise support.

        Args:
            endowment: Starting amount for investor each round
            multiplier: Multiplier applied to sent amount
            system_prompt_template: System prompt template string
            personas: Dict mapping agent_id to persona config
            round1_investor_template: Template for first round investor prompt
            round1_trustee_template: Template for first round trustee prompt
            later_investor_template: Template for later round investor prompt
            later_trustee_template: Template for later round trustee prompt
            noise_config: Dict with noise configuration:
                {
                    "type": "uniform" | "probabilistic" | "decay",
                    "range": float,           # for uniform: +/- range
                    "probability": float,     # for probabilistic: chance of noise
                    "replacement": str,       # for probabilistic: "random" | "zero" | "max"
                    "applies_to": str,        # "sent" | "returned" | "both"
                    "inform_agents": bool     # whether to tell agents about noise
                }
            other_player_names: Key from OTHER_PLAYER_NAMES dict for asymmetric naming
        """
        super().__init__()
        self.endowment = endowment
        self.multiplier = multiplier
        self.system_prompt_template = system_prompt_template
        self.round1_investor_template = round1_investor_template
        self.round1_trustee_template = round1_trustee_template
        self.later_investor_template = later_investor_template
        self.later_trustee_template = later_trustee_template
        self.personas = personas or {}

        # Noise configuration
        self.noise_config = noise_config or {}

        # Asymmetric naming: get name set for the OTHER player
        if isinstance(other_player_names, str):
            self.other_player_names = OTHER_PLAYER_NAMES.get(
                other_player_names, OTHER_PLAYER_NAMES["default"]
            )
        else:
            # Allow passing a custom dict directly
            self.other_player_names = other_player_names

        # Agent IDs (fixed)
        self.agent_1_id = "Agent_1"
        self.agent_2_id = "Agent_2"

    def _apply_noise(self, actual_amount, max_amount):
        """
        Apply noise to an amount based on config.

        Args:
            actual_amount: The true amount
            max_amount: Maximum valid amount (for clamping)

        Returns:
            tuple: (communicated_amount, actual_amount)
        """
        if not self.noise_config:
            return actual_amount, actual_amount

        noise_type = self.noise_config.get("type", "none")

        if noise_type == "uniform":
            noise_range = self.noise_config.get("range", 0)
            direction = self.noise_config.get("direction", "both")
            if direction == "negative":
                noise = random.uniform(-noise_range, 0)
            elif direction == "positive":
                noise = random.uniform(0, noise_range)
            else:
                noise = random.uniform(-noise_range, noise_range)
            communicated = actual_amount + noise
            communicated = max(0, min(communicated, max_amount))

        elif noise_type == "probabilistic":
            prob = self.noise_config.get("probability", 0)
            if random.random() < prob:
                replacement = self.noise_config.get("replacement", "random")
                if replacement == "random":
                    communicated = random.uniform(0, max_amount)
                elif replacement == "zero":
                    communicated = 0
                elif replacement == "max":
                    communicated = max_amount
                else:
                    communicated = actual_amount
            else:
                communicated = actual_amount

        elif noise_type == "decay":
            # Future extension: decay based on rounds_ago
            # For now, treat as no noise
            communicated = actual_amount

        else:
            communicated = actual_amount

        return round(communicated, 2), actual_amount

    def _should_apply_noise_to(self, action_type):
        """Check if noise should be applied to this action type."""
        applies_to = self.noise_config.get("applies_to", "sent")
        if applies_to == "both":
            return True
        return applies_to == action_type

    def get_roles_for_round(self, turn):
        """Determine role assignments for this round (roles swap each round)"""
        if turn % 2 == 1:  # Odd rounds
            return {
                "investor": self.agent_1_id,
                "trustee": self.agent_2_id
            }
        else:  # Even rounds
            return {
                "investor": self.agent_2_id,
                "trustee": self.agent_1_id
            }

    def get_move_order(self, turn, sim_data):
        """Define who moves in what order this turn (investor first, then trustee)"""
        roles = self.get_roles_for_round(turn)
        return [roles["investor"], roles["trustee"]]

    def get_system_prompt(self, agent_id, agent):
        """Role-agnostic system prompt that covers both roles"""
        if not self.system_prompt_template:
            raise ValueError(
                "No prompt provided. Provide prompt in config/experiments.yaml under "
                "prompt_templates, named 'trust_game_default' (or your custom template name)"
            )

        base_prompt = self.system_prompt_template.format(
            endowment=self.endowment,
            multiplier=self.multiplier
        )

        # Add persona if specified for this agent
        if agent_id in self.personas and self.personas[agent_id].get('system_addition'):
            base_prompt += f"\n\n{self.personas[agent_id]['system_addition']}"

        # Optionally inform agents about noise
        if self.noise_config.get("inform_agents", False):
            noise_info = """

NOTE: There may be communication noise in this game.
The amounts you see may differ slightly from what was actually sent/returned.
This is part of the experimental design."""
            base_prompt += noise_info

        return base_prompt

    def get_game_prompt_round_1(self, agent_id, agent, turn):
        """First turn"""
        roles = self.get_roles_for_round(turn)

        if agent_id == roles["investor"]:
            if not self.round1_investor_template:
                raise ValueError(
                    "No prompt provided. Provide prompt in noise/experiments_noisy.yaml under "
                    "prompt_templates, named 'trust_game_round1_investor'"
                )
            return self.round1_investor_template.format(
                endowment=self.endowment
            )
        else:
            # Trustee gets prompted after investor, will have pending_sent available
            sent_actual = self.sim_data_ref.game_data.get("pending_sent")
            if sent_actual is None:
                raise ValueError("pending_sent not found in game_data. Investor should have responded first.")

            # Apply noise to sent amount if configured
            if self._should_apply_noise_to("sent"):
                sent_communicated, _ = self._apply_noise(sent_actual, self.endowment)
            else:
                sent_communicated = sent_actual

            # Store communicated amount for later reference
            self.sim_data_ref.game_data["pending_sent_communicated"] = sent_communicated

            # Trustee sees received consistent with communicated sent
            received = sent_communicated * self.multiplier
            percentage = (sent_communicated / self.endowment * 100)

            # Get asymmetric name for the investor (the OTHER player from trustee's perspective)
            investor_display_name = self.other_player_names["investor"]

            if not self.round1_trustee_template:
                raise ValueError(
                    "No prompt provided. Provide prompt in noise/experiments_noisy.yaml under "
                    "prompt_templates, named 'trust_game_round1_trustee'"
                )

            # Format with investor_name for asymmetric naming
            template = self.round1_trustee_template

            # Check if template uses {investor_name} placeholder
            if "{investor_name}" in template:
                return template.format(
                    sent=sent_communicated,
                    percentage=percentage,
                    received=received,
                    investor_name=investor_display_name
                )
            else:
                # Fallback to standard template
                return template.format(
                    sent=sent_communicated,
                    percentage=percentage,
                    received=received
                )

    def get_game_prompt_later_round(self, agent_id, turn, sim_data, last_responses):
        """Subsequent turns with noise and asymmetric naming"""
        roles = self.get_roles_for_round(turn)

        # Find the last round that contains actual game data (sent is not None)
        last_round = None
        for entry in reversed(sim_data.conversation_history):
            if entry.get('sent') is not None:
                last_round = entry
                break

        if last_round is None:
            # No previous game data found, treat as first round
            return self.get_game_prompt_round_1(agent_id, None, turn)

        # Current round: pending_sent from this turn's investor
        sent_actual = sim_data.game_data["pending_sent"]

        # Apply noise to current sent amount for trustee prompt
        if self._should_apply_noise_to("sent"):
            sent_communicated, _ = self._apply_noise(sent_actual, self.endowment)
        else:
            sent_communicated = sent_actual

        sim_data.game_data["pending_sent_communicated"] = sent_communicated
        # Trustee sees received consistent with communicated sent
        received = sent_communicated * self.multiplier

        # Use communicated balance if available, fall back to actual
        if "balances_communicated" in sim_data.game_data:
            agent_balance = sim_data.game_data["balances_communicated"][agent_id]
        else:
            agent_balance = sim_data.game_data["balances"][agent_id]

        # Get asymmetric names
        investor_display_name = self.other_player_names["investor"]
        trustee_display_name = self.other_player_names["trustee"]

        # Asymmetric perspective: agents see correct info about their OWN
        # actions but noised info about the OTHER agent's intentions.
        # Current INVESTOR was TRUSTEE last round:
        #   - "investor sent $X" → NOISED (don't know what investor intended)
        #   - "you received $Y" → ACTUAL (know what they got)
        #   - "you returned $Z" → ACTUAL (know what they chose)
        # Current TRUSTEE was INVESTOR last round:
        #   - "you sent $X" → ACTUAL (know what they chose)
        #   - "tripled to $Y" → ACTUAL (sent × multiplier)
        #   - "trustee returned $Z" → NOISED (don't know what trustee intended)

        if agent_id == roles["investor"]:
            # I was TRUSTEE last round:
            # - I don't know what investor intended to send → noised
            # - received derived from noised sent for consistency
            # - I know what I returned → actual (own action)
            lr_sent = last_round.get('sent_communicated', last_round['sent'])
            lr_received = lr_sent * self.multiplier  # consistent with noised sent
            lr_returned = last_round['returned']  # my own action
            lr_sent_pct = (lr_sent / self.endowment * 100)
            # Payoff consistent with communicated values
            lr_trustee_payoff = lr_received - lr_returned

            if not self.later_investor_template:
                raise ValueError(
                    "No prompt provided. Provide prompt in noise/experiments_noisy.yaml under "
                    "prompt_templates, named 'trust_game_later_investor'"
                )
            return self.later_investor_template.format(
                turn=turn,
                last_round_sent=lr_sent,
                last_round_sent_percentage=lr_sent_pct,
                last_round_received=lr_received,
                last_round_returned=lr_returned,
                last_round_trustee_payoff=lr_trustee_payoff,
                agent_balance=agent_balance,
                endowment=self.endowment,
                investor_name=investor_display_name,
                trustee_name=trustee_display_name
            )
        else:
            # I was INVESTOR last round:
            # - I know what I sent → actual (own action)
            # - I know what was tripled → actual (derived from own sent)
            # - I don't know what trustee intended to return → noised
            lr_sent = last_round['sent']  # my own action
            lr_received = last_round['sent'] * self.multiplier  # actual (from own action)
            lr_returned = last_round.get('returned_communicated', last_round['returned'])
            lr_sent_pct = (lr_sent / self.endowment * 100)
            # Payoff consistent with communicated return
            lr_investor_payoff = self.endowment - lr_sent + lr_returned

            if not self.later_trustee_template:
                raise ValueError(
                    "No prompt provided. Provide prompt in noise/experiments_noisy.yaml under "
                    "prompt_templates, named 'trust_game_later_trustee'"
                )
            return self.later_trustee_template.format(
                turn=turn,
                last_round_sent=lr_sent,
                last_round_sent_percentage=lr_sent_pct,
                last_round_received=lr_received,
                last_round_returned=lr_returned,
                last_round_investor_payoff=lr_investor_payoff,
                agent_balance=agent_balance,
                received=received,
                investor_name=investor_display_name,
                trustee_name=trustee_display_name
            )

    def process_intermediate_response(self, agent_id, response, turn, sim_data):
        """Called after investor responds, before trustee"""
        roles = self.get_roles_for_round(turn)
        if agent_id == roles["investor"]:
            sent_amount = self._extract_amount(response, "send")
            sim_data.game_data["pending_sent"] = sent_amount
            # Store reference for get_round_1_prompt to use
            self.sim_data_ref = sim_data

    def process_turn(self, turn, agent_responses, sim_data):
        """Process complete turn (both moves done) with noise tracking"""
        # Initialize on first turn (don't overwrite pending values set during prompt generation)
        if "balances" not in sim_data.game_data:
            sim_data.game_data["balances"] = {self.agent_1_id: 0, self.agent_2_id: 0}
            sim_data.game_data.setdefault("pending_sent", 0)
            sim_data.game_data.setdefault("pending_sent_communicated", 0)
            self.sim_data_ref = sim_data

        # Get roles for this round
        roles = self.get_roles_for_round(turn)
        investor_id = roles["investor"]
        trustee_id = roles["trustee"]

        # Extract actual amounts from responses
        sent_actual = self._extract_amount(agent_responses[investor_id], "send")
        returned_actual = self._extract_amount(agent_responses[trustee_id], "return")

        # Get communicated sent amount (already stored during prompt generation)
        sent_communicated = sim_data.game_data.get("pending_sent_communicated", sent_actual)

        # Apply noise to returned amount if configured
        received_actual = sent_actual * self.multiplier
        if self._should_apply_noise_to("returned"):
            returned_communicated, _ = self._apply_noise(returned_actual, received_actual)
        else:
            returned_communicated = returned_actual

        # Calculate payoffs using ACTUAL amounts (not communicated)
        investor_payoff = (self.endowment - sent_actual) + returned_actual
        trustee_payoff = received_actual - returned_actual

        # Calculate communicated payoffs (what agents are told)
        received_communicated = sent_communicated * self.multiplier
        investor_payoff_communicated = (self.endowment - sent_actual) + returned_communicated
        trustee_payoff_communicated = received_communicated - returned_actual

        # Update balances with actual payoffs
        sim_data.game_data["balances"][investor_id] += investor_payoff
        sim_data.game_data["balances"][trustee_id] += trustee_payoff

        # Update communicated balances (what agents see)
        if "balances_communicated" not in sim_data.game_data:
            sim_data.game_data["balances_communicated"] = {self.agent_1_id: 0, self.agent_2_id: 0}
        sim_data.game_data["balances_communicated"][investor_id] += investor_payoff_communicated
        sim_data.game_data["balances_communicated"][trustee_id] += trustee_payoff_communicated

        # Track noise statistics
        if "noise_stats" not in sim_data.game_data:
            sim_data.game_data["noise_stats"] = {
                "rounds_with_noise": 0,
                "total_sent_noise": 0,
                "total_returned_noise": 0
            }

        noise_applied = (sent_communicated != sent_actual or returned_communicated != returned_actual)
        if noise_applied:
            sim_data.game_data["noise_stats"]["rounds_with_noise"] += 1
            sim_data.game_data["noise_stats"]["total_sent_noise"] += abs(sent_communicated - sent_actual)
            sim_data.game_data["noise_stats"]["total_returned_noise"] += abs(returned_communicated - returned_actual)

        # Fill in the pre-created entry for this round with game data
        for entry in sim_data.conversation_history:
            if entry["round"] == turn:
                # Store both actual and communicated amounts
                entry["sent"] = sent_actual
                entry["sent_communicated"] = sent_communicated
                entry["received"] = received_actual
                entry["received_communicated"] = sent_communicated * self.multiplier
                entry["returned"] = returned_actual
                entry["returned_communicated"] = returned_communicated
                entry["investor_payoff"] = investor_payoff
                entry["trustee_payoff"] = trustee_payoff
                entry["balances"] = dict(sim_data.game_data["balances"])
                entry["balances_communicated"] = dict(sim_data.game_data["balances_communicated"])
                entry["noise_applied"] = noise_applied
                entry["other_player_names"] = self.other_player_names
                entry["actions"] = {
                    investor_id: {"action": "sent", "amount": sent_actual, "communicated": sent_communicated},
                    trustee_id: {"action": "returned", "amount": returned_actual, "communicated": returned_communicated}
                }
                break

        return {
            investor_id: {"sent": sent_actual, "sent_communicated": sent_communicated},
            trustee_id: {"returned": returned_actual, "returned_communicated": returned_communicated}
        }

    def _extract_amount(self, response_data, key):
        """Extract number from JSON response in structured response data"""
        # Handle both old string format and new dict format for backward compatibility
        if isinstance(response_data, str):
            content = response_data
        else:
            content = response_data.get("content", "")

        # Parse JSON format: {'send': 5} or {"send": 5}
        pattern = rf"'{key}':\s*(\d+\.?\d*)|" + rf'"{key}":\s*(\d+\.?\d*)'
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return float(match.group(1) or match.group(2))
        raise ValueError(f"Could not extract {key} from: {content[:200]}")

    def print_turn_summary(self, turn, agent_responses, sim_data):
        """Print round summary with noise information"""
        entry = sim_data.conversation_history[-1]
        roles = entry["roles"]

        # Determine which agent had which role
        investor_id = [aid for aid, role in roles.items() if role == "investor"][0]
        trustee_id = [aid for aid, role in roles.items() if role == "trustee"][0]

        print(f"\n{'*' * 80}")
        print(f"ROUND {turn} COMPLETE")
        print(f"  Roles: {investor_id} = Investor, {trustee_id} = Trustee")
        print(f"  Sent: ${entry['sent']} → Received: ${entry['received']} → Returned: ${entry['returned']}")

        # Show noise if applied
        if entry.get('noise_applied'):
            print(f"  [NOISE] Communicated: sent=${entry['sent_communicated']:.2f}, "
                  f"returned=${entry['returned_communicated']:.2f}")

        # Show asymmetric naming if non-default
        if self.other_player_names != OTHER_PLAYER_NAMES["default"]:
            print(f"  [FRAMING] Other player names: {self.other_player_names}")

        print(f"  Payoffs: {investor_id} ${entry['investor_payoff']}, {trustee_id} ${entry['trustee_payoff']}")
        print(f"  Cumulative: {self.agent_1_id} ${entry['balances'][self.agent_1_id]}, "
              f"{self.agent_2_id} ${entry['balances'][self.agent_2_id]}")
        print(f"{'*' * 80}")

    def print_game_summary(self, sim_data):
        """Final summary with noise statistics"""
        # Calculate total simulation rounds from the highest round number
        total_rounds = max((entry.get("round", 0) for entry in sim_data.conversation_history), default=0)

        print("\n" + "=" * 80)
        print("GAME SUMMARY (NOISY)")
        print("=" * 80)

        # Filter for entries that contain actual game data (sent is not None)
        game_rounds = [r for r in sim_data.conversation_history if r.get("sent") is not None]

        total_sent = sum(r["sent"] for r in game_rounds)
        total_returned = sum(r["returned"] for r in game_rounds)
        actual_game_rounds = len(game_rounds)
        avg_sent = total_sent / actual_game_rounds if actual_game_rounds > 0 else 0
        avg_returned = total_returned / actual_game_rounds if actual_game_rounds > 0 else 0

        print(f"\nTotal rounds: {total_rounds}")
        print(f"Game rounds played: {actual_game_rounds}")
        print(f"Avg sent: ${avg_sent:.2f}/{self.endowment}")
        print(f"Avg returned: ${avg_returned:.2f}")
        print(f"Final earnings: {self.agent_1_id} ${sim_data.game_data['balances'][self.agent_1_id]}, "
              f"{self.agent_2_id} ${sim_data.game_data['balances'][self.agent_2_id]}")

        # Noise statistics
        noise_stats = sim_data.game_data.get("noise_stats", {})
        if noise_stats.get("rounds_with_noise", 0) > 0:
            print(f"\n--- Noise Statistics ---")
            print(f"  Rounds with noise: {noise_stats['rounds_with_noise']}/{actual_game_rounds}")
            print(f"  Total sent noise: ${noise_stats['total_sent_noise']:.2f}")
            print(f"  Total returned noise: ${noise_stats['total_returned_noise']:.2f}")

        # Asymmetric naming info
        if self.other_player_names != OTHER_PLAYER_NAMES["default"]:
            print(f"\n--- Asymmetric Naming ---")
            print(f"  Investor shown as: {self.other_player_names['investor']}")
            print(f"  Trustee shown as: {self.other_player_names['trustee']}")

        # Show role distribution
        agent_1_investor_rounds = sum(1 for r in game_rounds if "roles" in r and r["roles"][self.agent_1_id] == "investor")
        agent_2_investor_rounds = sum(1 for r in game_rounds if "roles" in r and r["roles"][self.agent_2_id] == "investor")
        print(f"\nRole distribution:")
        print(f"  {self.agent_1_id}: {agent_1_investor_rounds} rounds as investor, "
              f"{actual_game_rounds - agent_1_investor_rounds} rounds as trustee")
        print(f"  {self.agent_2_id}: {agent_2_investor_rounds} rounds as investor, "
              f"{actual_game_rounds - agent_2_investor_rounds} rounds as trustee")
