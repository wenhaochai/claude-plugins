"""Template 24: two-line budget sweep with solid round markers,
announcement-chart look. Use when: two models swept over a budget axis
(tokens, compute) on a shared metric; one hue at two lightness levels via
`twotone` — swap `G_BLUE` for any palette color and both series recolor.
"""
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, PercentFormatter

from style import apply_style, header_legend, finalize_headers, G_BLUE, twotone

apply_style()

series = {
    'Model A': ([2.0e3, 3.4e3, 7.0e3, 11.0e3, 15.3e3],   # x: budget sweep
                [39.0, 61.0, 75.5, 79.5, 83.0]),          # y: metric
    'Model B': ([4.9e3, 6.3e3, 9.1e3, 13.5e3, 16.0e3],
                [34.5, 62.0, 66.5, 74.0, 74.5]),
}

dark, light = twotone(G_BLUE, 'brand')   # lines want full-strength color

fig, ax = plt.subplots(figsize=(4.8, 3.5))

for (name, (xs, ys)), color, z in zip(series.items(), (dark, light), (3, 2)):
    ax.plot(xs, ys, color=color, linewidth=2.6, marker='o', markersize=8,
            solid_capstyle='round', zorder=z)

ax.set_xlim(0, 16.5e3)
ax.set_xticks(range(0, 16_001, 4_000))
ax.xaxis.set_major_formatter(
    FuncFormatter(lambda v, _: f'{v / 1000:g}k' if v else '0'))
ax.set_yticks([40, 60, 80])
ax.yaxis.set_major_formatter(PercentFormatter(decimals=0))
ax.set_xlabel('Output tokens')
ax.set_ylabel('Metric A')

header_legend(ax, list(zip(series, (dark, light))))
finalize_headers(fig)
