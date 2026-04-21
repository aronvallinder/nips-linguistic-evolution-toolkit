from games.base_game import Game
import re


# ============================================================================
# TRUST GAME IMPLEMENTATION
# ============================================================================

class TrustGame(Game):
    """Trust/Investment game with sequential moves and role swapping"""

    def __init__(self, endowment, multiplier, system_prompt_template=None, personas=None):
        super().__init__()
        self.endowment = endowment
        self.multiplier = multiplier
        self.system_prompt_template = system_prompt_template
        self.personas = personas or {}
        # Agent IDs (fixed)
        self.agent_1_id = "Agent_1"
        self.agent_2_id = "Agent_2"
    
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
        # Use custom template if provided, otherwise use default
        if self.system_prompt_template:
            base_prompt = self.system_prompt_template.format(
                endowment=self.endowment,
                multiplier=self.multiplier
            )
        else:
            base_prompt = f"""You are an agent in a trust game. You will play different roles across rounds.

When you are the INVESTOR:
- You receive ${self.endowment} each round
- You decide how much to SEND to the TRUSTEE ($0-${self.endowment})
- You can defect by sending $0
- Amount sent is multiplied by {self.multiplier}x
- Trustee decides how much to RETURN
- Trustee can defect by returning $0
- You keep: ${self.endowment} - sent + returned
- Trustee keeps: received - returned
- Response format: {{'send': <amount>, 'reason': <reasoning>}}

When you are the TRUSTEE:
- Investor receives ${self.endowment}
- Investor decides how much to SEND to you ($0-${self.endowment})
- Investor can defect by sending $0
- Amount sent is multiplied by {self.multiplier}x
- You decide how much to RETURN
- You can defect by returning $0
- Investor keeps: ${self.endowment} - sent + returned
- You keep: received - returned
- Response format: {{'return': <amount>, 'reason': <reasoning>}}

IMPORTANT: Always respond in the correct format based on your current role."""

        # Add persona if specified for this agent
        if agent_id in self.personas and self.personas[agent_id].get('system_addition'):
            base_prompt += f"\n\n{self.personas[agent_id]['system_addition']}"

        return base_prompt
    
    def get_game_prompt_round_1(self, agent_id, agent, turn):
        """First turn"""
        roles = self.get_roles_for_round(turn)
        
        if agent_id == roles["investor"]:
            return f"Round 1: You are the INVESTOR. You have ${self.endowment}. How much do you send? (0-{self.endowment})"
        else:
            # Trustee gets prompted after investor, will have pending_sent available
            sent = self.sim_data_ref.game_data.get("pending_sent")
            if sent is None:
                raise ValueError("pending_sent not found in game_data. The amount send by Investor is unknown. Investor should have responded first.")
            received = sent * self.multiplier
            percentage = (sent / self.endowment * 100)
            return f"Round 1: You are the TRUSTEE. Investor sent ${sent}, that is {percentage:.1f}% of its total endowment. You received ${received}. How much do you return? (0-{received})"
    
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

        sent = sim_data.game_data["pending_sent"]
        received = sent * self.multiplier
        last_round_sent = last_round['sent']
        last_round_received = last_round_sent * self.multiplier
        last_round_returned = last_round['returned']
        agent_balance = sim_data.game_data["balances"][agent_id]
        percentage = (sent / self.endowment * 100)
        last_round_sent_percentage = (last_round_sent / self.endowment * 100)
        last_round_received_percentage = (last_round_received / self.endowment * 100)
        last_round_trustee_payoff = last_round['trustee_payoff']
        last_round_investor_payoff = last_round['investor_payoff']

        if agent_id == roles["investor"]:
            return f"""Round {turn}

You are the INVESTOR this round. Last round you were the TRUSTEE. The other player sent ${last_round_sent}, 
that was {last_round_sent_percentage:.1f}% of its total endowment. You received ${last_round_received}. 
You returned ${last_round_returned}. So your payoff was {last_round_trustee_payoff}.
Your total earnings accross all rounds are ${agent_balance}.
How much do you send to the TRUSTEE this round? (0-{self.endowment})"""
        else:
            return f"""Round {turn}

You are the TRUSTEE this round. Last round you were the INVESTOR. The other player sent ${last_round_sent}, 
that was {last_round_sent_percentage:.1f}% of its total endowment. You received ${last_round_received}. 
The other player returned ${last_round_returned}. So your payoff was {last_round_investor_payoff}.
Your total earnings accross all rounds are ${agent_balance}. 
How much do you return to the INVESTOR this round? (0-{received})"""
    
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
        received = sent * self.multiplier
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
    
    def _extract_amount(self, response, key):
        """Extract number from response"""
        pattern = rf"'{key}':\s*(\d+\.?\d*)|" + rf'"{key}":\s*(\d+\.?\d*)'
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            return float(match.group(1) or match.group(2))
        raise ValueError(f"Could not extract {key} from: {response[:200]}")
    
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
