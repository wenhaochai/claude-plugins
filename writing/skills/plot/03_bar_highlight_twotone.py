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
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt

from style import apply_style, G_BLUE, darken, lighten, rounded_bar, twotone

apply_style()

# --- data (illustrative — replace) ------------------------------------------
models = ['Model A', 'Model B', 'Model C', 'Model D']
values = [92.1, 90.1, 88.3, 85.0]
HERO = 0                                    # index of the highlighted bar
YMIN, YMAX = 60, 100                        # non-zero baseline zooms the gap

dark, light = twotone(G_BLUE, 'medium')    # bars want the medium tier
edge = darken(dark, 0.25)                  # outlines sit deeper than the hero
dark = lighten(dark, 0.20)                 # fills sit a notch lighter; edge stays
INK = '#1a1a1a'

fig, ax = plt.subplots(figsize=(4.4, 3.4))
ax.grid(False)

x = np.arange(len(models))
w = 0.90                                    # near-touching bars
ax.set_xlim(-0.52, len(models) - 0.48)      # fix limits BEFORE rounded_bar
ax.set_ylim(YMIN, YMAX)
for i, (cx, v) in enumerate(zip(x, values)):
    if i == HERO:
        rounded_bar(ax, cx, v, w, r_frac=0.07, facecolor=dark,
                    edgecolor=edge, linewidth=0.9)
    else:
        rounded_bar(ax, cx, v, w, r_frac=0.07, facecolor=light,
                    edgecolor=edge, linewidth=0.9)
    ax.text(cx, v + (YMAX - YMIN) * 0.03, f'{v:.2f}%', ha='center',
            fontsize=11.5, color=INK)

# announcement-clean axes: bottom spine only, floating y labels, no grid
for side in ('top', 'right', 'left'):
    ax.spines[side].set_visible(False)
ax.spines['bottom'].set_color(INK)
ax.spines['bottom'].set_linewidth(0.9)
ax.tick_params(colors=INK)
ax.tick_params(axis='y', length=0)

ax.set_yticks(np.arange(YMIN, YMAX, 10))    # top tick dropped: title sits there
ax.set_ylabel('Metric A (%)')
ax.set_xticks(x, models, rotation=30, ha='right', rotation_mode='anchor')
# fontweight='bold' is a no-op here: macOS Palatino.ttc exposes only the
# regular face to matplotlib, so a thin same-color stroke fakes the bold.
ax.text(0, 1.0, 'Benchmark A', transform=ax.transAxes, ha='left',
        va='center', fontsize=14, color=INK,
        path_effects=[pe.withStroke(linewidth=0.8, foreground=INK)])
