"""Template 20: multi-line plot with markers (linear xy).

Use when: tracking a metric across a hyperparameter sweep for multiple model
variants. Two model families × two variants = 4 lines, paired colors.
"""
import numpy as np
import matplotlib.pyplot as plt
from style import (apply_style, apply_tier, header_legend, finalize_headers,
                   arrow, G_BLUE, G_GREEN, G_RED, G_YELLOW)

# More than 3 series: distinct Google hues (single-hue ramps stop reading
# past three steps). Use hue_ramp only for figures with <= 3 series.
PAL = [apply_tier(c, 'medium') for c in (G_BLUE, G_RED, G_YELLOW, G_GREEN)]

apply_style()

X = np.array([1, 4, 16, 32, 64])

SERIES = {
    'a1': dict(y=[19.5, 15.4, 14.85, 14.78, 14.7],  color=PAL[0], marker='s', label='Model A v1'),
    'a2': dict(y=[19.7, 15.3, 14.78, 14.72, 14.75], color=PAL[1], marker='o', label='Model A v2'),
    'b1': dict(y=[19.5, 15.65, 15.40, 15.50, 14.95], color=PAL[2], marker='^', label='Model B v1'),
    'b2': dict(y=[19.85, 16.0, 15.25, 15.95, 16.05], color=PAL[3], marker='D', label='Model B v2'),
}

LINE_KW = dict(linestyle='--', linewidth=1.4, markersize=6.5,
               markeredgecolor='white', markeredgewidth=0.6)

fig, ax = plt.subplots(figsize=(4.4, 3.2), constrained_layout=True)

for s in SERIES.values():
    ax.plot(X, s['y'], color=s['color'], marker=s['marker'], label=s['label'], **LINE_KW)

ax.set_xlabel('Hyperparameter (X)')
ax.set_ylabel(arrow('Value', 'down'))
ax.set_title(arrow('Metric A', 'down').replace(r'$\downarrow$', r'($\downarrow$)'))
ax.set_xticks(X)
header_legend(ax, [(s['label'], s['color'], s['marker']) for s in SERIES.values()],
              ncol=2, legend_size=8)
finalize_headers(fig)
