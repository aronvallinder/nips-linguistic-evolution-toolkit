"""Acceptance checks capture HTTP bodies, not only permissive SDK mocks."""

import importlib
import json
from unittest.mock import patch

import httpx
import pytest
from openai import OpenAI

from src.agents import Agent
from src.llm_settings import LLMSettingsError, prepare_combinations, prepared_plan, resolve_request_plan
from src.utils import DIRECT_MODEL_ALIASES, LLMClient, call_llm, create_llm_client, llm_runtime_metadata


def settings(provider="direct", reasoning=None, temperature="default", cap=128):
    return {
        "provider": provider,
        "reasoning": reasoning or {"reasoning_effort": "low"},
        "temperature": temperature,
        "max_output_tokens": cap,
    }


def plan_for(model="openai/gpt-5-nano", **kwargs):
    return resolve_request_plan(model, settings(**kwargs), DIRECT_MODEL_ALIASES)


def openai_response(finish="stop", details=None):
    usage = {"prompt_tokens": 3, "completion_tokens": 4, "total_tokens": 7}
    if details is not None:
        usage["completion_tokens_details"] = details
    return {
        "id": "test-response", "object": "chat.completion", "created": 0,
        "model": "test-returned-model",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": '{"send": 3}'}, "finish_reason": finish}],
        "usage": usage,
    }


def mocked_openai(plan, captured, response=None, status=200):
    def transport(request):
        captured.append(json.loads(request.content))
        return httpx.Response(status, json=response if response is not None else openai_response())

    native = OpenAI(api_key="test-key", base_url=plan.as_dict()["endpoint"], max_retries=0, http_client=httpx.Client(transport=httpx.MockTransport(transport)))
    client = LLMClient(plan.provider, native)
    client.request_plan = plan
    return client


def test_missing_policy_fails_before_any_call():
    with pytest.raises(LLMSettingsError, match="no llm_settings"):
        prepare_combinations([{"model": "openai/gpt-5-nano"}], {}, DIRECT_MODEL_ALIASES)


def test_worker_rejects_inputs_changed_after_planning():
    combinations = [{"model": "openai/gpt-5-nano", "template": "rules"}]
    prepare_combinations(combinations, {"llm_settings": settings()}, DIRECT_MODEL_ALIASES)
    combinations[0]["template"] = "different rules"
    with pytest.raises(LLMSettingsError, match="changed"):
        prepared_plan(combinations[0])


def test_endpoint_drift_fails_before_http():
    captured = []
    client = mocked_openai(plan_for(), captured)
    client.client.base_url = "https://wrong.invalid"
    with pytest.raises(ValueError, match="Endpoint changed"):
        call_llm(client, "openai/gpt-5-nano", 0.8, [])
    assert not captured


@pytest.mark.parametrize("field", ["provider", "reasoning", "temperature", "max_output_tokens"])
def test_every_policy_field_is_required(field):
    block = settings()
    block.pop(field)
    with pytest.raises(LLMSettingsError):
        resolve_request_plan("openai/gpt-5-nano", block, {})


@pytest.mark.parametrize("cap", [0, -1, True, 1.5])
def test_invalid_cap_is_rejected(cap):
    with pytest.raises(LLMSettingsError):
        plan_for(cap=cap)


def test_nested_policy_cannot_mutate_frozen_plan():
    block = settings()
    plan = resolve_request_plan("openai/gpt-5-nano", block, {})
    block["reasoning"]["reasoning_effort"] = "high"
    exported = plan.as_dict()
    exported["parameters"]["reasoning_effort"] = "high"
    assert plan.parameters["reasoning_effort"] == "low"


def test_environment_does_not_choose_the_request_or_native_model():
    plan = plan_for()
    captured = []
    client = mocked_openai(plan, captured)
    with patch.dict("os.environ", {
        "LLM_PROVIDER": "openrouter", "OPENAI_REASONING_EFFORT": "high",
        "LLM_DIRECT_MODEL_OPENAI_GPT_5_NANO": "different-model",
        "LLM_TEMPERATURE": "0.2", "LLM_REASONING": "high",
    }):
        result = call_llm(client, "openai/gpt-5-nano", 0.8, [{"role": "user", "content": "decision"}])
        metadata = llm_runtime_metadata(client, "openai/gpt-5-nano")
    assert captured[0] == {"model": plan.provider_model, "messages": [{"role": "user", "content": "decision"}], **plan.parameters}
    assert result["usage"]["request_settings"] == metadata["llm_request"] == plan.as_dict()
    assert "temperature" not in captured[0]
    assert captured[0]["max_completion_tokens"] == 128


def test_missing_pinned_credentials_do_not_fall_back():
    with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-router-key"}, clear=True):
        with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
            create_llm_client("openai/gpt-5-nano", request_plan=plan_for())


def test_pinned_endpoint_ignores_sdk_base_url_environment():
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key", "OPENAI_BASE_URL": "https://wrong.invalid"}, clear=True):
        client = create_llm_client("openai/gpt-5-nano", request_plan=plan_for())
        assert str(client.client.base_url) == "https://api.openai.com/v1/"
        client.client.close()


@pytest.mark.parametrize("details,expected", [(None, None), ({"reasoning_tokens": 0}, 0), ({"reasoning_tokens": 17}, 17)])
def test_unknown_reasoning_usage_is_not_zero(details, expected):
    client = mocked_openai(plan_for(), [], openai_response(details=details))
    response = call_llm(client, "openai/gpt-5-nano", 0.8, [])
    assert response["usage"]["reasoning_tokens"] == expected


@pytest.mark.parametrize("finish,outcome", [("stop", "complete"), ("length", "truncated"), ("content_filter", "blocked")])
def test_finish_status_is_recorded(finish, outcome):
    client = mocked_openai(plan_for(), [], openai_response(finish=finish))
    response = call_llm(client, "openai/gpt-5-nano", 0.8, [])
    assert response["usage"]["finish_reason"] == finish
    assert response["usage"]["outcome"] == outcome


def test_provider_error_stays_in_agent_audit_without_secret_body(capsys):
    plan = plan_for()
    client = mocked_openai(plan, [], {"error": {"message": "secret-must-not-appear", "type": "invalid_request_error", "code": "bad_parameter"}}, status=400)
    agent = Agent("test-agent", "openai/gpt-5-nano", 0.8, client, 10, None)
    with pytest.raises(ValueError, match="BadRequestError"):
        agent.respond("decision")
    event = agent.interaction_history[-1]
    assert event["response"]["usage"]["request_settings"] == plan.as_dict()
    assert event["response"]["usage"]["outcome"] == "error"
    assert not agent.messages
    assert "secret-must-not-appear" not in json.dumps(event) + capsys.readouterr().out


def test_empty_response_retains_known_usage_and_truncation():
    response = openai_response(finish="length", details={"reasoning_tokens": 4})
    response["choices"][0]["message"]["content"] = None
    client = mocked_openai(plan_for(), [], response)
    with pytest.raises(ValueError, match="Empty response") as failure:
        call_llm(client, "openai/gpt-5-nano", 0.8, [])
    assert failure.value.usage["output_tokens"] == 4
    assert failure.value.usage["reasoning_tokens"] == 4
    assert failure.value.usage["outcome"] == "truncated"


def test_openrouter_request_and_record_agree():
    plan = plan_for(provider="openrouter", reasoning={"reasoning": {"enabled": False}})
    captured = []
    client = mocked_openai(plan, captured)
    result = call_llm(client, "openai/gpt-5-nano", 0.8, [])
    assert captured[0] == {"model": "openai/gpt-5-nano", "messages": [], **plan.parameters}
    assert captured[0]["provider"] == {"require_parameters": True}
    assert result["usage"]["request_settings"]["parameters"] == plan.parameters


def test_anthropic_actual_sdk_request_and_record_agree():
    import anthropic

    transport_module = next(
        base.__module__.split(".")[0]
        for base in anthropic.DefaultHttpxClient.__mro__
        if base.__name__ == "Client"
    )
    provider_http = importlib.import_module(transport_module)
    model = "anthropic/claude-sonnet-4.5"
    plan = plan_for(model, reasoning={"thinking": {"type": "disabled"}})
    captured = []

    def transport(request):
        captured.append(json.loads(request.content))
        return provider_http.Response(200, json={
            "id": "test-message", "type": "message", "role": "assistant", "model": plan.provider_model,
            "content": [{"type": "text", "text": '{"send": 3}'}], "stop_reason": "end_turn",
            "usage": {"input_tokens": 3, "output_tokens": 4},
        })

    native = anthropic.Anthropic(api_key="test-key", max_retries=0, http_client=provider_http.Client(transport=provider_http.MockTransport(transport)))
    client = LLMClient("anthropic", native)
    client.request_plan = plan
    messages = [{"role": "system", "content": "rules"}, {"role": "user", "content": "decision"}]
    with patch.dict("os.environ", {"ANTHROPIC_MAX_TOKENS": "1"}):
        response = call_llm(client, model, 0.8, messages)
    assert captured[0] == {"model": plan.provider_model, "system": "rules", "messages": messages[1:], **plan.parameters}
    assert response["usage"]["reasoning_tokens"] is None
    assert response["usage"]["request_settings"] == plan.as_dict()


def test_google_request_and_record_agree():
    model = "google/gemini-2.5-flash"
    plan = plan_for(model, reasoning={"thinkingConfig": {"thinkingBudget": 0}})
    client = LLMClient("google", {"api_key": "test-key", "base_url": plan.as_dict()["endpoint"]})
    client.request_plan = plan
    captured = []

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps({"candidates": [{"content": {"parts": [{"text": '{"send": 3}'}]}, "finishReason": "STOP"}], "usageMetadata": {"promptTokenCount": 3}}).encode()

    def transport(request, **kwargs):
        captured.append(json.loads(request.data))
        return Response()

    with patch("src.utils.urllib.request.urlopen", side_effect=transport), patch.dict("os.environ", {"GEMINI_THINKING_LEVEL": "high"}):
        response = call_llm(client, model, 0.8, [{"role": "user", "content": "decision"}])
    assert captured[0]["generationConfig"] == plan.parameters
    assert response["usage"]["request_settings"] == plan.as_dict()
    assert response["usage"]["reasoning_tokens"] is None
    assert response["usage"]["prompt_block_reason"] is None
    assert response["usage"]["outcome"] == "complete"


@pytest.mark.parametrize("block_reason,outcome", [("SAFETY", "blocked"), ("OTHER", "blocked"), (None, "unknown"), ("BLOCK_REASON_UNSPECIFIED", "unknown")])
def test_google_prompt_block_is_preserved_in_agent_audit(block_reason, outcome):
    model = "google/gemini-2.5-flash"
    plan = plan_for(model, reasoning={"thinkingConfig": {"thinkingBudget": 0}})
    client = LLMClient("google", {"api_key": "test-key", "base_url": plan.as_dict()["endpoint"]})
    client.request_plan = plan
    payload = {"usageMetadata": {"promptTokenCount": 3}}
    if block_reason is not None:
        payload["promptFeedback"] = {"blockReason": block_reason}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps(payload).encode()

    agent = Agent("test-agent", model, 0.8, client, 10, None)
    with patch("src.utils.urllib.request.urlopen", return_value=Response()) as transport:
        with pytest.raises(ValueError, match="Empty response from Gemini"):
            agent.respond("decision")
    transport.assert_called_once()
    assert not agent.messages
    assert len(agent.interaction_history) == 1
    usage = agent.interaction_history[0]["response"]["usage"]
    assert usage["request_settings"] == plan.as_dict()
    assert usage["prompt_block_reason"] == block_reason
    assert usage["finish_reason"] is None
    assert usage["outcome"] == outcome
    assert usage["input_tokens"] == 3
    assert usage["output_tokens"] is None
    assert usage["reasoning_tokens"] is None
