# Image descriptions for commented slides 1–640

Inspected the saved original image files on 2026-09-15. These describe what the historical figures display, not independently verified results. Eleven comment-bearing slides contain twelve image objects; eight other comment-bearing slides have no image object in the retrieved resource. Native slide text and full comments belong alongside these descriptions in the reference. The original image filenames below identify the inspected evidence in `/tmp/design_sources/original_images/`.

## Slide 43

**Image:** `slide043_01.png`. A four-panel figure titled “Trajectory 1 – Numerical Choices,” with transaction flow, per-round payoffs, cumulative balances by agent, and cumulative balances by role. The horizontal axis extends to round 90. After a short initial transition, sent, received and returned amounts settle at 5, 15 and 7.5 respectively; both role payoffs settle at 7.5. The two agents' cumulative balances then rise almost together in straight lines. This is the stable early behavior Ed is responding to when questioning the value of a long run. The image's axis extends beyond the 80 rounds mentioned in his comment; neither is silently substituted for the other.

## Slide 45

**Image:** `slide045_01.png`. A four-panel “Trajectory 1 – Numerical Choices” figure extending to round 100. Transaction flow sits at zero for long stretches, interrupted by isolated spikes in sending, receipt and return. Per-round payoffs vary sharply at those spikes, with some plotted trustee payoffs below zero. Cumulative balances rise unevenly and the two agents change their relative positions. The lower-right panel separates role balances with alternating agent markers. This describes the displayed variability; it does not establish that every plotted action or payoff obeyed the intended rules.

## Slide 48

**Image:** `slide048_01.png`. A four-panel “Trajectory 1 – Numerical Choices” figure extending to round 100. Sends rise over the first few rounds to 5, receipts to 15, and returns to 7.5, after which those traces remain flat. Investor and trustee payoffs converge to 7.5. Agent and role cumulative-balance lines almost overlap and rise steadily. This is the strong, rapidly cooperative baseline behind Ed's concern about little room for an added myth effect.

## Slide 51

**No image object in the retrieved slide.** The native slide heading is “4 Agent Donor Game.” Ed's comments concern that proposed/introduced setting. The following figures and pasted configuration must be read separately; later Aron's-run figures show ten agents.

## Slide 52

**Image:** `slide052_01.png`. A four-panel “Donor Game – Numerical Trajectories” figure with legends for Agent_1 through Agent_4. Panels show donation amounts, generosity as a percentage of resources, resource balances, and net resource flow. Donation amounts and resource balances curve steeply upward near the end, while generosity remains near 25% for most rounds. The net-flow panel has large final-round excursions. **The image extends to round 100, whereas the native slide's pasted configuration says `num_turns: 50`.** This mismatch is unresolved; the chart does not demonstrate that increasing absolute donations reflects increasing generosity.

## Slide 54

**No image object in the retrieved slide.** Its native text introduces “Aron Runs,” with `gpt-4o-mini` and `memory_capacity: 5`. Ed's request to redo with Claude addresses this introduced block, whose following charts have ten-agent legends.

## Slide 56

**Image:** `slide056_01.png`. A four-panel figure titled “game_only – Numerical Trajectories” covering 100 rounds, with ten agents labeled **Agent_1 through Agent_10**. Donation amounts and resource balances grow steeply late in the run. The generosity panel shows fluctuating donation percentages, generally lower later than the earliest rounds, and a dashed 50% reference line. Net resource flows show large positive and negative late excursions. The figure distinguishes rising resources/amounts from generosity percentages; it is not a four-agent chart.

## Slide 63

**Image:** `slide063_01.png`. A four-panel “myth_then_game – Numerical Trajectories” figure with ten-agent legends, **Agent_1 through Agent_10**, over 100 rounds. Absolute donations and resource balances accelerate steeply near the end. Donation percentages fluctuate around a relatively narrow band for much of the run, with an isolated late spike; the net-flow panel also expands sharply late. Ed's cautious comment about possibly increasing generosity refers to an uncertain reading of these percentage trajectories, not proof from the much larger absolute resource totals.

## Slide 210

**No image object in the retrieved slide.** Native text says Claude myths appear in game output/reasoning and points to a named file and line interval. Ivar's comment proposes pattern matching as an explanation. No chart or causal evidence is added by an image here.

## Slide 211

**Image:** `slide211_01.png`. A chart titled “Final Cumulative Balances by Condition,” with Game Only, Game → Myth and Myth → Game on the horizontal axis and final cumulative balance averaged per agent vertically. All three conditions appear as horizontal marks at approximately the same high level; Game Only additionally has a lower isolated point. This is a displayed ceiling-like pattern, without visible evidence here of the theoretical optimum calculation requested in the comment.

## Slide 212

**Image:** `slide212_01.png`. A dark table titled “Cumulative Balances by Condition.” Rows are Game Only, Game → Myth and Myth → Game; columns are labeled GPT-5, Claude Sonnet 4.5 and Gemini 3 Pro. Cells contain means with ± values. Beneath the table, interpretation bullets describe Gemini as highest wealth through maximum trust and half returns, Claude as moderate wealth with balanced reciprocity, and GPT-5 as lowest wealth with minimal cooperation. These are the image author's interpretations. The table's GPT-5 label should not silently override more specific model labels elsewhere in the deck.

## Slide 217

**Image:** `slide217_01.png`. A three-row comparison table with columns Condition, Source, N and Mean Final Balance. Game Only points to `10runs_model_comparison`; both non-cooperative-priming task orders point to `10runs_non_coop_model_comparison`. **The displayed sample counts are 10 for Game Only, 6 for Game → Myth, and 5 for Myth → Game.** Displayed means decrease across those rows. The table does not report standard deviations and is not a completion audit; the folder prefix “10runs” does not establish ten completed observations in every condition.

## Slide 220

**Images:** `slide220_01.png` and `slide220_02.png`. Two cropped transaction-flow charts with sent, received and returned lines over 15 rounds. In the first image, those amounts remain at 5, 15 and 7.5 through round 9, then all become zero at round 10 and stay there. In the second, the first round has those same nonzero amounts, followed by zeros from round 2 onward. The slide's native labels identify Game Myth and Myth Game for the two comparisons. These images show contrasting timing of the displayed collapse; they do not by themselves establish why it happened.

## Slide 222

**No image object in the retrieved slide.** The native heading names Claude Sonnet 4.5/non-cooperative strategy guide; Ivar's comment reports refusal and no change. No plotted refusal-rate evidence is present in an image.

## Slide 224

**No image object in the retrieved slide.** The native text contains a manually inspected game trace, quoted model response and explanations. Comments discuss risk, one-shot reasoning, role/earnings confusion and adding repeated-round wording. These are textual sources and should be reproduced as such.

## Slide 227

**No image object in the retrieved slide.** Native text describes the old noised-observation implementation and informed prompt. The comment flags a possible contradiction between reported returns and the multiplier; its evidence is textual rather than a chart.

## Slide 394

**No image object in the retrieved slide.** The native text asks to compare distributions of cumulative-balance means and variance. Ivar and Mario's thread refers to the plots below this introductory slide, so it should not be paired with an invented chart on slide 394 itself.

## Slide 405

**No image object in the retrieved slide.** The native text is a model reasoning excerpt identifying inconsistent sent/received amounts, over-returns and negative payoffs. Ivar's report and Ed's fix/rerun reply attach to that text. Treat it as a quoted diagnostic trace, not a plot.

## Slide 637

**Image:** `slide637_01.png`. A grouped boxplot titled “Cumulative Balance at Round 10: gpt-5-nano.” The three task-order groups are Game Only, Game → Myth and Myth → Game. Each contains No Noise, Noise and Noise (Informed) boxes with individual points; the vertical axis is mean cumulative balance averaged over both agents. Informed-noise boxes sit higher in each displayed group, with broad scatter and outliers. A bracket and asterisk join two boxes in the Myth → Game group. The image itself does not specify the test or correction behind the asterisk. Ivar's attached comment clarifies that this figure still uses bootstrap/random-replacement noise, not perturbation, despite generic noise labels.
