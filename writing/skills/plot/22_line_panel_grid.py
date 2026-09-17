"""Small-multiples curve grid: one metric per row, one setting per column.

Every panel shares its row's y-axis and its column's x-axis, so a reader compares
down a column without re-reading an axis. One figure-level header carries the
series identity for all fifteen panels; a per-panel legend would repeat it
fifteen times. Row labels sit on the leftmost panel only.

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
COLUMNS = ['Setting A', 'Setting B', 'Setting C', 'Setting D', 'All settings']
ROWS = ['Metric A', 'Metric A slope', 'Metric B']

rng = np.random.default_rng(5)
X = np.logspace(5, 8, 24)                      # 100K to 100M, log x


def curve(row, k):
    """A plausible shape per row: rising, noisy-flat, rising."""
    t = np.linspace(0, 1, X.size)
    if row == 1:
        return 380 + rng.normal(0, 150, X.size).cumsum() * 0.25 + k * 40
    base = 1000 + 1200 * t ** (0.8 + 0.12 * k)
    return base + rng.normal(0, 22, X.size).cumsum() * 0.3


fig, axes = plt.subplots(3, 5, figsize=(WIDTH_1COL, 3.3),
                         sharex=True, sharey='row')

for r in range(3):
    for c in range(5):
        ax = axes[r][c]
        for k, (label, color) in enumerate(SERIES):
            y = curve(r, k)
            ax.plot(X, y, color=color, linewidth=1.0)
            if r != 1:
                ax.fill_between(X, y * 0.97, y * 1.03, color=color,
                                alpha=0.14, linewidth=0)
        if r == 1:
            ax.axhline(400, color=REF_GREY, linestyle=REF_DASH, linewidth=0.8)
        else:
            ax.plot(X, 1000 + 1200 * np.linspace(0, 1, X.size), color=REF_GREY,
                    linestyle=REF_DASH, linewidth=0.8)
        ax.set_xscale('log')
        ax.tick_params(labelsize=6.0, length=2.2)
        if r == 0:
            header(ax, COLUMNS[c], size=PANEL_PT)
        if c == 0:
            ax.set_ylabel(ROWS[r], fontsize=6.6)
        if r == 2:
            ax.set_xlabel('Budget', fontsize=6.6)
        ax.set_xticks([1e5, 1e6, 1e7, 1e8])
        ax.set_xticklabels(['100K', '1M', '10M', '100M'], fontsize=5.6)

fig_header(fig, 'Every metric, every setting',
           [(label, color) for label, color in SERIES] +
           [('Reference', REF_GREY, '--')])
finalize_headers(fig, level_all=False)
