"""Explicit request policies; native reasoning parameters are not cross-vendor scores."""

import json
import math
from dataclasses import dataclass


class LLMSettingsError(ValueError):
    """A guarded request is missing or contradicts its declared policy."""


REQUIRED_FIELDS = {"provider", "reasoning", "temperature", "max_output_tokens"}
REASONING_FIELDS = {
    "openai": {"reasoning_effort"},
    "anthropic": {"thinking", "output_config"},
    "google": {"thinkingConfig"},
    "openrouter": {"reasoning"},
}
ENDPOINTS = {
    "openai": "https://api.openai.com/v1",
    "anthropic": "https://api.anthropic.com",
    "google": "https://generativelanguage.googleapis.com/v1beta",
    "openrouter": "https://openrouter.ai/api/v1",
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def positive_integer(value, field):
    if type(value) is not int or value <= 0:
        raise LLMSettingsError(f"{field} must be a positive integer")
    return value


def validate_settings(block):
    if not isinstance(block, dict) or set(block) != REQUIRED_FIELDS:
        raise LLMSettingsError(
            "llm_settings must contain exactly provider, reasoning, temperature, "
            "and max_output_tokens; use explicit policies rather than environment defaults"
        )
    if not isinstance(block["provider"], str) or block["provider"] not in {*ENDPOINTS, "direct"}:
        raise LLMSettingsError("llm_settings.provider must name a provider or 'direct', never 'auto'")
    if not isinstance(block["reasoning"], dict) or not block["reasoning"]:
        raise LLMSettingsError("reasoning must contain explicit provider-native parameters")
    temperature = block["temperature"]
    if temperature != "default" and (
        type(temperature) not in (int, float)
        or not math.isfinite(temperature)
        or not 0 <= temperature <= 2
    ):
        raise LLMSettingsError("temperature must be 'default' (omit) or a finite number in [0, 2]")
    if block["max_output_tokens"] != "default":
        positive_integer(block["max_output_tokens"], "max_output_tokens")
    canonical(block)
    return block


def validate_reasoning(provider, reasoning):
    if set(reasoning) - REASONING_FIELDS[provider]:
        raise LLMSettingsError(f"Unexpected reasoning parameter for {provider}")
    if provider == "openai":
        if reasoning.get("reasoning_effort") not in {"none", "minimal", "low", "medium", "high", "xhigh", "max"}:
            raise LLMSettingsError("Invalid OpenAI reasoning_effort")
    elif provider == "anthropic":
        thinking = reasoning.get("thinking")
        if not isinstance(thinking, dict) or thinking.get("type") not in {"disabled", "enabled", "adaptive"}:
            raise LLMSettingsError("Anthropic thinking.type must be explicit")
        expected = {"type", "budget_tokens"} if thinking["type"] == "enabled" else {"type"}
        if set(thinking) != expected:
            raise LLMSettingsError("Unexpected or missing Anthropic thinking fields")
        if thinking["type"] == "enabled":
            positive_integer(thinking["budget_tokens"], "thinking.budget_tokens")
        output = reasoning.get("output_config")
        if output is not None and (
            not isinstance(output, dict) or set(output) != {"effort"}
            or output["effort"] not in {"low", "medium", "high", "max"}
        ):
            raise LLMSettingsError("Only an explicit output_config.effort is supported")
    elif provider == "google":
        thinking = reasoning.get("thinkingConfig")
        if not isinstance(thinking, dict) or set(thinking) not in ({"thinkingLevel"}, {"thinkingBudget"}):
            raise LLMSettingsError("Gemini needs exactly thinkingLevel or thinkingBudget")
        if "thinkingLevel" in thinking and thinking["thinkingLevel"] not in {"minimal", "low", "medium", "high"}:
            raise LLMSettingsError("Invalid Gemini thinkingLevel")
        if "thinkingBudget" in thinking and (type(thinking["thinkingBudget"]) is not int or thinking["thinkingBudget"] < -1):
            raise LLMSettingsError("Gemini thinkingBudget must be an integer >= -1")
    else:
        thinking = reasoning.get("reasoning")
        if not isinstance(thinking, dict) or set(thinking) not in ({"enabled"}, {"effort"}, {"max_tokens"}):
            raise LLMSettingsError("OpenRouter needs exactly enabled, effort, or max_tokens")
        if "enabled" in thinking and type(thinking["enabled"]) is not bool:
            raise LLMSettingsError("OpenRouter reasoning.enabled must be boolean")
        if "effort" in thinking and thinking["effort"] not in {"none", "minimal", "low", "medium", "high", "xhigh"}:
            raise LLMSettingsError("Invalid OpenRouter reasoning.effort")
        if "max_tokens" in thinking:
            positive_integer(thinking["max_tokens"], "reasoning.max_tokens")


@dataclass(frozen=True)
class RequestPlan:
    """Immutable JSON keeps nested settings stable across agents and worker processes."""

    encoded: str

    def as_dict(self):
        return json.loads(self.encoded)

    @property
    def provider(self):
        return self.as_dict()["provider"]

    @property
    def provider_model(self):
        return self.as_dict()["provider_model"]

    @property
    def parameters(self):
        return self.as_dict()["parameters"]


def resolve_request_plan(model, block, aliases):
    validate_settings(block)
    vendor = model.split("/", 1)[0]
    provider = vendor if block["provider"] == "direct" else block["provider"]
    if provider not in ENDPOINTS or (provider != "openrouter" and provider != vendor):
        raise LLMSettingsError(f"Configured provider does not match model {model!r}")
    validate_reasoning(provider, block["reasoning"])
    native_model = model if provider == "openrouter" else aliases.get(model, model.split("/", 1)[-1])
    parameters = json.loads(canonical(block["reasoning"]))
    if block["temperature"] != "default":
        if provider == "anthropic" and block["temperature"] > 1:
            raise LLMSettingsError("Anthropic temperature must be in [0, 1]")
        parameters["temperature"] = block["temperature"]
    cap = block["max_output_tokens"]
    if provider == "anthropic" and cap == "default":
        raise LLMSettingsError("Anthropic requires an explicit positive max_output_tokens")
    if cap != "default":
        cap_key = {"google": "maxOutputTokens", "openai": "max_completion_tokens"}.get(provider, "max_tokens")
        parameters[cap_key] = cap
    if provider == "anthropic":
        budget = parameters["thinking"].get("budget_tokens")
        if budget is not None and budget >= cap:
            raise LLMSettingsError("Anthropic thinking budget must be below the output cap")
    if provider == "openrouter":
        parameters["provider"] = {"require_parameters": True}
    return RequestPlan(canonical({
        "version": 1,
        "model": model,
        "provider": provider,
        "provider_model": native_model,
        "endpoint": ENDPOINTS[provider],
        "policy": block,
        "parameters": parameters,
    }))


def prepare_combinations(combinations, experiment_set, aliases, *, allow_legacy=False):
    block = experiment_set.get("llm_settings")
    if block is None and not allow_legacy:
        raise LLMSettingsError("Experiment has no llm_settings; pin it or explicitly use --allow-legacy-settings")
    displayed = set()
    for combination in combinations:
        combination["request_plan"] = resolve_request_plan(combination["model"], block, aliases) if block is not None else None
        combination["comparison_inputs"] = comparison_inputs(combination)
        plan = combination["request_plan"]
        if plan is not None and plan.encoded not in displayed:
            print("PINNED REQUEST: " + plan.encoded)
            displayed.add(plan.encoded)
    if block is None:
        print("LEGACY SETTINGS: environment-dependent requests; no strict provenance guarantee")
    return combinations


def prepared_plan(combination):
    if "request_plan" not in combination:
        raise LLMSettingsError("Unprepared combination: use a guarded runner or prepare_combinations with explicit legacy acknowledgement")
    plan = combination["request_plan"]
    if plan is not None and combination.get("comparison_inputs") != comparison_inputs(combination):
        raise LLMSettingsError("Combination changed after request planning")
    return plan


def comparison_inputs(combination):
    excluded = {
        "request_plan", "comparison_inputs", "execution_provenance", "output_dir",
        "template_name", "persona_key", "system_addition_key", "game_params_name",
        "game_prompt_addition_id", "initial_system_template_name", "myth_default_prompt_key",
        "myth_later_prompt_key", "myth_prompt_arm_id", "myth_prompt_template_names",
        "myth_topic_id", "round_prompt_template_names", "run_number",
    }
    result = {key: value for key, value in combination.items() if key not in excluded}
    plan = combination.get("request_plan")
    result["llm_request"] = plan.as_dict() if plan is not None else None
    return json.loads(canonical(result))
