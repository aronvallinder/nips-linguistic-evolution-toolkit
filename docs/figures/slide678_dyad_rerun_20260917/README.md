# Slide 678 two-agent counterpart figure

This is the same seven-cell chart design as slide 678, using the 35 validated
two-agent counterpart finals. Bars show mean final joint resources, error bars
show sample SD, and black points show the five donor/run replicates. The dyad
ceiling is $150, versus $600 for the eight-agent population.

Generate with:

```sh
python analyses/plot_slide678_rerun.py \
  --run-root data/json/noise_experiments/slide678_dyad_rerun_20260917 \
  --out-dir docs/figures/slide678_dyad_rerun_20260917 \
  --ceiling 150 \
  --population "2-agent fixed dyad" \
  --output-stem slide678_dyad_cell_means
```

The script verifies all final hashes against the completion receipt and derives
the plotted values independently from each final-round balance state.
