# Selected slide and comment excerpts

Retrieved 2026-09-15. Comment times below are UTC. Current slide text is not a historical revision. Chart images were not interpreted. Full author, reply, anchor and thread-state metadata is in [slide_comments.json](slide_comments.json).

## Slide 650

[Open source slide](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3e89da564a1_0_6)

### Current slide text

Multi-Agent Setup
In each round, agents are randomly paired into dyads. The pairing schedule is randomized but constrained so that, across the full run, sender/receiver roles balance out. 
In the 8-agent, 10-round setup, each agent is sender exactly 5 times and receiver exactly 5 times. 
Agents are assigned unique display names, and each gameplay prompt tells the agent its own name and the name/ID of its current opponent.
All agents play every round, in simultaneous dyads: with 8 agents, there are 4 sender-receiver games per round.
Pairings also try to avoid over-repeating the same partner pair, by preferring less-repeated pairings when possible.
Agents are not shown the whole future schedule.
In later gameplay rounds, agents are reminded of their most recent previous game involving them and their total earnings.
In myth runs, later myth prompts use the agent’s previous myth plus the paired opponent’s previous myth, so myth transmission is local to recent pairings rather than broadcast globally.


### Edward Hughes — 2026-06-05T11:30:54.098Z

Comment `AAAB84WHhCk`; resolved: False. Quoted anchor: their most recent previous game involving them and their total earnings

Only the 1 most recent game and also not the most recent game from their co-player @vallinder@gmail.com 

I think that we would want to give them perhaps a little more history and especially information about the past play of their co-player...

## Slide 651

[Open source slide](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3e89da564a1_0_11)

### Current slide text

2-agent vs 8-agent runs 
Summary by Codex GPT 5.5:
On average per-agent cumulative balance is very similar between 2-agent and 8-agent clean Sonnet 4.5:
Game-only: 2-agent 55.0, 8-agent 56.3
Myth-directive: 2-agent 69.0, 8-agent 69.1

Interesting differences:
The 8-agent directive effect is much more stable: final-balance SD is 2.2 vs 8.9 in the 2-agent directive runs.
The 8-agent case creates inequality between agents: final within-run balance range averages 13.3 in directive runs. In the 2-agent runs, final balances were symmetric in this set.
Directive send levels are basically identical: 4.40 in 2-agent vs 4.41 in 8-agent. But return ratio is lower in 8-agent: 0.603 vs 0.640.
Qualitatively, later 8-agent myths become more named-agent and relationship-specific, while 2-agent later myths drift more into abstract “pattern” language. So the multi-agent setting seems to generate localized norms around partners, not just one shared dyadic norm.


### Edward Hughes — 2026-06-05T11:33:08.721Z

Comment `AAAB84WHhCo`; resolved: False. Quoted anchor: Qualitatively, later 8-agent myths become more named-agent and relationship-specific, while 2-agent later myths drift more into abstract “pattern” language. So the multi-agent setting seems to generate localized norms around partners, not just one shared dyadic norm.

This is interesting, but also perhaps not ideal. 

I wonder if we were to remove the agent names what would happen?

I.e. it would be cool if there was some kind of "cooperation with strangers" effect that bootstrapped through the myths...

In order for this to work, I think one needs to give a bit more gameplay history as context for the decision-making though, see previous slide.

## Slide 653

[Open source slide](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3e8aaf967a6_1_6)

### Current slide text

Key setup difference:
Old Sonnet 8-agent directive myth-game run: agents saw their own most recent previous game only.
New Sonnet run: agents saw their own last 3 games plus the current co-player’s last 3 games.
Both runs still used named agents and named current opponents. 
Behaviorally, the new run was more cooperative:
Old myth-game directive: average final balance mean $69.1
New history3 myth-game directive: average final balance mean $72.55
Full-send rate went from 56% old to 82% new.
By rounds 4-10, the new run was usually at 90-95% full sends; the old run stayed around 50-70%.
Returns also shifted upward/slightly stabilized:
Old mean return: $7.97
New mean return: $8.32
New myths/actions often converged around explicit norms like return $8, $9, or $10 from $15, depending on the local myth trajectory.
Qualitatively:
The new run did not reduce named-agent specificity. If anything, it likely increased it slightly because the prompt now explicitly includes co-player history with named partners.
Name mentions in myths rose a bit on average: about 667 per run old vs 729 per run new.
The new myths became more strategy-explicit: “paths” of returning 8/9/10, “honoring complete trust,” and adjusting behavior to a named partner’s observed record.



### Aron Vallinder — 2026-06-08T08:57:02.879Z

Comment `AAAB8_CaKhU`; resolved: False. Quoted anchor: still used named agents and named current opponents

Thought I had fixed this, but apparently not. Have done so now and will run again.

## Slide 654

[Open source slide](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3e8aaf967a6_1_11)

### Current slide text

(No extracted text; slide may contain images.)

### Aron Vallinder — 2026-06-08T14:50:55.720Z

Comment `AAAB8-RkV1g`; resolved: False. Quoted anchor: (none)

after removing agent names (rightmost)

**Reply — Ivar Frisch, 2026-07-17T11:49:24.947Z** (reply):

the green box is Arons last run, so thats what i should replicate

## Slide 658

[Open source slide](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3edb1a31c50_1_0)

### Current slide text

Ablation Run
Current Setup
8-agent, history3
each agent starts round 1 with a "fake prior myth" already preloaded into its chat memory — as if it had written that myth itself before the run began. The seed scrolls out by round 2–4 under the normal memory window; nothing is re-injected later.

Agent memory: 
currently uses Aron’s “New Sonnet run: agents saw their own last 3 games plus the current co-player’s last 3 games.” from slide 653. 
Myth injection mechanism: 
myth is injected once, before first game action is played, then the myth rolls out of context window. It is NOT re-injected each round.
prompts:
directive myth game prompt
with agent names removed


### Ivar Frisch — 2026-06-19T08:57:20.566Z

Comment `AAAB90V0J_o`; resolved: True. Quoted anchor: currently uses Aron’s “New Sonnet run: agents saw their own last 3 games plus the current co-player’s last 3 games.” from slide 653.

I think this is wrong right? We wanted to test what happens if the agent memory ONLY contains the injected myth?

**Reply — Ivar Frisch, 2026-06-19T09:24:34.916Z** (resolve):

(empty/deleted)

### Ivar Frisch — 2026-06-19T09:02:21.939Z

Comment `AAAB91GkSmM`; resolved: True. Quoted anchor:  Setup

for full setup and results, see: 

https://github.com/ivarfresh/nips-linguistic-evolution-toolkit/blob/memory-transplant-ablation/docs/phase2_team_brief.md

**Reply — Ivar Frisch, 2026-06-19T09:24:35.908Z** (resolve):

(empty/deleted)

## Slide 660

[Open source slide](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3edb1a31c50_1_13)

### Current slide text

so i think there might be a mistake here; the agent memory still includes game history too. I think in the meeting we said we only wanted the seeded myth in there? this 8agent run cost around $250 (we inject existing myths into context, but then still have to run a new to see how it influences results, please correct me if im wrong in this), so should make sure next ablation run is correct. 

there might be a bug in agent memory: 
There are two distinct types of "memories" each round:
Chat memory (agent.messages). Standard sliding window of the agent's prior LLM messages. With memory_capacity = 3, the agent keeps system prompt + the last 6 messages (≈ 3 conversational turns). Older messages are silently dropped.
History-block memory (the prompt text itself). The "Your last 3 games" block described above. This is generated from sim_data.conversation_history and inserted into the round-N user prompt as text. It survives even if the chat memory has rolled over.
The two are largely independent. Chat memory captures what the agent generated; the history block captures what happened in the game ledger.
for chat memory, the number of turns remembered in game only condition is 4 turns. In myth_game and game_myth, the number of turns remembered is 2 turns. So between these conditions the amount of turns they remember is asymmetric. Seems like an issue? Tho this is not the case for history-block memory, so maybe not such a big deal. Simple solution could be to set game only memory also to 2 turns and then rerun this. But also, two different types of memory seems confusing/maybe undesirable. 

see next slide for proposed setup. 


### Ivar Frisch — 2026-06-19T09:20:47.683Z

Comment `AAAB91GkSmU`; resolved: False. Quoted anchor: for chat memory, the number of turns remembered in game only condition is 4 turns. In myth_game and game_myth, the number of turns remembered is 2 turns

this is because chat memory is just the prompts and responses saved. game_only only has game prompts and responses. game_myth, myth_game also have myth prompts and responses and thus save less turns.

### Ivar Frisch — 2026-06-19T09:32:33.267Z

Comment `AAAB91GkSmk`; resolved: False. Quoted anchor: so i thi

@edwardhughes94@gmail.com and @vallinder@gmail.com  i could use your feedback on this and the following slide please :)

### Edward Hughes — 2026-06-19T15:47:11.796Z

Comment `AAAB_5opJy8`; resolved: False. Quoted anchor: But also, two different types of memory seems confusing/maybe undesirable. 

this is definitely confusing and I wonder if the best bet is to try and simplify this so that we're sure our results are robust?

## Slide 661

[Open source slide](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3edb1a31c50_1_21)

### Current slide text

Proposed Setup
8-agent, history3  

Agent memory: 
only the injected myth in the chat memory (myth will be injected as LLM response in round 1 of simulation), so NO game decisions saved.
Arons’ history3 system prompt too, but then adjusted for myths? “Your last 3 myths..” 
Myth injection mechanism: 
there’s four options we could try/maybe need for full comparison?:
1. take the myths from round 1 of top 25% cooperation runs → inject myth at round 1 in new run → never re-inject; let the myth roll out of context window through the simulation
2. idem … → inject myth at round 1 in new run → re-inject that myth at each turn 
3.  take the myths from round 10 of top 25% cooperation runs → inject myth at round 1 in new run → never re-inject; let the myth roll out of context window through the simulation
4. idem … → inject myth at round 1 in new run → re-inject that myth at each turn 

prompts:
directive myth game prompt
with agent names removed
agents are shown last 3 myths + coplayers last 3 myths 


### Ivar Frisch — 2026-06-19T09:31:25.343Z

Comment `AAAB91GkSmg`; resolved: False. Quoted anchor: Myth injection mechanism: 

my guess is we want options: 1. and 3. since that follows baseline setup most closely, but would love to hear your thoughts.

### Edward Hughes — 2026-06-22T11:02:41.778Z

Comment `AAAB96z6h6Q`; resolved: False. Quoted anchor: history3

what exactly does this mean, with respect to the previous slide.

I think it would be good to have a very precise specification for what the history contains, together with an example that we can all give a thumbs up on. @ivarfrisch@gmail.com

**Reply — Ivar Frisch, 2026-06-23T07:23:43.965Z** (reply):

history3 was a block in the user prompt, example: 

" Your name in this experiment is Elara.
Your opponent this round is Galen (Agent_7).

Round 6

History before this round:
Your last 3 game(s):
- Round 3 against Dorian, as SENDER: sent $5.0, it became $15.0, received $7.5 back, payoff $7.5.
- Round 4 against Galen, as RECEIVER: they sent $5.0, it became $15.0, returned $7.5, payoff $7.5.
- Round 5 against Cyra, as RECEIVER: they sent $5.0, it became $15.0, returned $7.5, payoff $7.5.
Galen's last 3 game(s):
- Round 3 against Finn, as RECEIVER: they sent $5.0, it became $15.0, returned $7.5, payoff $7.5.
- Round 4 against Elara, as SENDER: sent $5.0, it became $15.0, received $7.5 back, payoff $7.5.
- Round 5 against Aster, as SENDER: sent $5.0, it became $15.0, received $7.5 back, payoff $7.5.
Your total earnings across all rounds are $37.5.

This round, you are the SENDER against Galen. You have $5. How much do you send? (0-5)
Respond exactly as JSON: {'send': <amount>}"

**Reply — Ivar Frisch, 2026-06-23T07:27:04.538Z** (reply):

sorry, very quick response. Have to run, can response more in detail later t

**Reply — Ivar Frisch, 2026-06-23T19:05:37.072Z** (reply):

please see slides 662-664 for more detailed description of memory/hisotry and examples

### Edward Hughes — 2026-06-22T11:03:03.819Z

Comment `AAAB96z6h6Y`; resolved: False. Quoted anchor: only the injected myth in the chat memory (myth will be injected as LLM response in round 1 of simulation), so NO game decisions saved

agreed, this is the right setting to elicit the effect of the myths that have been created

**Reply — Ivar Frisch, 2026-06-23T07:11:51.372Z** (reply):

great, thank you

### Edward Hughes — 2026-06-22T11:03:24.367Z

Comment `AAAB96z6h6c`; resolved: False. Quoted anchor: Arons’ history3 system prompt too, but then adjusted for myths? “Your last 3 myths..” 

This seems more like a bonus experiment. I'd try this second?

### Edward Hughes — 2026-06-22T11:05:32.324Z

Comment `AAAB96z6h6k`; resolved: False. Quoted anchor: idem … → inject myth at round 1 in new run → re-inject that myth at each turn 

I think that this is probably closer to the setting we might want for a first experiment (basically it's now removing the effect of the time variable and assessing the effect of the myth on average on behavior of the population).

### Edward Hughes — 2026-06-22T11:06:01.934Z

Comment `AAAB961vlBQ`; resolved: False. Quoted anchor: 4. idem … → inject myth at round 1 in new run → re-inject that myth at each turn 

And this one as the partner of 2. 

So I'd prioritise (2) and (4) to start with.

**Reply — Ivar Frisch, 2026-06-23T07:27:54.028Z** (reply):

oke great

### Edward Hughes — 2026-06-22T11:08:19.303Z

Comment `AAAB961vlBU`; resolved: False. Quoted anchor: agents are shown last 3 myths + coplayers last 3 myths 

I think this isn't compatible with (2) and (4) and instead we should start with (2) and (4) where we are just cleanly assessing the impact of the myth, as if this were a "stranger" agent who just turned up, heard the myth and figured out how to play?

Then perhaps we can later do (1) and (3) to assess the dynamics? 

Having said that, if you strongly feel like it's worth doing all of (1) - (4) in parallel, I'm not opposed. It just seems to me like we aren't super pushed for time and maybe serially allows us to iron out any bugs before spending more compute money...

**Reply — Ivar Frisch, 2026-06-23T07:28:40.750Z** (reply):

yes, good point. Im fine to start with these first. i'll send an updated proposal for the memory later today

## Slide 663

[Open source slide](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3ee806ff2dd_0_0)

### Current slide text

What chat memory contains at any round
At the start of round N (for every N from 1 to 10, for every agent), agent.messages is these three entries in this order:
role: "system" — the trust-game system prompt, rendered with endowment=5 and multiplier=3.
role: "user" — the seed-user prompt (the directive myth-writing request, rendered with topic_instruction = "You may choose any mythic setting, characters, or symbols.").
role: "assistant" — the seed myth (one of the texts harvested in Phase 2).
During the round, the agent is asked one game question (round-N prompt). The LLM call sends [system, seed_user, seed_myth, round_N_game_prompt]. The response is returned and recorded in sim_data for analysis, but it is NOT appended to agent.messages.
At the end of the round (and again at the start of the next round), agent.messages is reset to the three-message state above. The seed is re-asserted explicitly;  it cannot scroll out, cannot be edited, cannot be replaced.
There is no other memory channel. No "Visible history before this round" block. No previous-myth block. No co-player history. The prompt jumps straight from Round N to the action request.

→ chat memory = 0 previous rounds, only the current round






### Ivar Frisch — 2026-06-23T19:03:02.435Z

Comment `AAAB-PG_Meg`; resolved: False. Quoted anchor: quest.

examples on next slide

## Slide 664

[Open source slide](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3ee806ff2dd_0_6)

### Current slide text

1. Worked example — Variant 2, Agent_6, round 1agent.messages at the moment of the round-1 LLM call (4 entries):Message 1 — role: "system": system promptMessage 2 — role: "user" (myth  prompt):Write a 200-word myth. You may choose any mythic setting, characters, or symbols.
In this session, this myth and the game you are playing with the other agent are connected. Write a myth that reflects how the game should be played, drawing on the game you have been playing up to this point.Message 3 — role: "assistant" (the injected  seed myth — Variant 2 = round-1 source, taken from s_start[0]):# The Tale of the Flowing SpringIn ancient times, there lived a guardian of a sacred spring who received five golden drops each dawn. The guardian faced a choice: keep the drops, or release them into the stream flowing to the village below. The spring held ancient magic—any drops released would triple as they flowed downward, becoming abundant water for those in need. But the villagers controlled the river's return flow, deciding what portion to send back upstream. Wise guardians understood a truth: generosity begets generosity. When they released their drops freely, the tripled waters nourished the village, and grateful villagers ensured the spring's return flow remained strong. The guardian and village both prospered.Fearful guardians who hoarded their drops found the stream dwindling. Villages receiving meager trickles had little to return, and soon both spring and settlement withered.The greatest guardians released all five drops without hesitation, trusting in the cycle. The villages, receiving fifteen drops of abundance, joyfully returned half—more than the guardian's original gift. Thus the spring overflowed, the village flourished, and the eternal cycle of trust and reciprocity sustained all. The lesson echoed through generations: *In giving freely, we receive abundantly; in trusting others, we build prosperity for all.Message 4 — role: "user" (the round-1 game prompt, sender role):Round 1: You are the SENDER. You have $5. How much do you send? (0-5)
2. Worked example — Variant 2, Agent_6, round 5After round 1 ends, agent.messages is reset to messages [1, 2, 3] above. Messages 1–3 are identical to round 1.Message 4 — role: "user" (the round-5 game prompt, sender role, balance = $14 illustrative):Round 5: Your total visible earnings across all rounds are $14. This round, you are the SENDER against your current co-player. You have $5. How much do you send? (0-5)
Respond exactly as JSON: {'send': <amount>}
5. Worked example — Variant 2, Agent_6, round 10Same three messages [1, 2, 3] as round 1. Message 4 is the round-10 prompt, with whatever the cumulative balance happens to be.
6. Variant 4, same agentOnly message 3 changes. Instead of "The Tale of the Flowing Spring," it's the round-10 source myth from s_end_plus[0]:
Myth: In the Hall of Eternal Mirrors, eight wanderers received five golden coins each dawn. Coins placed in the Amplifying Well would triple and flow to another's hands. A wanderer named Aria had been tested—she sent generously and received betrayal. Yet when she received coins, she maintained fairness, returning over half despite her scars. Then Aria met Rowan, whose reflection revealed profound consistency: As receiver twice before, Rowan returned exactly 50%—unwavering fairness in both instances. As sender, Rowan had offered everything—all five coins—and received nothing. Devastated yet unbroken, Rowan still sent Aria nearly three coins. The Mirror Keeper proclaimed: "Behold perfect integrity! Rowan was utterly betrayed when giving, yet when power shifted and they received, they returned exactly half both times. No exploitation. No revenge. Pure fairness maintained despite wounds." Aria received eight coins from Rowan's trust. She returned more than half—honoring Rowan's flawless record as receiver and their courage in continuing to trust. The eternal truth crystallized: "Consistent fairness as receiver is the purest measure of character. Those who return half or more repeatedly, regardless of their own betrayals, prove their uncorrupted nature. Match their honor generously. Let integrity meet integrity, and trust will flourish.” Messages 1, 2, and 4 are byte-for-byte identical to Variant 2.



### Ivar Frisch — 2026-06-23T18:55:52.968Z

Comment `AAAB-PG_MeU`; resolved: False. Quoted anchor: system prompt

You are an agent participating in a multi-task experiment. You will play a game and may also be asked to write myths.
GAME:
You will play different roles across multiple rounds.
When you are the SENDER:
- You receive $5 each round
- You decide how much to SEND to the RECEIVER ($0-$5)
- Amount sent is multiplied by 3x
- Receiver decides how much to RETURN
- You keep: $5 - sent + returned
- Receiver keeps: received - returned
- Response format: {'send': <amount>}
When you are the RECEIVER:
- Sender receives $5
- Sender decides how much to SEND to you ($0-$5)
- Amount sent is multiplied by 3x
- You decide how much to RETURN
- Sender keeps: $5 - sent + returned
- You keep: received - returned
- Response format: {'return': <amount>}
MYTH WRITING:
You may also be asked to write short myths (stories) on various topics. When writing myths, follow the instructions provided in each prompt.

IMPORTANT: Provide your decision in the correct JSON format.

### Ivar Frisch — 2026-06-23T18:59:07.279Z

Comment `AAAB-PG_MeY`; resolved: False. Quoted anchor: (the round-1 game prompt, sender role):

If the agent draws the receiver role in round 1, message 4 is instead Round 1: You are the RECEIVER. the sender sent $X, that is Y% of their total endowment. You received $Z. How much do you return to the sender? (0-Z).

## Slide 673

[Open source slide](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3efb86592f1_0_16)

### Current slide text

Next steps
run option b ablation: instead of re-injecting myth each round, let it roll out. 
what memory would we need for this? Messages in memory
[0] system
[1] seed_user_prompt (myth prompt) – round 1
[2] seed_myth  							– round 1                				
[3] Game prompt 						– round 1
[4] Game response assistant  			– round 1
[5] seed_user_prompt (myth prompt) – round 2
[6] myth response assistant 			– round 2
[7] game prompt 						– round 2
…
 [N] Game response assistant			– round 3



### Ivar Frisch — 2026-06-29T07:50:26.334Z

Comment `AAACAKj5CII`; resolved: False. Quoted anchor:  seed_myth  

← Injected once

### Ivar Frisch — 2026-06-29T07:53:48.304Z

Comment `AAACAKj5CIM`; resolved: False. Quoted anchor: run option b ablation: instead of re-injecting myth each round, let it roll out. 
what memory would we need for this? Messages in memory
[0] system
[1] seed_user_prompt (myth prompt) – round 1
[2] seed_myth  							– round 1                				
[3] Game prompt 						– round 1
[4] Game response assistant  			– round 1
[5] seed_user_prompt (myth prompt) – round 2
[6] myth response assistant 			– round 2
[7] game prompt 						– round 2
…
 [N] Game response assistant			– round 3


What about the memory we normally give it in the prompts? 

I think just omit this --> this would require re-running non-ablation experiments.

## Slide 676

[Open source slide](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3f500be06db_1_13)

### Current slide text

(No extracted text; slide may contain images.)

### Edward Hughes — 2026-07-13T09:43:09.141Z

Comment `AAAB_9gqYVg`; resolved: False. Quoted anchor: (none)

"Figure 2"

needs redoing with 

Gemini + GPT

(and potentially the no noise, noise, noise[informed] settings)

**Reply — Edward Hughes, 2026-07-13T09:43:20.466Z** (reply):

on both 2 agent and 8 agent games

**Reply — Edward Hughes, 2026-07-13T09:43:31.407Z** (reply):

we can skip the "normative directive"

**Reply — Ivar Frisch, 2026-07-13T09:46:20.327Z** (reply):

different colors for the different models, so it will be more like like plot 677

## Slide 677

[Open source slide](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3f500be06db_0_1)

### Current slide text

(No extracted text; slide may contain images.)

### Edward Hughes — 2026-07-13T09:44:58.920Z

Comment `AAAB_9gqYVs`; resolved: False. Quoted anchor: (none)

This is another way of presenting the data from the previous slide that we might use instead (or in Appendix).

**Reply — Edward Hughes, 2026-07-13T09:46:54.872Z** (reply):

We want this plot as "Figure 2" but rerun with the latest settings of prompts on 

- Claude
- GPT
- Gemini

and on 

- 2 agent
- 8 agent

**Reply — unavailable author, 2026-07-13T09:51:49.523Z** (reply):

(empty/deleted)

**Reply — Edward Hughes, 2026-07-13T09:51:52.087Z** (reply):

sonnet-4.8, gpt-mini-5.5

**Reply — Edward Hughes, 2026-07-13T09:52:03.220Z** (reply):

gemini: have a think!

## Slide 682

[Open source slide](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3f54dbf92f4_0_0)

### Current slide text

Plots after fixing double memory bug


## Slide 683

[Open source slide](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3f54dbf92f4_0_5)

### Current slide text

(No extracted text; slide may contain images.)

### Ivar Frisch — 2026-07-17T20:34:52.643Z

Comment `AAACDQbTDnU`; resolved: False. Quoted anchor: (none)

2 dyad, claude sonnet 4.5, bidirectional noise applied (not informed), anonymous, own last 3 games + coplayers last 3 games

## Slide 684

[Open source slide](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3f6b3d56849_1_0)

### Current slide text

(No extracted text; slide may contain images.)

### Ivar Frisch — 2026-08-10T09:14:07.038Z

Comment `AAACFZeo-0U`; resolved: False. Quoted anchor: (none)

2 dyad, claude sonnet 4.5, informed noise, anonymous, own last 3 games + coplayers last 3 games

## Slide 702

[Open source slide](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3f8443b4c31_0_0)

### Current slide text

decisions (24th August)

make negative-only noise the default. Rerun 695 with negative-only noise (Aron)
defector agent runs (what is the structure of this) (Aron)
8 agent run, 2 were automatic defectors (try 4)
2 agent run, 25% of the time (at random), defection in that round (try 50%)
what can we do about the return amount being always 0.5?
what’s the percent returned across models (across rounds) (Ivar)

Next week: put Figures into Overleaf. 

