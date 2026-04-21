from src.utils import call_llm
import datetime

class Agent:
    """Represents a single LLM agent with memory capacity"""

    def __init__(self, agent_id, model, temperature, client, memory_capacity, initial_bias, system_prompt=None, log_file=None): #system prompt is none, so it can be set later.
        self.agent_id = agent_id
        self.model = model
        self.temperature = temperature
        self.client = client
        self.memory_capacity = memory_capacity
        self.messages = []
        self.initial_bias = initial_bias
        self.system_prompt = system_prompt
        self.log_file = log_file
    

    def _log_interaction(self, prompt, response_data):
        """Log prompt and response to file if log_file is set"""
        if self.log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"TIMESTAMP: {timestamp}\n")
                f.write(f"AGENT: {self.agent_id}\n")
                f.write(f"MODEL: {self.model}\n")
                f.write(f"{'='*80}\n\n")

                f.write(f"PROMPT:\n{'-'*80}\n")
                f.write(f"{prompt}\n")
                f.write(f"{'-'*80}\n\n")

                f.write(f"RESPONSE:\n{'-'*80}\n")
                f.write(f"{response_data['content']}\n")
                f.write(f"{'-'*80}\n")

                if response_data.get('reasoning'):
                    f.write(f"\nREASONING:\n{'-'*80}\n")
                    f.write(f"{response_data['reasoning']}\n")
                    f.write(f"{'-'*80}\n")

                if response_data.get('usage'):
                    f.write(f"\nUSAGE:\n{'-'*80}\n")
                    f.write(f"Input tokens: {response_data['usage'].get('input_tokens', 'N/A')}\n")
                    f.write(f"Output tokens: {response_data['usage'].get('output_tokens', 'N/A')}\n")
                    f.write(f"Reasoning tokens: {response_data['usage'].get('reasoning_tokens', 'N/A')}\n")
                    f.write(f"{'-'*80}\n")

                f.write(f"\n")

    # Response with messages
    def respond(self, prompt):
        """Respond to a prompt with the LLM. The truncation effectuates
        a short term memory effect; earlier interactions are forgotten. Thus introduces recency bias;
        recent interactions have more impact than older ones. Remove if unwanted"""
        # Truncate oldest messages if memory is full (but keep system prompt)
        if len(self.messages) > self.memory_capacity * 2 + 1:  # *2 for user and assistant messages, +1 for system prompt
            # Keep system prompt (first message) and last N messages
            self.messages = [self.messages[0]] + self.messages[-(self.memory_capacity * 2):]

        self.messages.append({"role": "user", "content": prompt})

        # Call the LLM and get structured response
        response_data = call_llm(self.client, self.model, self.temperature, self.messages)

        # Log the interaction
        self._log_interaction(prompt, response_data)

        # Store full response data in messages
        self.messages.append({
            "role": "assistant",
            "content": response_data["content"],
            "reasoning": response_data.get("reasoning"),
            "usage": response_data.get("usage")
        })

        return response_data  # Return full structure, not just content