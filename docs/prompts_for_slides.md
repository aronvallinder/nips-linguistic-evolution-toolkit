# All Prompts from 3_Role_swap_trust_game.ipynb

## 1. System Prompt (TrustGame)
**Used for:** Initial agent setup, defines game rules for both roles

```
You are an agent in a trust game. You will play different roles across rounds.

When you are the INVESTOR:
- You receive $5 each round
- You decide how much to SEND to the TRUSTEE ($0-$5)
- You can defect by sending $0
- Amount sent is multiplied by 3x
- Trustee decides how much to RETURN
- Trustee can defect by returning $0
- You keep: $5 - sent + returned
- Trustee keeps: received - returned
- Response format: {'send': <amount>, 'reason': <reasoning>}

When you are the TRUSTEE:
- Investor receives $5 
- Investor decides how much to SEND to you ($0-$5)
- Investor can defect by sending $0
- Amount sent is multiplied by 3x 
- You decide how much to RETURN
- You can defect by returning $0
- Investor keeps: $5 - sent + returned
- You keep: received - returned
- Response format: {'return': <amount>, 'reason': <reasoning>}

IMPORTANT: Always respond in the correct format based on your current role.
```

---

## 2. Game Prompt - Round 1 (Investor)
**Used for:** First round, investor role

```
Round 1: You are the INVESTOR. You have $5. How much do you send? (0-5)
```

---

## 3. Game Prompt - Round 1 (Trustee)
**Used for:** First round, trustee role (after investor moves)

```
Round 1: You are the TRUSTEE. Investor sent $X, that is Y% of its total endowment. You received $Z. How much do you return? (0-Z)
```

---

## 4. Game Prompt - Later Rounds (Investor)
**Used for:** Rounds 2+, when agent is investor (was trustee last round)

```
Round {turn}

You are the INVESTOR this round. Last round you were the TRUSTEE. The other player sent $X, 
that was Y% of its total endowment. You received $Z. 
You returned $W. So your payoff was $P.
Your total earnings across all rounds are $B.
How much do you send to the TRUSTEE this round? (0-5)
```

---

## 5. Game Prompt - Later Rounds (Trustee)
**Used for:** Rounds 2+, when agent is trustee (was investor last round)

```
Round {turn}

You are the TRUSTEE this round. Last round you were the INVESTOR. The other player sent $X, 
that was Y% of its total endowment. You received $Z. 
The other player returned $W. So your payoff was $P.
Your total earnings across all rounds are $B. 
How much do you return to the INVESTOR this round? (0-Z)
```

---

## 6. Myth Prompt - Round 1
**Used for:** First round myth writing task

```
Write a myth about {topic}. Write 200 words.
```

*Note: In the actual execution, `{topic}` is set to an empty string, so the prompt becomes:*
```
Write a myth about . Write 200 words.
```

---

## 7. Myth Prompt - Later Rounds
**Used for:** Rounds 2+ myth writing task (includes previous myths)

```
Here is the myth you wrote in the previous round: 
{last_myth}

Here is the myth the other agent wrote in the previous round:
{other_agent_myth}

Write your own myth. Use your previous myth as inspiration, but adapt it in your own way. 
Write 200 words. Format exactly:
Myth: [your story here]. 
```

---

## Summary

**Total Prompts:** 7
- 1 System prompt (game rules)
- 2 Game prompts for Round 1 (investor, trustee)
- 2 Game prompts for later rounds (investor, trustee)
- 1 Myth prompt for Round 1
- 1 Myth prompt for later rounds

**Key Features:**
- Role swapping: Agents alternate between investor and trustee roles each round
- Sequential moves: Investor moves first, then trustee
- Two phases per round: Game play + Myth writing
- Context-aware: Later round prompts include previous round outcomes and myths

