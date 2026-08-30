"""Template 28: two metrics with different units on twin y-axes,
announcement-chart look. Use when: two related series share an x sweep but
live on incompatible scales (tokens vs %); left series solid dark, right
series dashed light of the SAME hue (`twotone`), each y-axis label tinted
to its series so the pairing reads without a legend lookup. `clean_axes`
re-frames the twin the rc cannot reach.
"""
import numpy as np
import matplotlib.pyplot as plt

from style import (apply_style, clean_axes, header_legend, finalize_headers,
                   G_BLUE, INK, twotone)

apply_style()

bins = ['0-49', '50-99', '100-249', '250-499', '500-999', '1k-2.5k']
metric_a = [52.1, 74.9, 96.9, 118.7, 137.9, 152.9]   # left axis (k tokens)
metric_b = [0.21, 0.32, 0.55, 0.92, 1.48, 2.11]      # right axis (%)

dark, light = twotone(G_BLUE, 'medium')

fig, ax = plt.subplots(figsize=(5.6, 3.2), constrained_layout=True)

x = np.arange(len(bins))
ax.plot(x, metric_a, color=dark, marker='o', markersize=4.5,
        markeredgecolor='white', markeredgewidth=0.7, linewidth=1.7, zorder=4)
ax.set_xticks(x, bins)
ax.set_xlabel('Step Horizon Bin')
ax.set_ylabel('Metric A (k tokens)', color=dark)
ax.tick_params(axis='y', labelcolor=dark)
ax.set_ylim(40, 160)

tw = ax.twinx()
tw.plot(x, metric_b, color=light, marker='s', markersize=4.2,
        markeredgecolor='white', markeredgewidth=0.7, linewidth=1.7,
        linestyle='--', zorder=4)
tw.set_ylabel('Metric B (%)', color=light)
tw.set_ylim(0, 2.5)
clean_axes(tw)
tw.spines['left'].set_visible(False)
tw.spines['right'].set_visible(True)
tw.spines['right'].set_color(INK)
tw.tick_params(axis='y', labelcolor=light)

ax.set_title('Metric A and Metric B across Horizon')
header_legend(ax, [('Metric A', dark, '-'), ('Metric B', light, '--')])
finalize_headers(fig)
