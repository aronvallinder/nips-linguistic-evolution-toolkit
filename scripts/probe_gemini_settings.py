#!/usr/bin/env python3
"""Probe how a Gemini model treats temperature and thinking_level on the direct API.

Sends the trust game's round-1 investor prompt a few times and reports, per
call, the HTTP status, finishReason, thoughtsTokenCount and the parsed
decision. Use it before pinning a Gemini arm in a matched-reasoning design,
e.g. to confirm that ``thinking_level=minimal`` really yields zero thought
tokens on the game prompt and that the model accepts (or ignores) temperature.

Requires GEMINI_API_KEY (or GOOGLE_API_KEY) in the environment / .env.
Cost: a handful of ~300-token calls (well under a cent).

Usage (from repo root):
  python scripts/probe_gemini_settings.py                       # gemini-3.6-flash
  python scripts/probe_gemini_settings.py --model gemini-3.7-flash --n 3
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.experiment_config import ExperimentConfig  # noqa: E402
from src.utils import GEMINI_API_BASE_URL, _gemini_usage  # noqa: E402

SYSTEM_KEY = "trust_game_default"
ROUND1_KEY = "trust_game_round1_investor"
CONFIG_PATH = os.path.join(REPO_ROOT, "config", "experiments.yaml")


def _prompts():
    cfg = ExperimentConfig(CONFIG_PATH)
    templates = cfg.config["prompt_templates"]
    system = templates[SYSTEM_KEY].format(endowment=5, multiplier=3)
    user = templates[ROUND1_KEY].format(endowment=5)
    return system, user


def _call(model, api_key, system, user, temperature, thinking_level, timeout):
    generation_config = {}
    if temperature is not None:
        generation_config["temperature"] = temperature
    if thinking_level:
        generation_config["thinkingConfig"] = {"thinkingLevel": thinking_level}
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": generation_config,
    }
    request = urllib.request.Request(
        f"{GEMINI_API_BASE_URL}/models/{model}:generateContent",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"http": e.code, "error": body[:300]}
    candidate = (data.get("candidates") or [{}])[0]
    text = "".join(
        part.get("text", "")
        for part in candidate.get("content", {}).get("parts", [])
        if not part.get("thought")
    )
    return {
        "http": 200,
        "finish": candidate.get("finishReason"),
        "usage": _gemini_usage(data),
        "text": text.strip()[:120],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--model", default="gemini-3.6-flash")
    parser.add_argument("--n", type=int, default=2, help="calls per setting")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        sys.exit("GEMINI_API_KEY (or GOOGLE_API_KEY) is not set; nothing probed.")

    system, user = _prompts()
    settings = [
        ("temp=0.8, thinking=minimal", 0.8, "minimal"),
        ("no temp,  thinking=minimal", None, "minimal"),
        ("temp=0.8, thinking=low", 0.8, "low"),
        ("temp=0.8, thinking=default", 0.8, None),
    ]
    print(f"MODEL={args.model} N={args.n} per setting  EST_COST<$0.01")
    for label, temperature, level in settings:
        for i in range(args.n):
            r = _call(args.model, api_key, system, user, temperature, level, args.timeout)
            if r["http"] != 200:
                print(f"{label:28s} #{i}: HTTP {r['http']}  {r['error']}")
                continue
            u = r["usage"]
            print(
                f"{label:28s} #{i}: finish={r['finish']} "
                f"out={u.get('output_tokens')} thought={u.get('reasoning_tokens')} "
                f"| {r['text']}"
            )


if __name__ == "__main__":
    main()
