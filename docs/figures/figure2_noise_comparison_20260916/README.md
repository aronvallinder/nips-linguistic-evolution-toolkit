# Figure 2 noise comparisons

All 270 source hashes and final states verified. No defector conditions.
Each observation is round-10 cumulative actual resources averaged over agents
in one run. Boxes summarize five runs; dots show all five observations.
Delta bars are median(myth runs) minus median(game-only runs), not the median
of paired differences. Intervals use exact paired empirical bootstrap (3125
resamples), preserving replicate/seed blocks. With five replicates they are
exploratory and not multiplicity-adjusted. A collapsed interval is not proof
of no effect beyond this sample.

Two-agent panels are fixed dyads; eight-agent panels rotate partners and include
current-partner history. Differences between panels cannot isolate agent count.
Noise is negative-only communication distortion, range one on sends and returns.
The informed condition reuses September control finals. Implementation differences
are the earlier condition-validator fix and the provider billing-retry fix;
all other recorded implementation hashes match. Exact noise-matched comparison
inputs were checked within each model/population/order/replicate block.
Two Claude population myth-first runs were resampled after role-key errors;
GPT partial attempts stopped on exhausted credits and unfinished runs were rerun.
Successful finals only are plotted. See researchlog 2026-09-16 for the run history.

PNG, SVG and PDF versions are supplied with source values and median deltas.
