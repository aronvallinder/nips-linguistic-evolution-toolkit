"""Reusable Together AI backed LLM judge interface."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Optional, Sequence, Tuple

from pydantic import BaseModel


DEFAULT_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
# DEFAULT_MODEL = "google/gemma-4-31B-it"


class JudgeResult(BaseModel):
    """Structured result for one judged text."""

    index: int
    raw_response: str
    judgment: Any = None
    parse_status: str = "ok"
    parse_error: Optional[str] = None
    model: Optional[str] = None
    usage: Optional[Mapping[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


@dataclass(frozen=True)
class _PendingResult:
    index: int
    text: str


@dataclass
class LLMJudge:
    """Judge plain strings with a reusable prompt through Together AI.

    The prompt may include ``{text}``; when omitted, the text is appended after
    the prompt under an ``Input text:`` label.
    """

    prompt: str
    model: str = DEFAULT_MODEL
    temperature: float = 0.0
    # max_tokens: int = 1024
    client: Optional[Any] = None
    response_format: Optional[Mapping[str, Any]] = field(default_factory=lambda: {"type": "json_object"})
    system_prompt: Optional[str] = (
        "You are an impartial LLM-as-judge. Return only valid JSON unless the "
        "user explicitly requests another format."
    )

    def __post_init__(self) -> None:
        if self.client is None:
            try:
                from together import Together
            except ImportError as exc:
                raise RuntimeError(
                    "The Together AI SDK is not installed. Install with "
                    "`pip install together` or `pip install -e .`."
                ) from exc
            self.client = Together()

    def render_prompt(self, text: str) -> str:
        if "{text}" in self.prompt:
            return self.prompt.replace("{text}", text)
        return f"{self.prompt.rstrip()}\n\nInput text:\n{text}"

    def evaluate(self, text: str) -> JudgeResult:
        """Judge one text using the same implementation as batched judging."""

        return self.evaluate_many([text])[0]

    def evaluate_many(
        self,
        texts: Sequence[str],
        *,
        batch_size: int = 8,
        max_workers: int = 4,
    ) -> list[JudgeResult]:
        """Judge many texts concurrently while preserving input order."""

        if batch_size < 1:
            raise ValueError("batch_size must be at least 1")
        if max_workers < 1:
            raise ValueError("max_workers must be at least 1")

        pending = [_PendingResult(index=index, text=text) for index, text in enumerate(texts)]
        if not pending:
            return []

        results: list[Optional[JudgeResult]] = [None] * len(pending)
        chunks = list(_chunked(pending, batch_size))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_chunk = {
                executor.submit(self._evaluate_chunk, chunk): chunk for chunk in chunks
            }
            for future in as_completed(future_to_chunk):
                for result in future.result():
                    results[result.index] = result

        return [result for result in results if result is not None]

    def _evaluate_chunk(self, chunk: Sequence[_PendingResult]) -> list[JudgeResult]:
        return [self._evaluate_one(item.index, item.text) for item in chunk]

    def _evaluate_one(self, index: int, text: str) -> JudgeResult:
        rendered = self.render_prompt(text)
        messages: list[dict[str, str]] = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": rendered})

        request: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            # "max_tokens": self.max_tokens,
        }
        if self.response_format is not None:
            request["response_format"] = self.response_format

        response = self.client.chat.completions.create(**request)
        raw_response = _extract_content(response)
        parsed, parse_status, parse_error = _parse_json(raw_response)

        return JudgeResult(
            index=index,
            raw_response=raw_response,
            judgment=parsed,
            parse_status=parse_status,
            parse_error=parse_error,
            model=getattr(response, "model", self.model),
            usage=_usage_to_dict(getattr(response, "usage", None)),
        )


def _chunked(items: Sequence[_PendingResult], size: int) -> Iterable[Sequence[_PendingResult]]:
    for start in range(0, len(items), size):
        yield items[start : start + size]


def _extract_content(response: Any) -> str:
    choices = getattr(response, "choices", None)
    if not choices:
        return ""
    first = choices[0]
    message = getattr(first, "message", None)
    if message is not None:
        content = getattr(message, "content", None)
        if content is not None:
            return str(content)
    text = getattr(first, "text", None)
    return "" if text is None else str(text)


def _parse_json(raw_response: str) -> Tuple[Any, str, Optional[str]]:
    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        return None, "parse_error", str(exc)
    return parsed, "ok", None


def _usage_to_dict(usage: Any) -> Optional[dict[str, Any]]:
    if usage is None:
        return None
    if isinstance(usage, Mapping):
        return dict(usage)
    if hasattr(usage, "model_dump"):
        return usage.model_dump()
    if hasattr(usage, "dict"):
        return usage.dict()
    values = {
        key: getattr(usage, key)
        for key in ("prompt_tokens", "completion_tokens", "total_tokens")
        if hasattr(usage, key)
    }
    return values or None
