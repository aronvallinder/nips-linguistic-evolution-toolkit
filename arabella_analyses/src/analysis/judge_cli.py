"""Command-line helpers for running an LLM judge over local text files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Optional, Sequence, Union

from analysis.judge import DEFAULT_MODEL, LLMJudge, JudgeResult


def read_texts(path: Union[str, Path], *, jsonl_text_field: str = "text") -> list[str]:
    """Read input texts from a .txt file or JSONL file with a text field."""

    input_path = Path(path)
    if input_path.suffix.lower() == ".jsonl":
        texts: list[str] = []
        with input_path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    row = json.loads(stripped)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSONL at {input_path}:{line_number}: {exc}") from exc
                if jsonl_text_field not in row:
                    raise ValueError(
                        f"Missing field {jsonl_text_field!r} at {input_path}:{line_number}"
                    )
                texts.append(str(row[jsonl_text_field]))
        return texts

    return [input_path.read_text(encoding="utf-8")]


def write_results(path: Union[str, Path], results: Iterable[JudgeResult]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Judge plain texts with Together AI.")
    parser.add_argument("--input", required=True, help="Path to a .txt file or JSONL file.")
    parser.add_argument("--output", required=True, help="Path to write JSONL judgment results.")
    parser.add_argument("--prompt", help="Judge prompt. Use {text} to place each input.")
    parser.add_argument("--prompt-file", help="Path to a file containing the judge prompt.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--jsonl-text-field", default="text")
    parser.add_argument(
        "--no-json-mode",
        action="store_true",
        help="Do not request JSON output from Together; raw responses are still saved.",
    )
    args = parser.parse_args(argv)

    if bool(args.prompt) == bool(args.prompt_file):
        parser.error("Provide exactly one of --prompt or --prompt-file.")

    prompt = args.prompt
    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text(encoding="utf-8")

    texts = read_texts(args.input, jsonl_text_field=args.jsonl_text_field)
    judge = LLMJudge(
        prompt=prompt or "",
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        response_format=None if args.no_json_mode else {"type": "json_object"},
    )
    results = judge.evaluate_many(
        texts,
        batch_size=args.batch_size,
        max_workers=args.max_workers,
    )
    write_results(args.output, results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
