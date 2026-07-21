"""Single-series bar with value labels and one highlighted bar,
announcement-clean look.

Layout transferred from model-release benchmark charts (Loopie AIME era):
white field, no grid, left+bottom spines only, bold left-aligned panel
title, values above each bar, the hero bar dark and the rest light with a
dark outline, non-zero baseline to zoom the comparison. One hue at two
lightness levels via `twotone`; recolored to the Google palette + Palatino.
Swap `G_BLUE` for any palette color.
"""

import numpy as np
import matplotlib.pyplot as plt

from style import apply_style, G_BLUE, rounded_bar, twotone

apply_style()

# --- data (illustrative — replace) ------------------------------------------
models = ['Model A', 'Model B', 'Model C', 'Model D']
values = [92.1, 90.1, 88.3, 85.0]
HERO = 0                                    # index of the highlighted bar
YMIN, YMAX = 60, 100                        # non-zero baseline zooms the gap

dark, light = twotone(G_BLUE, 'medium')    # bars want the medium tier
INK = '#1a1a1a'

fig, ax = plt.subplots(figsize=(4.4, 3.4))
ax.grid(False)

x = np.arange(len(models))
w = 0.84                                    # near-touching bars
ax.set_xlim(-0.55, len(models) - 0.45)      # fix limits BEFORE rounded_bar
ax.set_ylim(YMIN, YMAX)
for i, (cx, v) in enumerate(zip(x, values)):
    if i == HERO:
        rounded_bar(ax, cx, v, w, facecolor=dark, linewidth=0)
    else:
        rounded_bar(ax, cx, v, w, facecolor=light, edgecolor=dark,
                    linewidth=0.9)
    ax.text(cx, v + (YMAX - YMIN) * 0.03, f'{v:.2f}%', ha='center',
            fontsize=11.5, color=INK)

# announcement-clean axes: L-shaped spines, outward ticks, no grid
for side in ('top', 'right'):
    ax.spines[side].set_visible(False)
for side in ('left', 'bottom'):
    ax.spines[side].set_color(INK)
    ax.spines[side].set_linewidth(0.9)
ax.tick_params(colors=INK)

ax.set_yticks(np.arange(YMIN, YMAX + 1, 10))
ax.set_ylabel('Metric A (%)')
ax.set_xticks(x, models, rotation=30, ha='right', rotation_mode='anchor')
ax.set_title('Benchmark A', loc='left', fontsize=14, pad=14)
