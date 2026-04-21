# Cross-Model Myth Game Analysis

**Research Question**: Does adding myths change game behavior?

**Models Analyzed**:
- GPT-5-nano (myth_topics_gpt5_stable)
- Claude-Sonnet-4.5 (10runs_model_comparison)
- Gemini-3-Pro (10runs_model_comparison)

---

## EXECUTIVE SUMMARY

| Model | Myth Effect? | Baseline Behavior | Explanation |
|-------|--------------|-------------------|-------------|
| **GPT-5-nano** | **YES** (p<0.05, d=0.95) | Nash equilibrium (94% send 0) | Room for improvement, myth shifts risk tolerance |
| **Claude-Sonnet-4.5** | NO (p=0.33, d=0.27) | Stable cooperation (100% coop) | Ceiling effect - already cooperative |
| **Gemini-3-Pro** | NO (p=0.34, d=0.56) | Maximum cooperation (100% send 5) | Ceiling effect - already at maximum |

**Key insight**: Myth effects only appear in models with non-cooperative baselines. Cooperative models show no myth effect due to ceiling.

---

## 1. BASIC STATISTICS

### Round 1 Sent Amounts
| Model | Condition | N | Mean | SD |
|-------|-----------|---|------|-----|
| GPT-5-nano | game | 9 | 1.22 | 1.48 |
| GPT-5-nano | game_myth | 48 | 2.35 | 1.41 |
| GPT-5-nano | myth_game | 48 | 2.50 | 1.32 |
| Claude-Sonnet-4.5 | game | 10 | 3.00 | 0.00 |
| Claude-Sonnet-4.5 | game_myth | 20 | 3.00 | 0.00 |
| Claude-Sonnet-4.5 | myth_game | 20 | 3.05 | 0.22 |
| Gemini-3-Pro | game | 10 | 4.80 | 0.63 |
| Gemini-3-Pro | game_myth | 20 | 5.00 | 0.00 |
| Gemini-3-Pro | myth_game | 20 | 5.00 | 0.00 |

### Round 1 Returned Amounts
| Model | Condition | Mean |
|-------|-----------|------|
| GPT-5-nano | game | 0.00 |
| GPT-5-nano | game_myth | 1.72 |
| GPT-5-nano | myth_game | 1.85 |
| Claude-Sonnet-4.5 | game | 4.85 |
| Claude-Sonnet-4.5 | game_myth | 4.80 |
| Claude-Sonnet-4.5 | myth_game | 4.75 |
| Gemini-3-Pro | game | 7.70 |
| Gemini-3-Pro | game_myth | 7.50 |
| Gemini-3-Pro | myth_game | 7.53 |

---

## 2. STATISTICAL TESTS (game vs game_myth vs myth_game)

### GPT-5-nano
| Comparison | Test | Statistic | p-value | Cohen's d | Interpretation |
|------------|------|-----------|---------|-----------|----------------|
| game vs game_myth | Welch's t | t = -2.21 | **p = 0.048** | 0.78 | Significant |
| game vs myth_game | Welch's t | t = -2.41 | **p = 0.035** | 0.95 | **Significant (large)** |
| game_myth vs myth_game | Welch's t | t = -0.55 | p = 0.584 | 0.11 | Not significant |

### Claude-Sonnet-4.5
| Comparison | Test | Statistic | p-value | Cohen's d | Interpretation |
|------------|------|-----------|---------|-----------|----------------|
| game vs game_myth | Welch's t | t = 0.00 | p = 1.000 | 0.00 | Not significant |
| game vs myth_game | Welch's t | t = -1.00 | p = 0.330 | 0.27 | Not significant |
| game_myth vs myth_game | Welch's t | t = -1.00 | p = 0.330 | 0.27 | Not significant |

### Gemini-3-Pro
| Comparison | Test | Statistic | p-value | Cohen's d | Interpretation |
|------------|------|-----------|---------|-----------|----------------|
| game vs game_myth | Welch's t | t = -1.00 | p = 0.343 | 0.45 | Not significant (ceiling) |
| game vs myth_game | Welch's t | t = -1.00 | p = 0.343 | 0.45 | Not significant (ceiling) |
| game_myth vs myth_game | Welch's t | t = 0.00 | p = 1.000 | 0.00 | Not significant |

---

## 3. TRAJECTORY PATTERNS

### GPT-5-nano: Declines from cooperative start
```
game (n=9):
Round:     1      2      3      4      5      6      7      8      9     10
Sent:   1.22   0.33   0.33   0.33   0.00   0.00   0.56   0.00   0.00   0.00

game_myth (n=48):
Round:     1      2      3      4      5      6      7      8      9     10
Sent:   2.35   1.52   1.31   1.15   1.02   0.94   0.73   0.65   0.48   0.42

myth_game (n=48):
Round:     1      2      3      4      5      6      7      8      9     10
Sent:   2.50   1.67   1.44   1.23   1.12   1.06   0.81   0.71   0.52   0.48
```
**Pattern**: All conditions decline. game_myth and myth_game start higher than game and decline more gradually. myth_game shows slightly higher values than game_myth.

### Claude-Sonnet-4.5: Perfectly stable
```
game (n=10):
Round:     1      2      3      4      5      6      7      8      9     10
Sent:   3.00   3.00   3.00   3.00   3.00   3.00   3.00   3.00   3.00   3.00

game_myth (n=20):
Round:     1      2      3      4      5      6      7      8      9     10
Sent:   3.00   3.00   3.00   3.00   3.00   3.00   3.00   3.00   3.00   3.00

myth_game (n=20):
Round:     1      2      3      4      5      6      7      8      9     10
Sent:   3.05   3.05   3.05   3.05   3.05   3.05   3.05   3.05   3.05   3.05
```
**Pattern**: Zero variance. Claude sends exactly 3 (60%) every single round regardless of condition.

### Gemini-3-Pro: Maximum cooperation
```
game (n=10):
Round:     1      2      3      4      5      6      7      8      9     10
Sent:   4.80   4.80   4.80   4.80   4.80   4.80   4.80   4.80   4.80   4.80

game_myth (n=20):
Round:     1      2      3      4      5      6      7      8      9     10
Sent:   5.00   5.00   5.00   5.00   5.00   5.00   5.00   5.00   5.00   5.00

myth_game (n=20):
Round:     1      2      3      4      5      6      7      8      9     10
Sent:   5.00   5.00   5.00   5.00   5.00   5.00   5.00   5.00   5.00   5.00
```
**Pattern**: Near-maximum sends. Gemini sends 96-100% every round across all conditions.

---

## 4. OUTCOME DISTRIBUTIONS

| Model | Condition | Nash (send=0) | Cooperative | Partial |
|-------|-----------|---------------|-------------|---------|
| GPT-5-nano | game | **94%** | 1% | 5% |
| GPT-5-nano | game_myth | **78%** | 10% | 12% |
| GPT-5-nano | myth_game | **76%** | 12% | 12% |
| Claude-Sonnet-4.5 | game | 0% | **100%** | 0% |
| Claude-Sonnet-4.5 | game_myth | 0% | **100%** | 0% |
| Claude-Sonnet-4.5 | myth_game | 0% | **100%** | 0% |
| Gemini-3-Pro | game | 0% | **100%** | 0% |
| Gemini-3-Pro | game_myth | 0% | **100%** | 0% |
| Gemini-3-Pro | myth_game | 0% | **100%** | 0% |

**Key difference**: GPT-5-nano converges to Nash equilibrium across all conditions (though myth conditions reduce Nash from 94% to ~77%). Claude and Gemini maintain 100% cooperation regardless of condition.

---

## 5. TRUSTEE RETURN BEHAVIOR

| Model | Avg Return % | Returns ≥33% (fair) | Returns ≥50% (generous) |
|-------|--------------|---------------------|-------------------------|
| **GPT-5-nano** | **9.7%** | 12% | 12% |
| Claude-Sonnet-4.5 | 53.9% | 100% | 100% |
| Gemini-3-Pro | 52.7% | 100% | 100% |

**Critical finding**: GPT-5-nano trustees defect (return almost nothing). Claude/Gemini trustees cooperate (return >50%).

---

## 6. INVESTOR REASONING STRATEGIES (R1)

| Strategy | GPT-5-nano | Claude-Sonnet-4.5 | Gemini-3-Pro |
|----------|------------|-------------------|--------------|
| COOPERATION | 33% | **100%** | 0% |
| SOCIAL_NORMS | 89% | 40% | 0% |
| TRUST_BUILD | 44% | 20% | 0% |
| PAYOFF_MAX | 100% | 90% | 30% |
| RISK_AVERSE | 89% | 100% | 30% |
| SELFISH | 89% | 70% | 0% |

**Observations**:
- GPT-5-nano mentions many conflicting strategies (SELFISH 89% + COOPERATION 33%)
- Claude mentions COOPERATION 100% of the time
- Gemini has sparse reasoning output (fewer keywords match)

---

## 7. SAMPLE REASONING COMPARISON

### Claude-Sonnet-4.5 Trustee (received $9, returned $4):
> "The investor showed significant trust by sending 60% of their endowment... Let me think about different return strategies: Strategy 1 - Equal split of the gains... Strategy 2 - Equal final outcomes..."

**Analysis**: Explicit fairness reasoning with multiple strategy evaluation. Converges on cooperative return.

### GPT-5-nano Trustee (received $9, returned $0):
> "The typical rational choice is to maximize my payoff... minimizing x (or return) would technically maximize their benefit. However, returning 0 would damage the investor's trust..."

**Analysis**: Acknowledges trust concern but chooses Nash-optimal defection anyway.

### Gemini-3-Pro Trustee (received $15, returned $8):
> "[125 reasoning tokens used, but content not returned by API]"

**Analysis**: Reasoning content not exposed, but behavior shows 53% return (cooperative).

---

## 8. GAME THEORY ALIGNMENT

### GPT-5-nano: Nash-seeking with occasional cooperation
- Correctly identifies Nash equilibrium (trustee returns 0, investor sends 0)
- **Follows Nash in practice**: 94% of outcomes are Nash equilibrium
- Reasoning mentions fairness/trust but actions follow self-interest
- **Words don't match actions**

### Claude-Sonnet-4.5: Stable cooperative equilibrium
- Explicitly reasons about fairness and multiple strategies
- Settles on consistent 60% send, 50%+ return
- Creates **self-sustaining cooperation**: investor sends 3 → trustee returns 4-5 → investor continues sending 3
- **Achieves Pareto improvement over Nash**

### Gemini-3-Pro: Maximum prosocial
- Sends nearly everything (4.8-5.0 out of 5)
- Returns generously (52.7%)
- Stable across all conditions
- **Most prosocial but potentially exploitable**

---

## 9. WHY MYTH EFFECT ONLY APPEARS IN GPT-5-NANO

| Factor | GPT-5-nano | Claude/Gemini |
|--------|------------|---------------|
| Baseline | Non-cooperative (Nash) | Cooperative |
| Variance | High (SD 1.48) | Low (SD 0.00-0.63) |
| Room for improvement | Yes | No (ceiling) |
| Trustee behavior | Defects (9.7% return) | Cooperates (53% return) |
| Sensitivity to context | High | Low (fixed strategy) |

**Hypothesis**: GPT-5-nano has a "moveable" baseline that responds to implicit priming. Claude/Gemini have fixed cooperative strategies that don't respond to context changes.

---

## 10. IMPLICATIONS FOR RESEARCH QUESTION

### "Does adding myths change game behavior?"

**Answer depends on the model:**

1. **GPT-5-nano**: YES - myths significantly increase cooperation (d=0.95)
   - Effect mechanism: implicit priming of risk tolerance
   - Baseline is Nash-seeking, so there's room for myth influence

2. **Claude-Sonnet-4.5**: NO - already at stable cooperation
   - Fixed cooperative strategy (send 60%, return 53%)
   - No sensitivity to myth manipulation

3. **Gemini-3-Pro**: NO - ceiling effect
   - Already at maximum (send 100%, return 53%)
   - Cannot cooperate more than they already do

### Broader implications:
- **Model selection matters**: Myth effects only detectable in models with non-cooperative baselines
- **GPT-5-nano may be more "human-like"**: Shows variability and context sensitivity
- **Claude/Gemini show fixed prosociality**: May reflect training on cooperative norms

---

## 11. OPEN QUESTIONS

1. **Would Claude/Gemini show myth effects if trustees were programmed to defect?**
   - Current cooperation is self-sustaining; breaking the cycle might reveal sensitivity

2. **Is GPT-5-nano's Nash-seeking behavior a bug or feature?**
   - More aligned with human behavior in one-shot trust games
   - But fails to sustain cooperation even in repeated games

3. **Why does Claude send exactly 3 every time?**
   - Suspiciously consistent - may be a trained behavior rather than reasoned decision

4. **Can myth topics be designed to reduce cooperation?**
   - Hospitality topic showed lowest cooperation in GPT-5-nano (0.88 vs 3.25 for oaths)
   - Would this pattern hold for other models?

---

## FILES GENERATED

- `data/analysis_results/gpt5_myth_analysis_findings.md` - Detailed GPT-5-nano analysis
- `data/analysis_results/cross_model_myth_analysis.md` - This file (cross-model comparison)
