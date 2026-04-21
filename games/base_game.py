class Game:
    """Base class for all games"""
    
    def __init__(self):
        pass
    
    def get_system_prompt(self, agent_id, agent):
        """Return the system prompt for an agent (game rules/context)"""
        raise NotImplementedError
    
    def get_round_1_prompt(self, agent_id, agent):
        """Return the initial user prompt for first turn"""
        raise NotImplementedError
    
    def get_later_round_prompt(self, agent_id, turn, sim_data, last_responses):
        """Return the prompt for an agent on subsequent turns"""
        raise NotImplementedError
    
    def process_turn(self, turn, agent_responses, sim_data):
        """Process the responses from all agents and update game state"""
        raise NotImplementedError
    
    def print_turn_summary(self, turn, agent_responses, sim_data):
        """Print summary of what happened this turn"""
        pass
    
    def print_game_summary(self, sim_data):
        """Print final game summary"""
        pass