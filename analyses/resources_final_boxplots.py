#!/usr/bin/env python3
"""Plot final cumulative resources from the exact sources of an existing grid.

Usage: python analyses/resources_final_boxplots.py --provenance <provenance.json> --out <directory>
Each observation is one completed run's mean over selected agents, at round 10.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path

from resources_over_time_max import (
    DEFECTION_COLS, MODEL_ROWS, POP_TITLES, TASK_ORDERS,
    group_cells, parse_condition, per_agent_series,
)
from _shared import load_simulation_runs, write_output_provenance
import matplotlib.pyplot as plt
import numpy as np

# Muted box fills and brighter dots, matching the supplied reference palette.
BOX_COLORS = {'game': '#999999', 'game_myth': '#e99675', 'myth_game': '#72b6a1'}
DOT_COLORS = {'game': '#777777', 'game_myth': '#fc8d62', 'myth_game': '#66c2a5'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provenance', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    provenance = json.loads(args.provenance.read_text())
    sources = [entry['path'] for entry in provenance['runs']]
    for entry in provenance['runs']:
        if hashlib.sha256(Path(entry['path']).read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError(f"Source changed: {entry['path']}")
    options = dict(allowed_differences=provenance['allowed_differences'],
                   legacy_reason=provenance.get('legacy_reason'))
    data_by_path = load_simulation_runs(sources, **options)
    runs = []
    for source, data in data_by_path.items():
        path = Path(source)
        condition = parse_condition(path.parent.name)
        if condition is None:
            raise ValueError(f'Unrecognized condition: {source}')
        run = dict(condition, model=path.parents[2].name,
                   task_order=path.parents[1].name, source_path=source)
        for key in ('all', 'ordinary'):
            run[key] = per_agent_series(data, ordinary_only=key == 'ordinary')
            if run[key] is None or len(run[key]) != 10 or not np.isfinite(run[key]).all():
                raise ValueError(f'Expected ten finite rounds: {source} ({key})')
        runs.append(run)
    args.out.mkdir(parents=True, exist_ok=True)
    rows = []
    for population, key, name in (
        ('dyad', 'all', 'dyad_all_agents_boxplots'),
        ('population', 'all', 'population_all_agents_boxplots'),
        ('population', 'ordinary', 'population_ordinary_agents_boxplots'),
    ):
        cells = group_cells(runs, population, key)
        fig, axes = plt.subplots(3, 3, figsize=(15, 10), sharey=True)
        for i, (model, model_label) in enumerate(MODEL_ROWS):
            for j, (defection, title) in enumerate(DEFECTION_COLS[population]):
                ax = axes[i, j]
                for pos, (order, label, _) in enumerate(TASK_ORDERS, 1):
                    cell = sorted(cells[(model, defection, order)], key=lambda r: r['source_path'])
                    if len(cell) != 5:
                        raise ValueError(f'Expected five runs: {model}, {defection}, {order}: {len(cell)}')
                    values = np.array([r[key][-1] for r in cell])
                    ax.boxplot(values, positions=[pos], widths=.52, patch_artist=True,
                               showfliers=False, whis=1.5,
                               boxprops=dict(facecolor=BOX_COLORS[order], edgecolor='#666666'),
                               medianprops=dict(color='#222222', linewidth=1.6),
                               whiskerprops=dict(color='#666666'), capprops=dict(color='#666666'))
                    ax.scatter(pos + np.linspace(-.10, .10, len(values)), values,
                               s=26, c=DOT_COLORS[order], alpha=.8, edgecolors='white', linewidths=.6, zorder=3)
                    for run, value in zip(cell, values):
                        rows.append(dict(population=population, agents=key, model=model,
                                         defection=defection, task_order=order,
                                         final_cumulative_resources=float(value),
                                         source_path=run['source_path']))
                ax.set_xticks([1, 2, 3], [t[1] for t in TASK_ORDERS], fontsize=10)
                ax.set_xlim(.5, 3.5)
                ax.set_ylim(0, 80)
                ax.set_axisbelow(True)
                ax.grid(axis='y', alpha=.22)
                ax.spines[['top', 'right']].set_visible(False)
                if i == 0:
                    ax.set_title(title, fontsize=13, fontweight='bold', pad=12)
                if j == 0:
                    ax.set_ylabel(model_label, fontsize=12, fontweight='bold')
        agents = 'all agents' if key == 'all' else 'ordinary agents only'
        fig.suptitle(f'Final cumulative resources — {POP_TITLES[population]}\n'
                     f'Negative-only noise · Round 10 · {agents}', fontsize=17, fontweight='bold')
        fig.supylabel('Cumulative resources per agent (mean over selected agents)', fontsize=13)
        fig.text(.5, .018, 'Each dot = one run (n = 5 per box) · Box = middle 50% · Line = median · Whiskers = up to 1.5 × IQR',
                 ha='center', fontsize=11, color='#444444')
        fig.tight_layout(rect=(.025, .05, 1, .93), h_pad=2.2, w_pad=2)
        for suffix in ('png', 'svg'):
            fig.savefig(args.out / f'{name}.{suffix}', dpi=180)
        plt.close(fig)
        print(f'Wrote {name} (PNG + SVG)')
    with (args.out / 'run_values.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    write_output_provenance(args.out, sources, **options)
    print(f'Verified {len(sources)} source hashes; plotted {len(rows)} run/group observations.')


if __name__ == '__main__':
    main()
