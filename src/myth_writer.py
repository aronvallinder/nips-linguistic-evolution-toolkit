# ============================================================================
# MYTH WRITING
# ============================================================================

class MythWriter:
    """Handles myth writing functionality, separate from game logic"""

    def __init__(self, myth_topic, round1_template=None, later_rounds_template=None):
        self.myth_topic = myth_topic
        self.round1_template = round1_template
        self.later_rounds_template = later_rounds_template
    
    def get_myth_prompt_round_1(self, agent_id, turn, sim_data):
        """Generate prompt for myth writing"""
        if not self.round1_template:
            raise ValueError(
                "No prompt provided. Provide prompt in config/experiments.yaml under "
                "prompt_templates, named 'myth_writing_default'"
            )
        return self.round1_template.format(myth_topic=self.myth_topic)

    def get_myth_prompt_round_later(self, agent_id, turn, sim_data):
        """Generate prompt for myth writing with the agent's previous myth"""
        if not self.later_rounds_template:
            raise ValueError(
                "No prompt provided. Provide prompt in config/experiments.yaml under "
                "prompt_templates, named 'myth_writing_later_rounds'"
            )

        # Get this agent's myth from previous round
        last_myth = ""
        other_agent_myth = ""

        for entry in sim_data.conversation_history:
            if entry["round"] == turn - 1 and "myths" in entry:
                if agent_id in entry["myths"]:
                    last_myth = entry["myths"][agent_id]

                # Get the other agent's myth
                for other_agent_id, myth in entry["myths"].items():
                    if other_agent_id != agent_id:
                        other_agent_myth = myth
                        break
                break

        if not last_myth:
            raise ValueError(f"NO SELF MYTH ERROR: No previous myth found for {agent_id} (you/self agent) in round {turn - 1}. Cannot generate later round prompt.")

        if not other_agent_myth:
            raise ValueError(f"OTHER AGENT MYTH ERROR: No previous myth found for {agent_id} (other agent) in round {turn - 1}. Cannot generate later round prompt.")

        return self.later_rounds_template.format(
            last_myth=last_myth,
            other_agent_myth=other_agent_myth
        )


    def process_myths(self, turn, agent_myths, sim_data):
        """Store the myths written by agents

        Args:
            turn: Current round number
            agent_myths: Dict mapping agent_id to response_data (dict with 'content', 'reasoning', 'usage')
            sim_data: Simulation data object
        """
        # Find the pre-created entry for this turn and fill in myths
        # Extract just the content from structured response data for storage
        myths_content = {}
        for agent_id, response_data in agent_myths.items():
            # Handle both old string format and new dict format for backward compatibility
            if isinstance(response_data, str):
                myths_content[agent_id] = response_data
            else:
                myths_content[agent_id] = response_data.get("content", "")

        for entry in sim_data.conversation_history:
            if entry["round"] == turn:
                entry["myths"] = myths_content
                break