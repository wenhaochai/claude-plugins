"""Two-line budget sweep with round markers, announcement-clean look.

Layout transferred from OpenAI's blog charts (GPT-5.6 era): white field,
no grid, left+bottom spines only, dot legend above the axes, thick lines
with solid round markers, one hue at two lightness levels via `twotone`.
Recolored to the Google palette + Palatino. Swap `G_BLUE` for any palette
color; both series recolor together.
"""

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, PercentFormatter

from style import apply_style, G_BLUE, twotone

apply_style()

# --- data (illustrative — replace) ------------------------------------------
series = {
    'Model A': ([2.0e3, 3.4e3, 7.0e3, 11.0e3, 15.3e3],   # x: budget sweep
                [39.0, 61.0, 75.5, 79.5, 83.0]),          # y: metric
    'Model B': ([4.9e3, 6.3e3, 9.1e3, 13.5e3, 16.0e3],
                [34.5, 62.0, 66.5, 74.0, 74.5]),
}

dark, light = twotone(G_BLUE, 'brand')   # lines want full-strength color
INK = '#1a1a1a'

fig, ax = plt.subplots(figsize=(4.8, 3.5))
ax.grid(False)

for (name, (xs, ys)), color, z in zip(series.items(), (dark, light), (3, 2)):
    ax.plot(xs, ys, color=color, linewidth=2.6, marker='o', markersize=8,
            solid_capstyle='round', zorder=z)

# announcement-clean axes: L-shaped spines, outward ticks, no grid
for side in ('top', 'right'):
    ax.spines[side].set_visible(False)
for side in ('left', 'bottom'):
    ax.spines[side].set_color(INK)
    ax.spines[side].set_linewidth(0.9)
ax.tick_params(colors=INK)

ax.set_xlim(0, 16.5e3)
ax.set_xticks(range(0, 16_001, 4_000))
ax.xaxis.set_major_formatter(
    FuncFormatter(lambda v, _: f'{v / 1000:g}k' if v else '0'))
ax.set_yticks([40, 60, 80])
ax.yaxis.set_major_formatter(PercentFormatter(decimals=0))
ax.set_xlabel('Output tokens')      # illustrative sweep axis — replace
ax.set_ylabel('Metric A')

# dot legend above the axes, flush left
handles = [
    Line2D([], [], marker='o', linestyle='', markersize=8, color=c, label=n)
    for n, c in zip(series, (dark, light))
]
ax.legend(handles=handles, loc='lower left', bbox_to_anchor=(0, 1.0),
          ncol=len(series), frameon=False, handletextpad=0.4,
          columnspacing=1.4, borderaxespad=0)
