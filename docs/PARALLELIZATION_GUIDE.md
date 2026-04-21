# Parallelization Guide

This guide explains how to use the parallel execution features in the batch experiment runner.

## Quick Start

### 1. Test Your Rate Limits (Recommended First Step)

Before running large parallel batches, determine the optimal worker count for your API plan:

```bash
python experiments/test_rate_limits.py --max-workers 8
```

This will:
- Run minimal experiments (3 turns each) with increasing worker counts
- Monitor rate limit errors from OpenRouter
- Recommend the optimal `--workers` setting
- Takes ~5-10 minutes to complete

Example output:
```
Workers    Success    RL Errors    Total Time    Avg Time
--------------------------------------------------------------
1          4/4        0            12.3s         3.1s
2          4/4        0            7.1s          1.8s
4          4/4        0            4.2s          1.1s
8          3/4        1            3.8s          0.9s

RECOMMENDATION: Use --workers 4
```

### 2. Run Your Experiments with Optimal Workers

Once you know your optimal worker count:

```bash
# Run with recommended workers
python experiments/run_trust_game_batch.py model_comparison --workers 4

# Or start conservative
python experiments/run_trust_game_batch.py model_comparison --workers 2
```

## Detailed Usage

### Sequential Execution (Default, Backward Compatible)

```bash
# These are equivalent
python experiments/run_trust_game_batch.py pilot
python experiments/run_trust_game_batch.py pilot --workers 1
```

**When to use:**
- Small experiment sets (< 10 experiments)
- Testing new configurations
- Debugging experiment issues
- Conservative API usage

**Pros:**
- Easier to monitor individual experiments
- Lower memory usage
- Predictable execution order

**Cons:**
- Slower for large batches

### Parallel Execution

```bash
# Run with 4 workers
python experiments/run_trust_game_batch.py model_comparison --workers 4

# Run with 8 workers (if rate limits allow)
python experiments/run_trust_game_batch.py model_comparison --workers 8
```

**When to use:**
- Large experiment sets (> 20 experiments)
- Production runs after testing
- When you've verified rate limits

**Pros:**
- 4-8x faster (depending on worker count)
- Efficient use of time
- Better user experience (see progress as experiments complete)

**Cons:**
- Higher memory usage (~500MB-1GB per worker)
- Risk of hitting API rate limits if too many workers
- Less detailed progress tracking per experiment

### Rate Limit Testing Options

```bash
# Quick test with fewer workers
python experiments/test_rate_limits.py --max-workers 4 --test-turns 2

# Test specific model
python experiments/test_rate_limits.py --model "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"

# More thorough test
python experiments/test_rate_limits.py --max-workers 16 --experiments-per-test 8
```

**Options:**
- `--max-workers N`: Test up to N workers (default: 8)
- `--test-turns N`: Turns per test experiment (default: 3, keep low for speed)
- `--model MODEL`: Specific model to test (default: first from pilot config)
- `--experiments-per-test N`: Experiments per worker count (default: 4)

## How Parallelization Works

### Architecture

```
Main Process
├── ProcessPoolExecutor (N workers)
│   ├── Worker 1 → Experiment A → Independent API client
│   ├── Worker 2 → Experiment B → Independent API client
│   ├── Worker 3 → Experiment C → Independent API client
│   └── Worker N → Experiment N → Independent API client
└── Collects results as they complete
```

**Key features:**
- **Process-based**: Each worker is a separate Python process (no GIL limitations)
- **Isolated**: Workers don't share state or API clients
- **Independent**: One experiment failure doesn't affect others
- **Asynchronous progress**: Results shown as experiments complete (not in submission order)

### Memory Usage

Each worker process loads:
- Full Python dependencies
- LLM client libraries
- Experiment configuration
- Game and simulation code

**Estimate**: ~500MB-1GB per worker

**Example**: 8 workers ≈ 4-8GB total memory usage

### API Rate Limits

OpenRouter enforces different rate limits based on:
- Subscription plan (free vs. paid tiers)
- Model being used (popular models may have stricter limits)
- Account history and usage patterns

**Why test matters:**
- Free tier: Often 10-20 requests/minute → Use 1-2 workers
- Paid tier: Often 100+ requests/minute → Can use 4-8 workers
- Enterprise: Higher limits → Can use 8+ workers

The `test_rate_limits.py` script helps you find your specific limits.

### Checkpointing Behavior

Checkpointing works identically in parallel and sequential modes:

```
experiment_name_001_model_persona_task_order.json          # Final output
experiment_name_001_model_persona_task_order.results.json  # Lightweight state
experiment_name_001_model_persona_task_order.checkpoint.json  # Resume point
```

**Parallel safety:**
- Each experiment has independent checkpoint files
- No file conflicts between workers
- If Worker 1 crashes, Workers 2-N continue unaffected
- Re-run the batch to resume failed experiments from checkpoints

## Best Practices

### 1. Always Test Rate Limits First

```bash
# Before running large batch
python experiments/test_rate_limits.py --max-workers 8

# Then use recommended workers
python experiments/run_trust_game_batch.py model_comparison --workers 4
```

### 2. Start Conservative

```bash
# First run: conservative
python experiments/run_trust_game_batch.py model_comparison --workers 2

# If no rate limit errors, increase
python experiments/run_trust_game_batch.py model_comparison --workers 4
```

### 3. Monitor the First Few Completions

Watch for rate limit errors in the output:
```
[1/54] ✓ meta-llama/... / neutral / ['game']
    → data/json/model_comparison/...
[2/54] ✗ FAILED: meta-llama/... / altruistic / ['game']
    Error: 429 Too Many Requests  # ← Rate limit!
```

If you see rate limit errors:
1. Stop the batch (Ctrl+C)
2. Reduce worker count
3. Re-run (will resume from checkpoints)

### 4. Use Sequential for Debugging

If experiments are failing mysteriously:

```bash
# Switch to sequential for clearer error messages
python experiments/run_trust_game_batch.py experiment_name --workers 1
```

Sequential mode provides more detailed per-experiment output.

### 5. Consider API Costs

**Important**: Parallelization doesn't reduce API calls, just speeds them up.

- 54 experiments × 10 turns × 2 agents = 1,080 API calls
- Same cost whether workers=1 or workers=8
- But workers=8 completes ~8x faster

**Budget accordingly:**
- Know your OpenRouter quota limits
- Monitor usage during runs
- Consider spreading large batches across multiple days

## Troubleshooting

### "Too Many Requests" / Rate Limit Errors

**Solution**: Reduce workers or add delays

```bash
# Reduce from 8 to 4 workers
python experiments/run_trust_game_batch.py experiment_name --workers 4

# Or use sequential
python experiments/run_trust_game_batch.py experiment_name --workers 1
```

The existing retry logic in `src/utils.py` handles occasional rate limits, but sustained errors mean too many workers.

### Memory Issues / System Slowdown

**Solution**: Reduce workers

```bash
# If system is sluggish, reduce workers
python experiments/run_trust_game_batch.py experiment_name --workers 2
```

Each worker uses substantial memory. On systems with <16GB RAM, use ≤4 workers.

### Inconsistent Results Between Runs

**Check**: Are you using the same worker count?

Parallel execution order is non-deterministic (experiments complete in varying order). However, **individual experiment results are deterministic** given the same:
- Model
- Temperature
- Random seed
- Configuration

The batch summary might show experiments in different orders, but each experiment's internal results are reproducible.

### One Experiment Keeps Failing

**Solution**: Debug it individually

```bash
# First, identify the failing combo from batch output
# Then run just that experiment in sequential mode for clearer errors
python experiments/run_trust_game.py  # Edit to match failing combo
```

Or reduce to workers=1 for clearer error messages.

## Performance Examples

Based on typical experiment durations:

### Small Batch (8 experiments, 3 minutes each)

| Workers | Expected Time | Speedup |
|---------|--------------|---------|
| 1       | 24 minutes   | 1x      |
| 2       | 12 minutes   | 2x      |
| 4       | 6 minutes    | 4x      |

### Medium Batch (54 experiments, 5 minutes each)

| Workers | Expected Time | Speedup |
|---------|--------------|---------|
| 1       | 270 minutes  | 1x      |
| 4       | 68 minutes   | 4x      |
| 8       | 34 minutes   | 8x      |

### Large Batch (200 experiments, 4 minutes each)

| Workers | Expected Time | Speedup |
|---------|--------------|---------|
| 1       | 800 minutes  | 1x      |
| 4       | 200 minutes  | 4x      |
| 8       | 100 minutes  | 8x      |

**Note**: Actual speedup depends on:
- API response times (variable)
- Rate limit throttling
- System resources
- Network conditions

## Advanced Usage

### Testing Different Worker Counts

```bash
# Test progression to find optimal
python experiments/run_trust_game_batch.py small_test --workers 1
python experiments/run_trust_game_batch.py small_test --workers 2
python experiments/run_trust_game_batch.py small_test --workers 4
# Compare total times
```

### Running Multiple Experiment Sets

```bash
# Run multiple sets with same worker count
python experiments/run_trust_game_batch.py pilot --workers 4
python experiments/run_trust_game_batch.py persona_comparison --workers 4
python experiments/run_trust_game_batch.py model_comparison --workers 4
```

### Monitoring System Resources

```bash
# In another terminal, monitor resource usage
watch -n 2 "ps aux | grep python | grep -v grep | wc -l"  # Process count
htop  # Interactive monitoring
```

## Summary

1. **Always test rate limits first**: `python experiments/test_rate_limits.py`
2. **Start conservative**: Use recommended workers or less
3. **Monitor early results**: Watch for rate limit errors
4. **Scale up gradually**: If no errors, increase workers on next run
5. **Know your API quota**: Budget accordingly
6. **Use sequential for debugging**: Clearer error messages

With proper rate limit testing and conservative worker counts, parallelization can speed up large experiment batches by 4-8x with no downsides.
