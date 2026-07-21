"""Scatter of a metric vs compute, with baseline + best-recipe scaling lines.

Layout transferred from OpenAI's release charts, recolored to the Google
palette + Palatino. One brand hue at two lightness levels via `twotone`:
the pale line is the baseline ladder, the deep line is the best recipe.
A grey point cloud (light=early runs -> dark=late runs) shows every
experiment; a horizontal arrow marks the N-times compute speedup of the
best recipe over the baseline at a fixed metric level. Announcement-clean
chrome: L-spine only, faint vertical-only grid, dot legend above the axes.
Log x. Swap `G_BLUE` for any palette color; both lines recolor together.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from style import apply_style, G_BLUE, G_RED, twotone, apply_tier

apply_style()

# --- data (illustrative — replace) ------------------------------------------
# (flops, metric) rungs; lower metric is better. Baseline + best-recipe ladders
# plus a grey cloud of one-off experiments shaded by run order (early -> late).
baseline = [(3e17, 21.0), (1e18, 17.4), (4e18, 14.6), (1.5e19, 12.4)]  # pale line
recipe   = [(3e17, 18.6), (1e18, 15.2), (4e18, 12.7), (1.5e19, 10.8)]  # deep line
cloud = [  # (flops, metric, run_order 0..1)
    (5e17, 20.1, 0.05), (8e17, 18.9, 0.15), (2e18, 16.8, 0.30),
    (3e18, 15.6, 0.42), (6e18, 14.1, 0.58), (9e18, 13.3, 0.72),
    (1.2e19, 12.6, 0.85), (7e17, 19.4, 0.22), (2.5e18, 16.1, 0.50),
]
speedup = 2.3   # illustrative best-recipe compute speedup at fixed metric

dark, light = twotone(G_BLUE, 'brand')
base_color, champ_color = light, dark
INK = '#1a1a1a'

fig, ax = plt.subplots(figsize=(5.0, 3.6), constrained_layout=True)

# faint vertical-only grid, drawn first so points sit on top
ax.grid(False)
ax.grid(axis='x', which='major', linestyle='--', alpha=0.28, color='0.7', zorder=0)

# grey experiment cloud: early runs light, late runs dark
for f, v, order in cloud:
    g = 0.90 * (1 - order)
    ax.scatter([f], [v], s=32, color=(g, g, g), edgecolor='white',
               linewidth=0.25, alpha=0.85, zorder=2)

# two scaling lines + their rung markers
bx, by = zip(*baseline)
rx, ry = zip(*recipe)
ax.plot(bx, by, '-', color=base_color, linewidth=2.6, alpha=0.95,
        solid_capstyle='round', zorder=3)
ax.plot(rx, ry, '-', color=champ_color, linewidth=2.6, alpha=0.98,
        solid_capstyle='round', zorder=5)
ax.scatter(bx, by, s=54, color=base_color, edgecolor='white', linewidth=0.6, zorder=4)
ax.scatter(rx, ry, s=60, color=champ_color, edgecolor='white', linewidth=0.6, zorder=6)

# horizontal N-times speedup arrow at a mid metric level (head = compute-saving side)
Lmid = 14.0
cb = float(np.interp(Lmid, by[::-1], bx[::-1]))   # baseline flops at Lmid
cr = float(np.interp(Lmid, ry[::-1], rx[::-1]))   # recipe flops at Lmid
ax.annotate('', xy=(cr, Lmid), xytext=(cb, Lmid),
            arrowprops=dict(arrowstyle='->', color='0.25', lw=1.6,
                            shrinkA=0, shrinkB=0), zorder=7)
ax.text((cb * cr) ** 0.5, Lmid, f'{speedup:.2f}\u00d7', fontsize=15,
        fontweight='bold', color='0.12', ha='center', va='bottom', zorder=8)

ax.set_xscale('log')
ax.set_xlabel('Training FLOPs')
ax.set_ylabel('Metric')      # lower is better — replace

# announcement-clean axes: L-shaped spines, outward ticks
for side in ('top', 'right'):
    ax.spines[side].set_visible(False)
for side in ('left', 'bottom'):
    ax.spines[side].set_color(INK)
    ax.spines[side].set_linewidth(0.9)
ax.tick_params(direction='out', colors=INK, which='both')
ax.margins(y=0.06)

# dot legend above the axes, flush left: Baseline / Best Recipe / Experiments
handles = [
    Line2D([], [], marker='o', linestyle='', markersize=10, color=base_color, label='Baseline'),
    Line2D([], [], marker='o', linestyle='', markersize=10, color=champ_color, label='Best Recipe'),
    Line2D([], [], marker='o', linestyle='', markersize=10, color='0.55', label='Experiments'),
]
ax.legend(handles=handles, loc='lower left', bbox_to_anchor=(0, 1.0),
          ncol=len(handles), frameon=False, handletextpad=0.4,
          columnspacing=1.4, borderaxespad=0)
