from games.base_game import Game
import re
import random


# ============================================================================
# TRUST GAME IMPLEMENTATION
# ============================================================================

class TrustGame(Game):
    """Trust/Investment game with sequential moves and role swapping"""

    def __init__(self, endowment, multiplier, system_prompt_template=None, personas=None,
                 round1_investor_template=None, round1_trustee_template=None,
                 later_investor_template=None, later_trustee_template=None,
                 multiplier_distribution=None):
        """
        Args:
            endowment: Starting amount for investor each round
            multiplier: Base multiplier value (used for 'fixed' distribution or as base for others)
            multiplier_distribution: Dict specifying how multiplier changes over rounds
                - None or {"type": "fixed"}: Use fixed multiplier value
                - {"type": "increasing", "start": 1, "step": 1}: Start at 1, increase by 1 each round
                - {"type": "decreasing", "start": 10, "step": 1}: Start at 10, decrease by 1 each round
                - {"type": "random", "min": 1, "max": 5}: Random value between min and max each round
        """
        super().__init__()
        self.endowment = endowment
        self.base_multiplier = multiplier  # Keep for backward compatibility
        self.multiplier_distribution = multiplier_distribution or {"type": "fixed"}
        self.system_prompt_template = system_prompt_template
        self.round1_investor_template = round1_investor_template
        self.round1_trustee_template = round1_trustee_template
        self.later_investor_template = later_investor_template
        self.later_trustee_template = later_trustee_template
        self.personas = personas or {}
        # Agent IDs (fixed)
        self.agent_1_id = "Agent_1"
        self.agent_2_id = "Agent_2"
        # Cache for random multipliers (so both agents see same value in a round)
        self._round_multipliers = {}

    def get_multiplier(self, turn):
        """Get the multiplier for a given turn based on distribution type"""
        dist = self.multiplier_distribution
        dist_type = dist.get("type", "fixed")

        if dist_type == "fixed":
            return self.base_multiplier

        elif dist_type == "increasing":
            start = dist.get("start", self.base_multiplier)
            step = dist.get("step", 1)
            return start + (turn - 1) * step

        elif dist_type == "decreasing":
            start = dist.get("start", self.base_multiplier)
            step = dist.get("step", 1)
            return max(0, start - (turn - 1) * step)  # Don't go below 0

        elif dist_type == "random":
            # Cache random value so both agents see same multiplier in a round
            if turn not in self._round_multipliers:
                min_val = dist.get("min", 1)
                max_val = dist.get("max", 5)
                self._round_multipliers[turn] = random.uniform(min_val, max_val)
            return self._round_multipliers[turn]

        else:
            # Unknown type, fall back to base multiplier
            return self.base_multiplier

    @property
    def multiplier(self):
        """Backward compatibility: return base multiplier for system prompt"""
        return self.base_multiplier
    
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

        return base_prompt
    
    def get_game_prompt_round_1(self, agent_id, agent, turn):
        """First turn"""
        roles = self.get_roles_for_round(turn)

        if agent_id == roles["investor"]:
            if not self.round1_investor_template:
                raise ValueError(
                    "No prompt provided. Provide prompt in config/experiments.yaml under "
                    "prompt_templates, named 'trust_game_round1_investor'"
                )
            return self.round1_investor_template.format(
                endowment=self.endowment
            )
        else:
            # Trustee gets prompted after investor, will have pending_sent available
            sent = self.sim_data_ref.game_data.get("pending_sent")
            if sent is None:
                raise ValueError("pending_sent not found in game_data. The amount send by Investor is unknown. Investor should have responded first.")
            current_multiplier = self.get_multiplier(turn)
            received = sent * current_multiplier
            percentage = (sent / self.endowment * 100)

            if not self.round1_trustee_template:
                raise ValueError(
                    "No prompt provided. Provide prompt in config/experiments.yaml under "
                    "prompt_templates, named 'trust_game_round1_trustee'"
                )
            return self.round1_trustee_template.format(
                sent=sent,
                percentage=percentage,
                received=received
            )
    
    def get_game_prompt_later_round(self, agent_id, turn, sim_data, last_responses):
        """Subsequent turns"""
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

        current_multiplier = self.get_multiplier(turn)
        sent = sim_data.game_data["pending_sent"]
        received = sent * current_multiplier
        last_round_sent = last_round['sent']
        last_round_received = last_round.get('received', last_round_sent * self.base_multiplier)  # Use stored value
        last_round_returned = last_round['returned']
        agent_balance = sim_data.game_data["balances"][agent_id]
        last_round_sent_percentage = (last_round_sent / self.endowment * 100)
        last_round_trustee_payoff = last_round['trustee_payoff']
        last_round_investor_payoff = last_round['investor_payoff']

        if agent_id == roles["investor"]:
            if not self.later_investor_template:
                raise ValueError(
                    "No prompt provided. Provide prompt in config/experiments.yaml under "
                    "prompt_templates, named 'trust_game_later_investor'"
                )
            return self.later_investor_template.format(
                turn=turn,
                last_round_sent=last_round_sent,
                last_round_sent_percentage=last_round_sent_percentage,
                last_round_received=last_round_received,
                last_round_returned=last_round_returned,
                last_round_trustee_payoff=last_round_trustee_payoff,
                agent_balance=agent_balance,
                endowment=self.endowment
            )
        else:
            if not self.later_trustee_template:
                raise ValueError(
                    "No prompt provided. Provide prompt in config/experiments.yaml under "
                    "prompt_templates, named 'trust_game_later_trustee'"
                )
            return self.later_trustee_template.format(
                turn=turn,
                last_round_sent=last_round_sent,
                last_round_sent_percentage=last_round_sent_percentage,
                last_round_received=last_round_received,
                last_round_returned=last_round_returned,
                last_round_investor_payoff=last_round_investor_payoff,
                agent_balance=agent_balance,
                received=received
            )
    
    def process_intermediate_response(self, agent_id, response, turn, sim_data):
        """Called after investor responds, before trustee"""
        roles = self.get_roles_for_round(turn)
        if agent_id == roles["investor"]:
            sent_amount = self._extract_amount(response, "send")
            #sent_amount = max(0, min(sent_amount, self.endowment))    # Clamps to valid range: Forces 0 ≤ amount ≤ endowment (do we want this???))
            sim_data.game_data["pending_sent"] = sent_amount
            # Store reference for get_round_1_prompt to use
            self.sim_data_ref = sim_data
    
    def process_turn(self, turn, agent_responses, sim_data):
        """Process complete turn (both moves done)"""
        # Initialize on first turn
        if "balances" not in sim_data.game_data:
            sim_data.game_data["balances"] = {self.agent_1_id: 0, self.agent_2_id: 0}
            sim_data.game_data["pending_sent"] = 0
            self.sim_data_ref = sim_data
        
        # Get roles for this round
        roles = self.get_roles_for_round(turn)
        investor_id = roles["investor"]
        trustee_id = roles["trustee"]
        
        # Extract amounts
        sent = self._extract_amount(agent_responses[investor_id], "send")
        #sent = max(0, min(sent, self.endowment))   # Clamps to valid range: Forces 0 ≤ amount ≤ endowment (do we want this???))

        returned = self._extract_amount(agent_responses[trustee_id], "return")
        current_multiplier = self.get_multiplier(turn)
        received = sent * current_multiplier
        #returned = max(0, min(returned, received))  # Clamps to valid range: Forces 0 ≤ amount ≤ endowment (do we want this???))

        # Calculate payoffs
        investor_payoff = (self.endowment - sent) + returned
        trustee_payoff = received - returned
        
        # Update balances
        sim_data.game_data["balances"][investor_id] += investor_payoff
        sim_data.game_data["balances"][trustee_id] += trustee_payoff
        
        # Fill in the pre-created entry for this round with game data
        for entry in sim_data.conversation_history:
            if entry["round"] == turn:
                entry["sent"] = sent
                entry["received"] = received
                entry["returned"] = returned
                entry["multiplier"] = current_multiplier  # Store multiplier used this round
                entry["investor_payoff"] = investor_payoff
                entry["trustee_payoff"] = trustee_payoff
                entry["balances"] = dict(sim_data.game_data["balances"])
                entry["actions"] = {
                    investor_id: {"action": "sent", "amount": sent},
                    trustee_id: {"action": "returned", "amount": returned}
                }
                break
        
        return {
            investor_id: {"sent": sent},
            trustee_id: {"returned": returned}
        }
    
    def _extract_amount(self, response_data, key):
        """Extract number from JSON response in structured response data

        Args:
            response_data: Either a string (old format) or dict with 'content' key (new format)
            key: The JSON key to extract ('send' or 'return')

        Returns:
            float: The extracted amount
        """
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
        """Print round summary"""
        entry = sim_data.conversation_history[-1]
        roles = entry["roles"]
        
        # Determine which agent had which role
        investor_id = [aid for aid, role in roles.items() if role == "investor"][0]
        trustee_id = [aid for aid, role in roles.items() if role == "trustee"][0]
        
        print(f"\n{'*' * 80}")
        print(f"ROUND {turn} COMPLETE")
        print(f"  Roles: {investor_id} = Investor, {trustee_id} = Trustee")
        print(f"  Sent: ${entry['sent']} → Received: ${entry['received']} → Returned: ${entry['returned']}")
        print(f"  Payoffs: {investor_id} ${entry['investor_payoff']}, {trustee_id} ${entry['trustee_payoff']}")
        print(f"  Cumulative: {self.agent_1_id} ${entry['balances'][self.agent_1_id]}, {self.agent_2_id} ${entry['balances'][self.agent_2_id]}")
        print(f"{'*' * 80}")
    
    def print_game_summary(self, sim_data):
        """Final summary"""
        # Calculate total simulation rounds from the highest round number
        total_rounds = max((entry.get("round", 0) for entry in sim_data.conversation_history), default=0)
        
        print("\n" + "=" * 80)
        print("GAME SUMMARY")
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
        print(f"Final earnings: {self.agent_1_id} ${sim_data.game_data['balances'][self.agent_1_id]}, {self.agent_2_id} ${sim_data.game_data['balances'][self.agent_2_id]}")

        # Show role distribution
        agent_1_investor_rounds = sum(1 for r in game_rounds if "roles" in r and r["roles"][self.agent_1_id] == "investor")
        agent_2_investor_rounds = sum(1 for r in game_rounds if "roles" in r and r["roles"][self.agent_2_id] == "investor")
        print(f"\nRole distribution:")
        print(f"  {self.agent_1_id}: {agent_1_investor_rounds} rounds as investor, {actual_game_rounds - agent_1_investor_rounds} rounds as trustee")
        print(f"  {self.agent_2_id}: {agent_2_investor_rounds} rounds as investor, {actual_game_rounds - agent_2_investor_rounds} rounds as trustee")
