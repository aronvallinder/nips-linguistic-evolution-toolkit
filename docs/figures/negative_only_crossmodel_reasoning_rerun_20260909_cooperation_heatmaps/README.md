# Cooperation ratios by round — negative-only informed-noise rerun (2026-09-09)

Same layout as the resources summary heatmap in
`docs/figures/figure2_noise_comparison_20260916/`, but the columns are rounds
1–10 instead of noise conditions. All 270 finals of the 2026-09-09 rerun were
hash-checked against its `provenance.json`; every run is negative-only
communication noise, range one, agents informed, ten rounds, pinned September
request profiles.

Each cell is the mean over the five runs of a per-round ratio, computed by the
same function as the line plots in `analyses/cooperation_ratio_over_time.py`:

- **Send fraction** = amount sent / $5 endowment, averaged over the selected
  investors that round (1.0 = investors sent everything).
- **Return ratio** = sum(returned) / sum(received) over the selected trustees
  that received more than $0 that round (0.5 = half returned; 1/3 = the
  investor breaks even). Rounds in which nobody received anything are blank.
  The return-ratio colour scale runs 0–0.6 so that the 1/3 and 0.5 landmarks
  are visible; the send-fraction scale runs 0–1.

"Selected" is all agents in the `*_control` figures. In the defector figures
`*_all_agents` includes the defectors' own zero decisions and
`*_ordinary_agents` excludes them. Dyad columns use 25%/50% random defection;
population columns use 2 or 4 designated defectors of 8. Ratios use actual
(post-noise) amounts. Means and standard deviations for every cell are in
`cell_round_values.csv`.

Two-agent panels are fixed dyads; eight-agent panels rotate partners and
provide current-partner history, so the columns do not isolate agent count.
