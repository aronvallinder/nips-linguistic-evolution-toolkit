import os
import random
import re
import time
import json
import math
import urllib.error
import urllib.request

from dotenv import load_dotenv
from openai import APIConnectionError, APIError, OpenAI, RateLimitError
from src.llm_settings import ENDPOINTS, LLMSettingsError

try:
    import anthropic
except ImportError:
    anthropic = None

load_dotenv()

TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MAX_TOKENS = os.environ.get("OPENROUTER_MAX_TOKENS", "")
OPENROUTER_REASONING_EFFORT = os.environ.get("OPENROUTER_REASONING_EFFORT", "").strip()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "auto").strip().lower() or "auto"

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
VALID_PROVIDER_MODES = {"auto", "direct", "openrouter", "openai", "anthropic", "google", "gemini"}

DIRECT_MODEL_ALIASES = {
    # OpenRouter-style Anthropic slugs used in repo configs -> direct Anthropic API IDs.
    "anthropic/claude-3-haiku": "claude-3-haiku-20240307",
    "anthropic/claude-3.5-sonnet": "claude-3-5-sonnet-latest",
    "anthropic/claude-haiku-4.5": "claude-haiku-4-5-20251001",
    "anthropic/claude-sonnet-4": "claude-sonnet-4-20250514",
    "anthropic/claude-sonnet-4.5": "claude-sonnet-4-5-20250929",
    "anthropic/claude-sonnet-4.6": "claude-sonnet-4-6",
    "anthropic/claude-opus-4": "claude-opus-4-20250514",
    "anthropic/claude-opus-4.1": "claude-opus-4-1-20250805",
    "anthropic/claude-opus-4.5": "claude-opus-4-5-20251101",
    "anthropic/claude-opus-4.6": "claude-opus-4-6",
    # OpenRouter-style Google slugs used in repo configs -> direct Gemini API IDs.
    "google/gemini-3.7-flash": "gemini-3.7-flash",
    "google/gemini-3.6-flash": "gemini-3.6-flash",
    "google/gemini-3-flash-preview": "gemini-3-flash-preview",
    "google/gemini-3-pro-preview": "gemini-3.1-pro-preview",
    "google/gemini-3.1-pro-preview": "gemini-3.1-pro-preview",
}


class LLMClient:
    """Small provider wrapper around the concrete SDK client."""

    def __init__(self, provider, client):
        self.provider = provider
        self.client = client
        self.request_plan = None

    def __getattr__(self, name):
        return getattr(self.client, name)


def _env(name):
    return os.environ.get(name, "")


def _provider_for_model(model):
    if model.startswith("openai/"):
        return "openai"
    if model.startswith("anthropic/"):
        return "anthropic"
    if model.startswith("google/"):
        return "google"
    return "openrouter"


def _direct_model_override_name(model):
    normalized = re.sub(r"[^A-Z0-9]+", "_", model.upper()).strip("_")
    return f"LLM_DIRECT_MODEL_{normalized}"


def resolve_model_for_provider(client, model):
    """Return the model ID that should be sent to the selected provider."""
    plan = getattr(client, "request_plan", None)
    if plan is not None:
        if model != plan.as_dict()["model"]:
            raise LLMSettingsError("Model changed after request planning")
        return plan.provider_model
    provider, _ = _unwrap_client(client)
    if provider == "openrouter":
        return model

    override = _env(_direct_model_override_name(model))
    if override:
        return override

    if model in DIRECT_MODEL_ALIASES:
        return DIRECT_MODEL_ALIASES[model]

    prefix = f"{provider}/"
    if model.startswith(prefix):
        return model[len(prefix):]
    return model


def llm_runtime_metadata(client, model):
    """Return non-secret provider settings needed to reproduce a run."""
    plan = getattr(client, "request_plan", None)
    if plan is not None:
        return {
            "llm_provider": plan.provider,
            "provider_model": resolve_model_for_provider(client, model),
            "llm_provider_mode": plan.as_dict()["policy"]["provider"],
            "llm_request": plan.as_dict(),
        }
    provider, _ = _unwrap_client(client)
    metadata = {
        "llm_provider": provider,
        "provider_model": resolve_model_for_provider(client, model),
        "llm_provider_mode": (
            _env("LLM_PROVIDER") or LLM_PROVIDER or "auto"
        ).strip().lower(),
    }
    if provider == "anthropic":
        metadata.update(
            {
                "max_output_tokens": int(
                    _env("ANTHROPIC_MAX_TOKENS") or "1024"
                ),
                "max_output_tokens_source": "ANTHROPIC_MAX_TOKENS",
            }
        )
    elif provider == "openrouter":
        metadata.update(
            {
                "max_output_tokens": (
                    int(OPENROUTER_MAX_TOKENS)
                    if OPENROUTER_MAX_TOKENS
                    else None
                ),
                "max_output_tokens_source": (
                    "OPENROUTER_MAX_TOKENS"
                    if OPENROUTER_MAX_TOKENS
                    else "provider_default"
                ),
            }
        )
    elif provider == "google":
        thinking_level = _env("GEMINI_THINKING_LEVEL")
        metadata.update(
            {
                "max_output_tokens": None,
                "max_output_tokens_source": "provider_default",
                "thinking_level": thinking_level or "provider_default",
                "thinking_level_source": (
                    "GEMINI_THINKING_LEVEL"
                    if thinking_level
                    else "provider_default"
                ),
                "temperature_sent": _gemini_supports_temperature(
                    resolve_model_for_provider(client, model)
                ),
                "request_timeout_seconds": _gemini_request_timeout_seconds(),
                "request_timeout_source": (
                    "GEMINI_REQUEST_TIMEOUT_SECONDS"
                    if _env("GEMINI_REQUEST_TIMEOUT_SECONDS")
                    else "default_120"
                ),
            }
        )
    elif provider == "openai":
        configured_effort = _env("OPENAI_REASONING_EFFORT")
        metadata.update(
            {
                "max_output_tokens": None,
                "max_output_tokens_source": "provider_default",
                "reasoning_effort": _direct_openai_reasoning_effort(),
                "reasoning_effort_source": (
                    "OPENAI_REASONING_EFFORT"
                    if configured_effort
                    else "repository_default_minimal"
                ),
            }
        )
    else:
        metadata.update(
            {
                "max_output_tokens": None,
                "max_output_tokens_source": "provider_default",
            }
        )
    return metadata


def create_llm_client(model, provider=None, request_plan=None):
    """
    Create a provider client for the given repo model slug.

    LLM_PROVIDER modes:
      - auto: direct OpenAI/Anthropic when the matching key exists, else OpenRouter.
      - direct: require a direct provider for openai/*, anthropic/*, or google/* models.
      - openrouter/openai/anthropic/google/gemini: force that provider.
    """
    if request_plan is not None:
        if model != request_plan.as_dict()["model"]:
            raise LLMSettingsError("Model differs from the resolved request plan")
        factories = {
            "openai": lambda: _create_openai_client(pinned=True),
            "anthropic": lambda: _create_anthropic_client(pinned=True),
            "google": _create_gemini_client,
            "openrouter": _create_openrouter_client,
        }
        client = factories[request_plan.provider]()
        client.request_plan = request_plan
        return client
    selected = (provider or _env("LLM_PROVIDER") or LLM_PROVIDER or "auto").strip().lower()
    if selected not in VALID_PROVIDER_MODES:
        raise RuntimeError(
            f"Unsupported LLM_PROVIDER={selected!r}. Expected one of: "
            f"{', '.join(sorted(VALID_PROVIDER_MODES))}."
        )

    model_provider = _provider_for_model(model)

    if selected == "openrouter":
        return _create_openrouter_client()
    if selected == "openai":
        return _create_openai_client()
    if selected == "anthropic":
        return _create_anthropic_client()
    if selected in {"google", "gemini"}:
        return _create_gemini_client()

    if selected == "direct":
        if model_provider == "openai":
            return _create_openai_client()
        if model_provider == "anthropic":
            return _create_anthropic_client()
        if model_provider == "google":
            return _create_gemini_client()
        raise RuntimeError(
            f"LLM_PROVIDER=direct cannot run model {model!r}. Direct routing is "
            "implemented for openai/*, anthropic/*, and google/* models only."
        )

    if model_provider == "openai" and _env("OPENAI_API_KEY"):
        return _create_openai_client()
    if model_provider == "anthropic" and _env("ANTHROPIC_API_KEY"):
        return _create_anthropic_client()
    if model_provider == "google" and _gemini_api_key():
        return _create_gemini_client()
    if _env("OPENROUTER_API_KEY"):
        return _create_openrouter_client()

    raise RuntimeError(
        f"No usable API key found for model {model!r}. Set OPENAI_API_KEY for "
        "openai/* models, ANTHROPIC_API_KEY for anthropic/* models, "
        "GEMINI_API_KEY or GOOGLE_API_KEY for google/* models, or "
        "OPENROUTER_API_KEY for OpenRouter fallback."
    )


def _create_openrouter_client():
    api_key = _env("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set.")
    return LLMClient(
        "openrouter",
        OpenAI(api_key=api_key, base_url=OPENROUTER_BASE_URL),
    )


def _create_openai_client(pinned=False):
    api_key = _env("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return LLMClient("openai", OpenAI(api_key=api_key, base_url=ENDPOINTS["openai"] if pinned else None))


def _create_anthropic_client(pinned=False):
    api_key = _env("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set.")
    if anthropic is None:
        raise RuntimeError(
            "The anthropic package is not installed. Run: pip install -r requirements.txt"
        )
    return LLMClient("anthropic", anthropic.Anthropic(api_key=api_key, base_url=ENDPOINTS["anthropic"] if pinned else None))


def _gemini_api_key():
    return _env("GEMINI_API_KEY") or _env("GOOGLE_API_KEY") or _env("GOOGLE_GENERATIVE_AI_API_KEY")


def _create_gemini_client():
    api_key = _gemini_api_key()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY or GOOGLE_API_KEY is not set.")
    return LLMClient("google", {"api_key": api_key, "base_url": GEMINI_API_BASE_URL})


def _unwrap_client(client):
    if isinstance(client, LLMClient):
        return client.provider, client.client
    return getattr(client, "provider", "openrouter"), getattr(client, "client", client)


def _chat_messages(messages):
    sanitized = []
    for message in messages:
        role = message.get("role")
        content = message.get("content")
        if role in {"system", "user", "assistant"} and content is not None:
            sanitized.append({"role": role, "content": content})
    return sanitized


def _anthropic_messages(messages):
    system_parts = []
    chat_messages = []
    for message in messages:
        role = message.get("role")
        content = message.get("content")
        if content is None:
            continue
        if role == "system":
            system_parts.append(content)
        elif role in {"user", "assistant"}:
            chat_messages.append({"role": role, "content": content})

    system = "\n\n".join(system_parts) if system_parts else None
    return system, chat_messages


def _gemini_messages(messages):
    system_parts = []
    contents = []
    for message in messages:
        role = message.get("role")
        content = message.get("content")
        if content is None:
            continue
        if role == "system":
            system_parts.append(content)
        elif role in {"user", "assistant"}:
            contents.append({
                "role": "model" if role == "assistant" else "user",
                "parts": [{"text": content}],
            })

    system_instruction = None
    if system_parts:
        system_instruction = {"parts": [{"text": "\n\n".join(system_parts)}]}
    return system_instruction, contents


def call_llm(client, model, temperature, messages, max_retries=3, reasoning_effort="medium"):
    """
    Call LLM with retry logic and provider-specific message adaptation.

    Args:
        client: LLMClient wrapper or OpenAI-compatible client instance
        model: Repo model slug
        temperature: Temperature setting
        messages: Conversation messages
        max_retries: Maximum number of retry attempts (default: 3)
        reasoning_effort: Reasoning effort level for OpenRouter models that support it

    Returns:
        dict: Structured response with content, reasoning, and usage data
    """
    plan = getattr(client, "request_plan", None)
    try:
        return _dispatch_llm(client, model, temperature, messages, max_retries, reasoning_effort, plan)
    except Exception as error:
        if plan is None or isinstance(error, LLMRequestError):
            raise
        usage = _request_usage({}, plan, None)
        usage.update(outcome="error", error_type=type(error).__name__, status_code=getattr(error, "status_code", getattr(error, "code", None)))
        message = _public_error(error, plan)
        raise LLMRequestError(message, usage) from None


def _dispatch_llm(client, model, temperature, messages, max_retries, reasoning_effort, request_plan):
    provider, api_client = _unwrap_client(client)
    if request_plan is not None and provider != request_plan.provider:
        raise LLMSettingsError("Provider changed after request planning")
    if request_plan is not None:
        endpoint = api_client["base_url"] if provider == "google" else str(api_client.base_url)
        if endpoint.rstrip("/") != request_plan.as_dict()["endpoint"].rstrip("/"):
            raise LLMSettingsError("Endpoint changed after request planning")
    extra = {"request_plan": request_plan} if request_plan is not None else {}
    if provider == "anthropic":
        return _call_anthropic(
            api_client,
            resolve_model_for_provider(client, model),
            temperature,
            messages,
            max_retries,
            **extra,
        )
    if provider == "google":
        return _call_gemini(
            api_client,
            resolve_model_for_provider(client, model),
            temperature,
            messages,
            max_retries,
            **extra,
        )
    return _call_openai_compatible(
        provider,
        api_client,
        resolve_model_for_provider(client, model),
        temperature,
        messages,
        max_retries,
        reasoning_effort,
        **extra,
    )


def _call_openai_compatible(
    provider,
    client,
    provider_model,
    temperature,
    messages,
    max_retries,
    reasoning_effort,
    request_plan=None,
):
    for attempt in range(max_retries):
        try:
            request_params = {
                "model": provider_model,
                "messages": _chat_messages(messages),
            }
            if request_plan is None and _supports_custom_temperature(provider, provider_model):
                request_params["temperature"] = temperature
            if request_plan is None and _supports_reasoning_effort(provider, provider_model):
                request_params["reasoning_effort"] = _direct_openai_reasoning_effort()

            if request_plan is None and provider == "openrouter" and OPENROUTER_MAX_TOKENS:
                request_params["max_tokens"] = int(OPENROUTER_MAX_TOKENS)

            # OpenRouter-only extension. Direct OpenAI calls use standard OpenAI params.
            # OPENROUTER_REASONING_EFFORT=none disables the extra reasoning body
            # for low-budget runs where short direct answers are sufficient.
            active_reasoning_effort = (
                OPENROUTER_REASONING_EFFORT
                if OPENROUTER_REASONING_EFFORT
                else reasoning_effort
            )
            if isinstance(active_reasoning_effort, str) and active_reasoning_effort.lower() in {"", "none", "false", "0", "off"}:
                active_reasoning_effort = None

            models_without_reasoning = ["openai/", "meta-llama/"]
            if (
                provider == "openrouter"
                and active_reasoning_effort
                and not any(provider_model.startswith(prefix) for prefix in models_without_reasoning)
            ):
                request_params["extra_body"] = {
                    "reasoning": {
                        "effort": active_reasoning_effort
                    }
                }

            if request_plan is not None:
                request_params = {
                    "model": provider_model,
                    "messages": _chat_messages(messages),
                    "extra_body": request_plan.parameters,
                }

            response = client.chat.completions.create(**request_params)

            if not response.choices or not response.choices[0].message.content:
                if request_plan is not None:
                    finish = response.choices[0].finish_reason if response.choices else None
                    usage = {
                        "input_tokens": getattr(response.usage, "prompt_tokens", None),
                        "output_tokens": getattr(response.usage, "completion_tokens", None),
                        "reasoning_tokens": _reasoning_token_count(response.usage),
                    }
                    raise LLMRequestError("Empty response from LLM", _request_usage(usage, request_plan, finish))
                raise ValueError("Empty response from LLM")

            reasoning = None
            msg = response.choices[0].message

            if hasattr(msg, "reasoning") and msg.reasoning:
                reasoning = msg.reasoning

            if reasoning is None and hasattr(msg, "reasoning_details") and msg.reasoning_details:
                reasoning_texts = []
                for detail in msg.reasoning_details:
                    if isinstance(detail, dict) and detail.get("type") == "reasoning.text":
                        text = detail.get("text", "")
                        if text:
                            reasoning_texts.append(text)
                if reasoning_texts:
                    reasoning = "\n".join(reasoning_texts)

            if reasoning is None and hasattr(msg, "model_extra") and msg.model_extra:
                extra = msg.model_extra
                if "reasoning" in extra and extra["reasoning"]:
                    reasoning = extra["reasoning"]
                elif "reasoning_details" in extra and extra["reasoning_details"]:
                    reasoning_texts = []
                    for detail in extra["reasoning_details"]:
                        if isinstance(detail, dict) and detail.get("type") == "reasoning.text":
                            text = detail.get("text", "")
                            if text:
                                reasoning_texts.append(text)
                    if reasoning_texts:
                        reasoning = "\n".join(reasoning_texts)

            if reasoning is None and hasattr(response, "usage"):
                reasoning_tokens = _reasoning_token_count(response.usage)

                if reasoning_tokens and reasoning_tokens > 0:
                    reasoning = f"[{reasoning_tokens} reasoning tokens used, but content encrypted by provider]"

            usage = None
            if hasattr(response, "usage"):
                reasoning_tokens = _reasoning_token_count(response.usage)

                usage = {
                    "input_tokens": getattr(response.usage, "prompt_tokens", None),
                    "output_tokens": getattr(response.usage, "completion_tokens", None),
                    "reasoning_tokens": reasoning_tokens
                }

            usage = _request_usage(usage, request_plan, getattr(response.choices[0], "finish_reason", None))
            if request_plan is not None:
                usage["response_model"] = getattr(response, "model", None)
                usage["response_id"] = getattr(response, "id", None)
            return {
                "content": response.choices[0].message.content,
                "reasoning": reasoning,
                "usage": usage
            }

        except RateLimitError as e:
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            if attempt < max_retries - 1:
                print(f"⚠️  Rate limit hit. Waiting {wait_time:.2f}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                continue
            print(f"❌ Rate limit error after {max_retries} attempts: {_public_error(e, request_plan)}")
            raise

        except APIConnectionError as e:
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            if attempt < max_retries - 1:
                print(f"⚠️  Connection error. Waiting {wait_time:.2f}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                continue
            print(f"❌ Connection error after {max_retries} attempts: {_public_error(e, request_plan)}")
            raise

        except APIError as e:
            if e.status_code and e.status_code >= 500:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                if attempt < max_retries - 1:
                    print(f"⚠️  Server error ({e.status_code}). Waiting {wait_time:.2f}s before retry {attempt + 1}/{max_retries}...")
                    time.sleep(wait_time)
                    continue
                print(f"❌ Server error after {max_retries} attempts: {_public_error(e, request_plan)}")
                raise
            print(f"❌ Client error ({e.status_code}): {_public_error(e, request_plan)}")
            raise

        except Exception as e:
            print(f"❌ Unexpected error in LLM call: {_public_error(e, request_plan)}")
            raise

    raise Exception(f"Failed to get LLM response after {max_retries} attempts")


def _supports_custom_temperature(provider, provider_model):
    if provider != "openai":
        return True
    # Direct OpenAI GPT-5 family Chat Completions currently accepts only the
    # default temperature, so omit the parameter rather than sending 0.8.
    return not provider_model.startswith("gpt-5")


def _supports_reasoning_effort(provider, provider_model):
    return provider == "openai" and provider_model.startswith("gpt-5")


def _direct_openai_reasoning_effort():
    return _env("OPENAI_REASONING_EFFORT") or "minimal"


def _anthropic_supports_temperature(provider_model):
    # Opus 4.7 and later reject explicit temperature; omit when calling them.
    if provider_model.startswith("claude-opus-4-7") or provider_model.startswith("claude-opus-4-8"):
        return False
    return True


def _call_anthropic(client, provider_model, temperature, messages, max_retries, request_plan=None):
    if anthropic is None:
        raise RuntimeError(
            "The anthropic package is not installed. Run: pip install -r requirements.txt"
        )

    max_tokens = request_plan.parameters["max_tokens"] if request_plan is not None else int(_env("ANTHROPIC_MAX_TOKENS") or "1024")
    system, chat_messages = _anthropic_messages(messages)

    for attempt in range(max_retries):
        try:
            request_params = {
                "model": provider_model,
                "messages": chat_messages,
                "max_tokens": max_tokens,
            }
            if _anthropic_supports_temperature(provider_model):
                request_params["temperature"] = temperature
            if system:
                request_params["system"] = system

            if request_plan is not None:
                request_params.pop("temperature", None)
                parameters = request_plan.parameters
                parameters.pop("max_tokens")
                request_params["extra_body"] = parameters
                # A large output ceiling makes the Anthropic SDK estimate that
                # a non-streaming call may exceed ten minutes and reject it
                # locally unless a timeout is explicit. This matches the
                # transport timeout exercised by the September 8 pilot; it
                # does not alter the provider request body or model condition.
                request_params["timeout"] = 1200.0

            response = client.messages.create(**request_params)
            content = _anthropic_text(response)
            usage = None
            if hasattr(response, "usage") and response.usage:
                usage = {
                    "input_tokens": getattr(response.usage, "input_tokens", None),
                    "output_tokens": getattr(response.usage, "output_tokens", None),
                    "reasoning_tokens": _reasoning_token_count(response.usage),
                }

            usage = _request_usage(usage, request_plan, getattr(response, "stop_reason", None))
            if request_plan is not None:
                usage["response_model"] = getattr(response, "model", None)
                usage["response_id"] = getattr(response, "id", None)
            if not content:
                if request_plan is not None:
                    raise LLMRequestError("Empty response from LLM", usage)
                raise ValueError("Empty response from LLM")
            return {
                "content": content,
                "reasoning": None,
                "usage": usage,
            }

        except Exception as e:
            if _should_retry_anthropic(e) and attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"⚠️  Anthropic API retryable error. Waiting {wait_time:.2f}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                continue
            print(f"❌ Anthropic API error: {_public_error(e, request_plan)}")
            raise

    raise Exception(f"Failed to get LLM response after {max_retries} attempts")


def _anthropic_text(response):
    texts = []
    for block in getattr(response, "content", []) or []:
        if isinstance(block, dict):
            if block.get("type") == "text" and block.get("text"):
                texts.append(block["text"])
        elif getattr(block, "type", None) == "text" and getattr(block, "text", None):
            texts.append(block.text)
    return "\n".join(texts).strip()


def _should_retry_anthropic(error):
    name = type(error).__name__
    status_code = getattr(error, "status_code", None)
    return (
        name in {"RateLimitError", "APIConnectionError", "APITimeoutError"}
        or (status_code is not None and status_code >= 500)
        # Stochastic refusals surface as empty content (no text blocks); at
        # nonzero temperature a retry usually succeeds, so don't kill the run.
        or (isinstance(error, ValueError) and "Empty response" in str(error))
    )


def _call_gemini(client, provider_model, temperature, messages, max_retries, request_plan=None):
    api_key = client["api_key"]
    base_url = client["base_url"].rstrip("/")
    system_instruction, contents = _gemini_messages(messages)
    if not contents:
        raise ValueError("No user/assistant messages available for Gemini call.")

    generation_config = {}
    if _gemini_supports_temperature(provider_model):
        generation_config["temperature"] = temperature
    payload = {
        "contents": contents,
        "generationConfig": generation_config,
    }
    if system_instruction:
        payload["system_instruction"] = system_instruction

    thinking_level = _env("GEMINI_THINKING_LEVEL")
    if thinking_level:
        payload["generationConfig"]["thinkingConfig"] = {"thinkingLevel": thinking_level}

    if request_plan is not None:
        payload["generationConfig"] = request_plan.parameters

    url = f"{base_url}/models/{provider_model}:generateContent"

    for attempt in range(max_retries):
        try:
            request = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": api_key,
                },
                method="POST",
            )
            with urllib.request.urlopen(
                request,
                timeout=_gemini_request_timeout_seconds(),
            ) as response:
                response_data = json.loads(response.read().decode("utf-8"))

            content = _gemini_text(response_data)
            candidates = response_data.get("candidates") or [{}]
            usage = _request_usage(_gemini_usage(response_data), request_plan, candidates[0].get("finishReason"))
            if request_plan is not None:
                block_reason = (response_data.get("promptFeedback") or {}).get("blockReason")
                usage["prompt_block_reason"] = block_reason
                if block_reason and block_reason != "BLOCK_REASON_UNSPECIFIED":
                    usage["outcome"] = "blocked"
            if not content:
                if request_plan is not None:
                    raise LLMRequestError("Empty response from Gemini", usage)
                raise ValueError(f"Empty response from Gemini: {_gemini_finish_reason(response_data)}")

            if request_plan is not None:
                usage["response_model"] = response_data.get("modelVersion")
                usage["response_id"] = response_data.get("responseId")
            return {
                "content": content,
                "reasoning": None,
                "usage": usage,
            }

        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            if _should_retry_gemini_http(e.code) and attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"⚠️  Gemini API retryable error ({e.code}). Waiting {wait_time:.2f}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                continue
            public_body = _redact_error_message(body) if request_plan is not None else _redact_gemini_error(body)
            print(f"❌ Gemini API error ({e.code}): {public_body}")
            if request_plan is not None:
                usage = _request_usage({}, request_plan, None)
                usage.update(outcome="error", error_type=type(e).__name__, status_code=e.code)
                raise LLMRequestError(f"Gemini API error ({e.code}): {public_body}", usage) from None
            raise

        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"⚠️  Gemini connection error. Waiting {wait_time:.2f}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                continue
            print(f"❌ Gemini connection error after {max_retries} attempts: {_public_error(e, request_plan)}")
            raise

    raise Exception(f"Failed to get Gemini response after {max_retries} attempts")


def _gemini_supports_temperature(provider_model):
    """Return whether the direct GenerateContent endpoint accepts temperature.

    The 3.6+ Flash line accepts temperature but ignores it (probe 2026-09-04:
    gemini-3.6-flash returned 5/5 distinct outputs at temperature 0), so we
    omit it there and record temperature_sent=false. Keep the historical
    parameter for earlier models so existing experiments remain unchanged.
    """
    return provider_model not in _GEMINI_TEMPERATURE_IGNORED


_GEMINI_TEMPERATURE_IGNORED = frozenset({"gemini-3.6-flash", "gemini-3.7-flash"})


def _gemini_request_timeout_seconds():
    raw_value = _env("GEMINI_REQUEST_TIMEOUT_SECONDS")
    if not raw_value:
        return 120.0
    try:
        timeout = float(raw_value)
    except ValueError as error:
        raise RuntimeError(
            "GEMINI_REQUEST_TIMEOUT_SECONDS must be a positive number"
        ) from error
    if not math.isfinite(timeout) or timeout <= 0:
        raise RuntimeError(
            "GEMINI_REQUEST_TIMEOUT_SECONDS must be a positive number"
        )
    return timeout


def _gemini_text(response_data):
    texts = []
    for candidate in response_data.get("candidates", []) or []:
        for part in (candidate.get("content") or {}).get("parts", []) or []:
            text = part.get("text")
            if text:
                texts.append(text)
    return "\n".join(texts).strip()


def _gemini_finish_reason(response_data):
    reasons = []
    for candidate in response_data.get("candidates", []) or []:
        reason = candidate.get("finishReason")
        if reason:
            reasons.append(reason)
    prompt_feedback = response_data.get("promptFeedback")
    if prompt_feedback:
        reasons.append(f"promptFeedback={prompt_feedback}")
    return ", ".join(reasons) or "unknown finish reason"


def _gemini_usage(response_data):
    usage = response_data.get("usageMetadata")
    if not usage:
        return None
    return {
        "input_tokens": usage.get("promptTokenCount"),
        "output_tokens": usage.get("candidatesTokenCount"),
        "reasoning_tokens": usage.get("thoughtsTokenCount"),
    }


class LLMRequestError(ValueError):
    """A provider failure with a non-secret request/outcome record."""

    def __init__(self, message, usage):
        super().__init__(message)
        self.usage = usage


def _public_error(error, request_plan):
    if request_plan is None:
        return str(error)
    return f"{type(error).__name__}: {_redact_error_message(str(error))}"


def _redact_error_message(message):
    # Preserve rejected parameter names and vendor explanations, never credentials.
    secrets = {
        value for name, value in os.environ.items()
        if value and name.upper().endswith(("_API_KEY", "_TOKEN", "_SECRET", "_PASSWORD"))
    }
    secrets.update(filter(None, (
        OPENROUTER_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY,
        GEMINI_API_KEY, TOGETHER_API_KEY,
    )))
    for secret in sorted(secrets, key=len, reverse=True):
        message = message.replace(secret, "[REDACTED]")
    message = re.sub(
        r"(?i)(\b(?:authorization|x-api-key|x-goog-api-key|api[_-]?key|access[_-]?token|key)"
        r"[\"']?\s*[:=]\s*[\"']?)(?:Bearer\s+)?[^\s\"',;&}\]]+",
        r"\1[REDACTED]", message,
    )
    message = re.sub(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]+=*", "Bearer [REDACTED]", message)
    message = re.sub(r"\b(?:sk-[A-Za-z0-9_-]+|hf_[A-Za-z0-9]+|AIza[A-Za-z0-9_-]+)\b", "[REDACTED]", message)
    return message


def _reasoning_token_count(usage):
    def value(record, key):
        return record.get(key) if isinstance(record, dict) else getattr(record, key, None)

    for key in ("reasoning_tokens", "thinking_tokens"):
        count = value(usage, key)
        if count is not None:
            return count
    for key in ("completion_tokens_details", "output_tokens_details"):
        for token_key in ("reasoning_tokens", "thinking_tokens"):
            count = value(value(usage, key), token_key)
            if count is not None:
                return count
    return None


def _request_usage(usage, request_plan, finish_reason):
    if request_plan is None:
        return usage
    outcome = "unknown"
    if finish_reason in {"stop", "end_turn", "stop_sequence", "STOP"}:
        outcome = "complete"
    elif finish_reason in {"length", "max_tokens", "MAX_TOKENS"}:
        outcome = "truncated"
    elif finish_reason in {"content_filter", "refusal", "SAFETY", "RECITATION", "BLOCKLIST", "PROHIBITED_CONTENT"}:
        outcome = "blocked"
    result = {"input_tokens": None, "output_tokens": None, "reasoning_tokens": None, **(usage or {})}
    result.update(request_settings=request_plan.as_dict(), finish_reason=finish_reason, outcome=outcome)
    return result


def _should_retry_gemini_http(status_code):
    return status_code in {408, 409, 429} or status_code >= 500


def _redact_gemini_error(body):
    return re.sub(r"(AIza|AIzaSy)[A-Za-z0-9_\\-]+", "[redacted-google-api-key]", body)


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
    if num_agents == 2:
        print("Role swapping: ENABLED (agents alternate roles each round)")
    else:
        print("Pairing mode: FULL-POOL RANDOM DYADS (role repeats allowed)")
    print("-" * 80)
