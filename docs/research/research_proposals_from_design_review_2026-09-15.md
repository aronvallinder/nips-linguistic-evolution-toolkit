# Research proposals from the design review

Saved: 2026-09-15.

**Status: assistant proposals, not agreed design decisions or authorization to run experiments.** Saved at Ivar's request from sections 1–5 of the discussion. Ivar clarified that his preceding question primarily concerned the project's memory and reference system; these research suggestions are retained separately for future consideration. No settings were changed or experiments launched.

Context: [experiment-design reference](../experiment_design_reference.md) and [data audit](mixed_future_data_audit.md). Assessments below reflect the evidence reviewed on this date.

## 1. Make the paper's claim more precise

Separate three claims explicitly:

| Claim | Assessment |
|---|---|
| Writing or receiving myths can change cooperation. | Supported in particular tested settings; effects differ across models. |
| Experience-derived myth content helps another agent cooperate. | Promising historical transplant evidence; needs a clean comparison under the current setup. |
| Useful cooperative culture emerges and persists through transmission. | The larger ambition, still unresolved. |

That gives the paper a clear progression without requiring every experiment to establish “cultural evolution.” The current audit supports this distinction. [Evidence assessment](mixed_future_data_audit.md#historical-evidence-map-what-has-already-been-tried)

**Suggested central question:**

> Can narratives distilled from social experience transfer useful cooperative behavior to other agents, and what determines whether that transfer succeeds?

This connects the original storytelling idea, Ed's interest in strangers, and the transplant experiments.

## 2. Prioritize one clean content experiment

**This would be the first experimental priority**, ahead of another broad sweep.

Take a saved decision context and compare what happens when the agent receives:

- An authentic myth from a previous run.
- A plain-language strategy summary carrying approximately the same information.
- A version of the myth with its actionable social information removed.
- Unrelated text of similar length.
- No added text.

Keep the game history, partner information, model settings, and decision prompt fixed.

This would distinguish several explanations:

- Stories provide useful information.
- Narrative form contributes something beyond explicit advice.
- The effect comes from generic cooperative encouragement.
- Additional context or a preliminary writing step changes behavior.

Use **multiple independently generated source myths**, with a selection rule fixed beforehand. Otherwise, a striking result could depend on one unusually effective story. Matching information across a myth and its prose summary also needs checking; it cannot simply be assumed.

First measure immediate decisions in matched contexts, then test the most informative contrast during free play. The historical transplant results give this experiment a strong basis. [Transplant evidence](mixed_future_data_audit.md#independently-reproduced-historical-seed-outcomes), [proposed controls](mixed_future_data_audit.md#implications-for-the-five-experiment-shortlist)

## 3. Turn “cooperation with strangers” into a direct test

Removing names is useful, but it does not directly test whether knowledge transfers beyond familiar relationships.

Introduce **newcomers who never interacted with the original myth writers**. Give them either:

- Inherited myths.
- Matched factual or strategic summaries.
- No inherited material.

Then let them interact with new partners under matched conditions.

The key question becomes:

> Does experience acquired by one group benefit another group through the material it leaves behind?

Only after establishing that, add several generations of replacement and ask whether useful information survives or improves. That would make the connection to cultural transmission much more concrete.

This follows Ed's stated motivation and his preference for first isolating an arriving stranger's exposure to an injected myth. [Recovered decisions](../experiment_design_reference.md#june-september-decisions-and-corrections)

## 4. Treat task order as its own research question

The “founding myth” interpretation deserves a focused test.

Separate:

- **An initial myth only**, followed by ordinary play.
- **Continued myth writing and exchange** throughout play.
- **A matched initial reflection or strategy-writing step.**
- Game only.

That asks whether the advantage comes from a cooperative starting point, continuing story exchange, or simply considering a strategy before acting.

If one initial story explains most of the benefit, that is an interesting result. It would change how we describe the mechanism and how much repeated transmission matters.

The August 24 memory records the team's interest in this interpretation, but that endorsement should remain distinct from a causal demonstration. [Meeting memory](/Users/ivar/.claude/projects/-Users-ivar-Desktop-Research-AI-projects-LLM-evolution-nips-linguistic-evolution-toolkit/memory/project_meeting_2026_08_24.md) (local assistant-written summary; original discussion remains the stronger source).

## 5. Stop expecting one headline effect across all models

Organize the existing results around **different starting behaviors**:

- A model already cooperating maximally has little room to improve.
- A model trapped in defection may benefit from a cooperative starting point.
- A model gradually learning to cooperate may get there faster with myths.

These are potentially different mechanisms, not inconvenient variations around one universal effect.

For the current paper, retain the ceiling results honestly. For a subsequent environment, choose difficulty using a **baseline-only criterion fixed before testing myths**—so we do not select a game because it happens to produce the desired myth effect.

Likewise, distinguish lower resources caused directly by forced defection from changes in how ordinary agents behave. [Current results and limits](mixed_future_data_audit.md#latest-figures-independently-reproduced)
