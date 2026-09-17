# Slide 678 ablation rerun figure

`slide678_cell_means.png` and `.pdf` reproduce the original slide-678 chart
design using the 35 validated rerun finals. Bars show the mean final joint
balance, error bars show the sample SD, and black points show the five individual
donor/run replicates. The dotted line is the rerun baseline mean; the dashed line
is the $600 cooperation ceiling.

Generate with:

```sh
python analyses/plot_slide678_rerun.py
```

The script verifies all final-file hashes against
`data/json/noise_experiments/slide678_rerun_20260916/completion_receipt.json`,
requires five complete ten-round finals per cell, and independently derives each
plotted value from the last-round balances. `summary.json` records the receipt
hash, plan hash, values, means, and sample SDs used in the figure.

Interpretation remains descriptive at n=5. Donor identity and stochastic run
variation are combined, and this ablation does not isolate narrative form from
actionable information.
