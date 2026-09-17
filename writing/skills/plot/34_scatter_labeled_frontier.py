"""Capability against cost, with the frontier drawn and its points named.

Two cohorts on a log-x cost axis, each point carrying a vertical error bar, the
running-best frontier traced through them in grey, and a direct label on every
point that sits on it. Direct labels replace a legend of model names: a legend
that lists twelve models is a lookup table, and the reader has to do the join.

Contains no measured results; the points below are drawn to show the layout.
Output: 5.5 in wide, placed at 1:1.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from style import (apply_style, header, finalize_headers, note,
                   G_BLUE, G_RED, REF_GREY, WIDTH_1COL, paper)

apply_style()
COHORT_A, COHORT_B = paper(G_RED), paper(G_BLUE)

# cost (USD per unit of work, log axis), score, +- se, label, cohort, on-frontier
POINTS = [
    (0.016, 92.4, 3.0, 'Model A-lite', 'B', True),
    (0.055, 96.0, 4.4, 'Model A-mini', 'B', False),
    (0.085, 106.5, 4.2, 'Model A', 'B', True),
    (0.105, 112.7, 5.5, 'Model A-pro', 'A', True),
    (0.150, 102.0, 3.6, 'Model B-mini', 'B', False),
    (0.230, 113.0, 6.0, 'Model B', 'B', True),
    (0.260, 86.2, 3.1, 'Model B-lite', 'B', False),
    (0.380, 116.8, 5.0, 'Model C', 'B', True),
    (0.420, 108.5, 4.0, 'Model C-mini', 'A', False),
    (0.560, 113.5, 4.6, 'Model D', 'B', False),
    (0.720, 104.5, 4.2, 'Model D-mini', 'A', False),
    (0.880, 87.6, 3.4, 'Model E-lite', 'A', False),
    (1.900, 122.6, 6.4, 'Model E', 'A', True),
    (3.600, 96.5, 8.0, 'Model F', 'B', False),
    (18.0, 107.4, 4.4, 'Model G-mini', 'A', False),
    (26.0, 112.8, 4.8, 'Model G', 'A', False),
    (62.0, 130.6, 7.2, 'Model H', 'A', True),
]

fig, ax = plt.subplots(figsize=(WIDTH_1COL, 3.0))

frontier = sorted([p for p in POINTS if p[5]])
ax.plot([p[0] for p in frontier], [p[1] for p in frontier],
        color=REF_GREY, linewidth=2.0, zorder=1, solid_capstyle='round')

for cost, score, se, label, cohort, on_front in POINTS:
    color = COHORT_A if cohort == 'A' else COHORT_B
    ax.errorbar(cost, score, yerr=se, fmt='o', markersize=4.2, color=color,
                markeredgecolor='white', markeredgewidth=0.6,
                elinewidth=0.9, capsize=0, zorder=3)
    if on_front:            # only the frontier earns a name
        note(ax, cost, score + se + 1.4, label, color=color)

ax.set_xscale('log')
ax.set_xlim(0.010, 110)
ax.set_ylim(78, 142)
ax.set_xticks([0.01, 0.1, 1, 10, 100])
ax.set_xticklabels(['$0.01', '$0.10', '$1', '$10', '$100'])
ax.set_xlabel('Cost per unit of work (USD, log scale)')
ax.set_ylabel('Capability index')

header(ax, 'Capability against cost',
       [('Cohort A', COHORT_A), ('Cohort B', COHORT_B),
        ('Best at this cost', REF_GREY, '-')])
finalize_headers(fig)
