"""Grouped two-series vertical bar with error bars, announcement-clean look.

Layout transferred from OpenAI's blog charts (LifeSciBench era): white field,
no grid, left+bottom spines only, dot legend above the axes, one hue at two
lightness levels via `twotone`. Recolored to the Google palette + Palatino.
Swap `G_GREEN` for any palette color; both series recolor together.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import PercentFormatter

from style import apply_style, G_GREEN, darken, rounded_bar, twotone

apply_style()

# --- data (illustrative — replace) ------------------------------------------
categories = ['Task A', 'Task B', 'Task C', 'Task D', 'Task E']
series = {
    'Model A': ([37.0, 30.5, 40.0, 39.5, 59.0],   # mean
                [8.5, 6.5, 8.0, 5.5, 12.0]),       # symmetric error
    'Model B': ([29.0, 23.5, 28.5, 28.5, 40.5],
                [7.5, 6.0, 7.0, 5.0, 11.5]),
}

dark, light = twotone(G_GREEN, 'medium')   # bars want the medium tier
edge = darken(dark, 0.25)                  # outlines sit deeper than the dark bar
INK = '#1a1a1a'

fig, ax = plt.subplots(figsize=(6.0, 3.4))
ax.grid(False)

x = np.arange(len(categories))
w = 0.34                                    # bar width; pair gap = 0.04
ax.set_xlim(-0.6, len(categories) - 0.4)    # fix limits BEFORE rounded_bar
ax.set_ylim(0, 100)
(mean_a, err_a), (mean_b, err_b) = series.values()
for cx, h in zip(x - w / 2 - 0.02, mean_a):
    rounded_bar(ax, cx, h, w, facecolor=dark, linewidth=0)
for cx, h in zip(x + w / 2 + 0.02, mean_b):
    rounded_bar(ax, cx, h, w, facecolor=light, edgecolor=edge, linewidth=0.9)
err_kw = dict(fmt='none', elinewidth=1.0, capsize=3, capthick=1.0,
              ecolor=INK, zorder=4)
ax.errorbar(x - w / 2 - 0.02, mean_a, yerr=err_a, **err_kw)
ax.errorbar(x + w / 2 + 0.02, mean_b, yerr=err_b, **err_kw)

# announcement-clean axes: L-shaped spines, outward ticks, no grid
for side in ('top', 'right'):
    ax.spines[side].set_visible(False)
for side in ('left', 'bottom'):
    ax.spines[side].set_color(INK)
    ax.spines[side].set_linewidth(0.9)
ax.tick_params(colors=INK)

ax.set_yticks(np.arange(0, 101, 20))
ax.yaxis.set_major_formatter(PercentFormatter(decimals=0))
ax.set_ylabel('Metric A (%)')
ax.set_xticks(x, categories, rotation=30, ha='right', rotation_mode='anchor')

# dot legend above the axes, flush left
handles = [
    Line2D([], [], marker='o', linestyle='', markersize=7, color=c, label=n)
    for n, c in zip(series, (dark, light))
]
ax.legend(handles=handles, loc='lower left', bbox_to_anchor=(0, 1.0),
          ncol=len(series), frameon=False, handletextpad=0.4,
          columnspacing=1.4, borderaxespad=0)
