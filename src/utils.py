import os

#together API key
Together_API_KEY = "4f0440e2cc8baa37f8017270d398124bd4e477459f3500c74290591509b2e6b3"

#openrouter API key
API_KEY = "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"

# Messages: yes contains messages
# def call_llm(client, model, temperature, messages, logprobs=True, top_logprobs=5):
#     """Call LLM and get response"""
#     response = client.chat.completions.create(
#         model=model,
#         messages=messages,
#         temperature=temperature,
#         logprobs=logprobs,
#         top_logprobs=top_logprobs
#     )
#     return response.choices[0].message.content

import time
import random
from openai import APIError, RateLimitError, APIConnectionError

def call_llm(client, model, temperature, messages, max_retries=3, reasoning_effort="medium"):
    """
    Call LLM with retry logic and error handling.

    Args:
        client: OpenAI client instance
        model: Model name
        temperature: Temperature setting
        messages: Conversation messages
        max_retries: Maximum number of retry attempts (default: 3)
        reasoning_effort: Reasoning effort level for models that support it (default: "medium")

    Returns:
        dict: Structured response with content, reasoning, and usage data
            {
                "content": str,
                "reasoning": str or None,
                "usage": dict or None
            }

    Raises:
        Exception: If all retries fail or non-retryable error occurs
    """
    for attempt in range(max_retries):
        try:
            # Build request parameters
            request_params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }

            # Add reasoning parameter if supported (OpenRouter extended reasoning)
            # Skip for models that don't support it (e.g., OpenAI models via Azure)
            models_without_reasoning = ["openai/", "meta-llama/"]
            if reasoning_effort and not any(model.startswith(prefix) for prefix in models_without_reasoning):
                request_params["extra_body"] = {
                    "reasoning": {
                        "effort": reasoning_effort
                    }
                }

            response = client.chat.completions.create(**request_params)

            # Check if response is valid
            if not response.choices or not response.choices[0].message.content:
                raise ValueError("Empty response from LLM")

            # Extract reasoning if available (check multiple locations)
            reasoning = None
            msg = response.choices[0].message

            # Method 1: Direct reasoning attribute (works for Claude, some Gemini responses)
            if hasattr(msg, "reasoning") and msg.reasoning:
                reasoning = msg.reasoning

            # Method 2: Extract from reasoning_details array (Gemini format)
            # reasoning_details contains objects with type 'reasoning.text' or 'reasoning.encrypted'
            if reasoning is None and hasattr(msg, "reasoning_details") and msg.reasoning_details:
                reasoning_texts = []
                for detail in msg.reasoning_details:
                    if isinstance(detail, dict) and detail.get("type") == "reasoning.text":
                        text = detail.get("text", "")
                        if text:
                            reasoning_texts.append(text)
                if reasoning_texts:
                    reasoning = "\n".join(reasoning_texts)

            # Method 3: Check model_extra (where OpenAI SDK stores non-standard fields)
            if reasoning is None and hasattr(msg, "model_extra") and msg.model_extra:
                extra = msg.model_extra
                # Check for reasoning in model_extra
                if "reasoning" in extra and extra["reasoning"]:
                    reasoning = extra["reasoning"]
                # Check for reasoning_details in model_extra
                elif "reasoning_details" in extra and extra["reasoning_details"]:
                    reasoning_texts = []
                    for detail in extra["reasoning_details"]:
                        if isinstance(detail, dict) and detail.get("type") == "reasoning.text":
                            text = detail.get("text", "")
                            if text:
                                reasoning_texts.append(text)
                    if reasoning_texts:
                        reasoning = "\n".join(reasoning_texts)

            # Fallback: If reasoning tokens were used but content is encrypted/not returned
            if reasoning is None and hasattr(response, "usage"):
                reasoning_tokens = 0
                if hasattr(response.usage, "output_tokens_details") and hasattr(
                    response.usage.output_tokens_details, "reasoning_tokens"
                ):
                    reasoning_tokens = response.usage.output_tokens_details.reasoning_tokens
                elif hasattr(response.usage, "completion_tokens_details") and hasattr(
                    response.usage.completion_tokens_details, "reasoning_tokens"
                ):
                    reasoning_tokens = response.usage.completion_tokens_details.reasoning_tokens

                if reasoning_tokens and reasoning_tokens > 0:
                    # Reasoning was used but content was encrypted/not returned
                    reasoning = f"[{reasoning_tokens} reasoning tokens used, but content encrypted by provider]"

            # Extract usage information if available
            usage = None
            if hasattr(response, "usage"):
                # Extract reasoning tokens from nested structure (check both locations)
                reasoning_tokens = 0
                if hasattr(response.usage, "output_tokens_details") and hasattr(
                    response.usage.output_tokens_details, "reasoning_tokens"
                ):
                    reasoning_tokens = response.usage.output_tokens_details.reasoning_tokens
                elif hasattr(response.usage, "completion_tokens_details") and hasattr(
                    response.usage.completion_tokens_details, "reasoning_tokens"
                ):
                    reasoning_tokens = response.usage.completion_tokens_details.reasoning_tokens

                usage = {
                    "input_tokens": getattr(response.usage, "prompt_tokens", 0),
                    "output_tokens": getattr(response.usage, "completion_tokens", 0),
                    "reasoning_tokens": reasoning_tokens
                }

            # Return structured response
            return {
                "content": response.choices[0].message.content,
                "reasoning": reasoning,
                "usage": usage
            }
            
        except RateLimitError as e:
            # Rate limit: wait longer, then retry
            wait_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
            if attempt < max_retries - 1:
                print(f"⚠️  Rate limit hit. Waiting {wait_time:.2f}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                continue
            else:
                print(f"❌ Rate limit error after {max_retries} attempts: {e}")
                raise
        
        except APIConnectionError as e:
            # Network error: retry with backoff
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            if attempt < max_retries - 1:
                print(f"⚠️  Connection error. Waiting {wait_time:.2f}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                continue
            else:
                print(f"❌ Connection error after {max_retries} attempts: {e}")
                raise
        
        except APIError as e:
            # Other API errors: check if retryable
            if e.status_code and e.status_code >= 500:
                # Server error: retry
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                if attempt < max_retries - 1:
                    print(f"⚠️  Server error ({e.status_code}). Waiting {wait_time:.2f}s before retry {attempt + 1}/{max_retries}...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"❌ Server error after {max_retries} attempts: {e}")
                    raise
            else:
                # Client error (4xx): don't retry
                print(f"❌ Client error ({e.status_code}): {e}")
                raise
        
        except Exception as e:
            # Unexpected errors: log and raise
            print(f"❌ Unexpected error in LLM call: {type(e).__name__}: {e}")
            raise
    
    # Should never reach here, but just in case
    raise Exception(f"Failed to get LLM response after {max_retries} attempts")

def print_simulation_header(game, num_turns, num_agents, memory_capacity, agent_biases):
    """Print simulation configuration header"""
    print("=" * 80)
    print(f"SIMULATION: {game.__class__.__name__}")
    print("=" * 80)
    print(f"Number of rounds: {num_turns}")
    print(f"Number of agents: {num_agents}")
    print(f"Memory capacity: {memory_capacity}")
    if agent_biases:
        print(f"Agent biases: {agent_biases}")
    print(f"Role swapping: ENABLED (agents alternate roles each round)")
    print("-" * 80)
