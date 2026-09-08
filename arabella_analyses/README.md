# cultevo-transcript-analysis

Repository for transcript analysis experiments.

## Together AI LLM judge

This repo includes a small reusable interface for judging plain text strings with
Together AI.

Install the package and dependencies:

```bash
python -m pip install -e ".[test]"
```

Set your Together API key:

```bash
export TOGETHER_API_KEY="your_api_key"
```

Use the Python interface:

```python
from analysis.judge import LLMJudge

judge = LLMJudge(
    prompt=(
        "Evaluate the text below. Return JSON with keys score and rationale.\n\n"
        "Text:\n{text}"
    )
)

result = judge.evaluate("Agent A cooperated consistently across the exchange.")
print(result.judgment)

results = judge.evaluate_many(["first text", "second text"], batch_size=2, max_workers=2)
```

Or use the CLI with a `.txt` file or JSONL file containing a `text` field:

```bash
python -m analysis.judge_cli \
  --input inputs.jsonl \
  --output outputs/judgments.jsonl \
  --prompt-file judge_prompt.txt
```

By default, the judge asks Together for JSON output and preserves raw model
responses when parsing fails.
