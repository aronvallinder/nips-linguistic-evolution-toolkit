import copy
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
        self.interaction_history = []
    

    def _log_interaction(self, prompt, response_data):
        """Log prompt and response to file if log_file is set"""
        if self.log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"TIMESTAMP: {timestamp}\n")
                f.write(f"AGENT: {self.agent_id}\n")
                f.write(f"MODEL: {self.model}\n")
                f.write(f"RESPONSE SOURCE: {response_data.get('response_source', 'llm')}\n")
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

    def _record_interaction(self, prompt, messages_sent, response_data=None, transcript_metadata=None, error=None):
        """Store the exact request/response payload for full transcripts."""
        plan = getattr(self.client, "request_plan", None)
        event = {
            "interaction_index": len(self.interaction_history) + 1,
            "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
            "agent_id": self.agent_id,
            "model": self.model,
            "temperature": plan.as_dict()["policy"]["temperature"] if plan is not None else self.temperature,
            "memory_capacity": self.memory_capacity,
            "metadata": transcript_metadata or {},
            "prompt": prompt,
            "messages_sent": messages_sent,
        }
        if response_data is not None:
            event["response"] = {
                "content": response_data.get("content", ""),
                "reasoning": response_data.get("reasoning"),
                "usage": response_data.get("usage"),
                "response_source": response_data.get("response_source", "llm"),
            }
        if error is not None:
            event["error"] = {
                "type": type(error).__name__,
                "message": str(error),
            }
        self.interaction_history.append(event)

    def _truncate_messages(self):
        """Apply the configured interaction-memory window."""
        if len(self.messages) > self.memory_capacity * 2 + 1:
            self.messages = [self.messages[0]] + self.messages[
                -(self.memory_capacity * 2):
            ]

    def _rollback_pending_prompt(self, prompt):
        """Remove an unanswered prompt before a clean simulation-level retry."""
        if (
            self.messages
            and self.messages[-1].get("role") == "user"
            and self.messages[-1].get("content") == prompt
        ):
            self.messages.pop()

    def scripted_response(
        self,
        prompt,
        response_data,
        transcript_metadata=None,
        remember=True,
    ):
        """Record a deterministic response without making an LLM call."""
        self._truncate_messages()
        if remember:
            self.messages.append({"role": "user", "content": prompt})
            messages_for_record = self.messages
        else:
            messages_for_record = self.messages + [
                {"role": "user", "content": prompt}
            ]
        messages_sent = copy.deepcopy(messages_for_record)
        normalized_response = {
            "content": response_data["content"],
            "reasoning": response_data.get("reasoning"),
            "usage": response_data.get("usage"),
            "response_source": response_data.get(
                "response_source",
                "scripted",
            ),
        }
        self._log_interaction(prompt, normalized_response)
        if remember:
            self.messages.append(
                {
                    "role": "assistant",
                    "content": normalized_response["content"],
                    "reasoning": normalized_response["reasoning"],
                    "usage": normalized_response["usage"],
                }
            )
        self._record_interaction(
            prompt,
            messages_sent,
            response_data=normalized_response,
            transcript_metadata=transcript_metadata,
        )
        return normalized_response

    # Response with messages
    def respond(
        self,
        prompt,
        transcript_metadata=None,
        remember=True,
        response_validator=None,
        memory_prompt=None,
    ):
        """Respond to a prompt with the LLM. The truncation effectuates
        a short term memory effect; earlier interactions are forgotten. Thus introduces recency bias;
        recent interactions have more impact than older ones. Remove if unwanted.

        When `remember=False`, the prompt and response are sent to the LLM and
        the response is returned/recorded as usual, but neither the user prompt
        nor the assistant response is appended to `self.messages`. Used by
        Phase 3 myth-only memory mode so game decisions don't pollute the
        seeded-myth chat memory.

        `memory_prompt` is an operational-retry escape hatch. The LLM and
        interaction audit see `prompt`, while a successful response is paired
        with `memory_prompt` in chat memory. This lets a format-only corrective
        retry enforce the response schema without changing the experimental
        prompt remembered in later rounds.
        """
        # Truncate oldest messages if memory is full (but keep system prompt).
        self._truncate_messages()

        if remember:
            self.messages.append({"role": "user", "content": prompt})
            messages_for_call = self.messages
        else:
            # Build a transient message list that includes the prompt without
            # mutating self.messages.
            messages_for_call = self.messages + [{"role": "user", "content": prompt}]
        messages_sent = copy.deepcopy(messages_for_call)

        # Call the LLM and get structured response
        try:
            response_data = call_llm(self.client, self.model, self.temperature, messages_for_call)
        except Exception as exc:
            if remember:
                self._rollback_pending_prompt(prompt)
            self._record_interaction(
                prompt,
                messages_sent,
                response_data={"usage": exc.usage} if hasattr(exc, "usage") else None,
                transcript_metadata=transcript_metadata,
                error=exc,
            )
            raise

        # Log the interaction
        self._log_interaction(prompt, response_data)

        # Validate task-specific response boundaries before committing the
        # assistant response to chat memory. Preserve the rejected payload in
        # the interaction audit, but remove the pending user prompt so a retry
        # starts from the same clean conversation state.
        if response_validator is not None:
            try:
                response_validator(response_data.get("content", ""))
            except Exception as exc:
                if remember:
                    self._rollback_pending_prompt(prompt)
                self._record_interaction(
                    prompt,
                    messages_sent,
                    response_data=response_data,
                    transcript_metadata=transcript_metadata,
                    error=exc,
                )
                raise

        if remember:
            if memory_prompt is not None:
                if not self.messages or self.messages[-1].get("role") != "user":
                    raise RuntimeError(
                        "Cannot replace retry prompt: pending user message is missing."
                    )
                self.messages[-1]["content"] = memory_prompt
            # Store full response data in messages
            self.messages.append({
                "role": "assistant",
                "content": response_data["content"],
                "reasoning": response_data.get("reasoning"),
                "usage": response_data.get("usage")
            })
        self._record_interaction(
            prompt,
            messages_sent,
            response_data=response_data,
            transcript_metadata=transcript_metadata,
        )

        return response_data  # Return full structure, not just content
