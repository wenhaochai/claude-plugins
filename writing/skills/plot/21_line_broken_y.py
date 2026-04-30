"""Template 21: line plot with broken y-axis.

Use when: two groups of curves live on disjoint y-ranges and you want both
visible without one collapsing flat. Implemented as two stacked subplots
sharing x; small diagonal slashes mark the break.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from style import apply_style, paper, lighten, arrow, G_BLUE, G_YELLOW

apply_style()

X = np.array([1, 4, 16, 32, 64])

# Top group (e.g. Model A) sits around 0.50 ± a band
TOP_SERIES = {
    'a1': dict(y=[0.580, 0.503, 0.503, 0.502, 0.500], color=lighten(G_BLUE, 0.45), marker='s', label='Model A v1'),
    'a2': dict(y=[0.550, 0.488, 0.483, 0.485, 0.488], color=paper(G_BLUE),         marker='o', label='Model A v2'),
}
# Bottom group (e.g. Model B) sits around 0.49 with a much tighter range
BOT_SERIES = {
    'b1': dict(y=[0.495, 0.484, 0.485, 0.483, 0.482], color=lighten(G_YELLOW, 0.32), marker='^', label='Model B v1'),
    'b2': dict(y=[0.500, 0.491, 0.488, 0.495, 0.493], color=paper(G_YELLOW),         marker='D', label='Model B v2'),
}

LINE_KW = dict(linestyle='--', linewidth=1.4, markersize=6.5,
               markeredgecolor='white', markeredgewidth=0.6)

fig = plt.figure(figsize=(4.4, 3.4))
gs = GridSpec(2, 1, height_ratios=[1, 1], hspace=0.18,
              left=0.16, right=0.97, top=0.90, bottom=0.14)
ax_top = fig.add_subplot(gs[0])
ax_bot = fig.add_subplot(gs[1])

for s in TOP_SERIES.values():
    ax_top.plot(X, s['y'], color=s['color'], marker=s['marker'], label=s['label'], **LINE_KW)
for s in BOT_SERIES.values():
    ax_bot.plot(X, s['y'], color=s['color'], marker=s['marker'], label=s['label'], **LINE_KW)

ax_top.set_ylim(0.475, 0.605)
ax_bot.set_ylim(0.478, 0.512)
ax_top.set_xticks(X); ax_bot.set_xticks(X)
ax_top.set_xticklabels([])
ax_bot.set_xlabel('Hyperparameter (X)')
ax_top.set_ylabel(arrow('Value', 'down'))
ax_bot.set_ylabel(arrow('Value', 'down'))
ax_top.set_title(arrow('Metric A', 'down').replace(r'$\downarrow$', r'($\downarrow$)'))
ax_top.legend(fontsize=9, loc='upper right')
ax_bot.legend(fontsize=9, loc='upper right')

# Spine break + diagonal slashes
ax_top.spines['bottom'].set_visible(False)
ax_bot.spines['top'].set_visible(False)
ax_top.tick_params(bottom=False, labelbottom=False)
d = .015
kw = dict(color='k', clip_on=False, lw=0.7)
ax_top.plot((-d, +d), (-d, +d), transform=ax_top.transAxes, **kw)
ax_top.plot((1 - d, 1 + d), (-d, +d), transform=ax_top.transAxes, **kw)
ax_bot.plot((-d, +d), (1 - d, 1 + d), transform=ax_bot.transAxes, **kw)
ax_bot.plot((1 - d, 1 + d), (1 - d, 1 + d), transform=ax_bot.transAxes, **kw)
