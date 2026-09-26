"""Caches in the linguistic analysis must not reuse stale or unparseable entries."""
import json
import sys
import types
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from analyses import myth_moral_judge  # noqa: E402
from analyses._shared import cached_embeddings  # noqa: E402


def test_embedding_cache_is_invalidated_when_texts_change(tmp_path, monkeypatch):
    calls = []

    class FakeModel:
        def __init__(self, name):
            pass

        def encode(self, texts, **kwargs):
            calls.append(list(texts))
            return np.array([[float(len(t))] for t in texts])

    monkeypatch.setitem(sys.modules, "sentence_transformers", types.SimpleNamespace(SentenceTransformer=FakeModel))
    cache = tmp_path / "emb.npy"
    first = cached_embeddings(cache, ["a", "bb"])
    again = cached_embeddings(cache, ["a", "bb"])
    changed = cached_embeddings(cache, ["ccc", "a"])  # same row count, different texts
    assert len(calls) == 2
    assert np.array_equal(first, again)
    assert changed.tolist() == [[3.0], [1.0]]


def test_judge_does_not_cache_or_reuse_invalid_replies(tmp_path, monkeypatch):
    replies = iter(["", '{"label": "be fair"}'])

    def create(**kwargs):
        message = types.SimpleNamespace(content=next(replies))
        return types.SimpleNamespace(choices=[types.SimpleNamespace(message=message)], usage=None, model="m")

    judge = myth_moral_judge.Judge.__new__(myth_moral_judge.Judge)
    judge.client = types.SimpleNamespace(chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=create)))
    judge.model, judge.reasoning_off, judge.cache = "m", True, tmp_path
    valid = lambda raw: myth_moral_judge.parse("label", raw)[1] == "ok"  # noqa: E731

    assert judge("prompt", valid)["raw"] == ""
    assert not judge.cache_path("prompt").exists()
    assert judge("prompt", valid)["raw"] == '{"label": "be fair"}'
    assert json.loads(judge.cache_path("prompt").read_text())["raw"] == '{"label": "be fair"}'
    assert judge("prompt", valid)["cached"] is True

    judge.cache_path("prompt").write_text(json.dumps({"raw": "not json"}))  # a bad entry from an older run
    replies = iter(['{"label": "be generous"}'])
    assert judge("prompt", valid)["raw"] == '{"label": "be generous"}'
