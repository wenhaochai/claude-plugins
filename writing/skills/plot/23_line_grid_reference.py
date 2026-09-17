"""One panel per setting, each curve family measured against the same reference.

A 2x2 grid where every panel plots the same series on a log-x budget axis against
one shared dashed reference, so the question in every panel is identical: which
series beat the reference, and where did they cross it. The figure carries one
legend; the panels carry only their own title.

Contains no measured results; the curves below come from a fixed seed.
Output: 5.5 in wide, placed at 1:1.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from style import (apply_style, fig_header, header, finalize_headers,
                   G_BLUE, G_RED, G_YELLOW, G_GREEN, REF_GREY, REF_DASH,
                   PANEL_PT, WIDTH_1COL, paper)

apply_style()
SERIES = [('Model A', paper(G_YELLOW)), ('Model B', paper(G_BLUE)),
          ('Model C', paper(G_RED)), ('Model D', paper(G_GREEN))]
PANELS = ['Setting A', 'Setting B', 'Setting C', 'Setting D']

rng = np.random.default_rng(3)
X = np.logspace(5, 8, 30)
T = np.linspace(0, 1, X.size)
REFERENCE = 1000 + 1250 * T          # the same line in every panel

fig, axes = plt.subplots(2, 2, figsize=(WIDTH_1COL, 3.4),
                         sharex=True, sharey=True)

for ax, panel in zip(axes.flat, PANELS):
    for k, (label, color) in enumerate(SERIES):
        y = 1000 + 1250 * T ** (0.75 + 0.14 * k) + rng.normal(0, 18, X.size).cumsum() * 0.35
        ax.plot(X, y, color=color, linewidth=1.15)
    ax.plot(X, REFERENCE, color=REF_GREY, linestyle=REF_DASH, linewidth=0.9)
    ax.set_xscale('log')
    ax.set_xticks([1e5, 3e5, 1e6, 3e6, 1e7, 3e7, 1e8])
    ax.set_xticklabels(['100K', '300K', '1M', '3M', '10M', '30M', '100M'], fontsize=5.8)
    ax.set_ylim(900, 2400)
    ax.tick_params(length=2.4)
    header(ax, panel, size=PANEL_PT)

for ax in axes[:, 0]:
    ax.set_ylabel('Metric A')
for ax in axes[1, :]:
    ax.set_xlabel('Budget')

fig_header(fig, 'Every setting against the same reference',
           [(label, color) for label, color in SERIES] +
           [('Reference', REF_GREY, '--')])
finalize_headers(fig, level_all=False)
