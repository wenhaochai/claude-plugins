"""Template 20: multi-line plot with markers (linear xy).

Use when: tracking a metric across a hyperparameter sweep for multiple model
variants. Two model families × two variants = 4 lines, paired colors.
"""
import numpy as np
import matplotlib.pyplot as plt
from style import apply_style, paper, lighten, arrow, G_BLUE, G_YELLOW

apply_style()

X = np.array([1, 4, 16, 32, 64])

SERIES = {
    'a1': dict(y=[19.5, 15.4, 14.85, 14.78, 14.7],  color=lighten(G_BLUE, 0.45),  marker='s', label='Model A v1'),
    'a2': dict(y=[19.7, 15.3, 14.78, 14.72, 14.75], color=paper(G_BLUE),          marker='o', label='Model A v2'),
    'b1': dict(y=[19.5, 15.65, 15.40, 15.50, 14.95], color=lighten(G_YELLOW, 0.32), marker='^', label='Model B v1'),
    'b2': dict(y=[19.85, 16.0, 15.25, 15.95, 16.05], color=paper(G_YELLOW),       marker='D', label='Model B v2'),
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
ax.legend(loc='upper right')
ax.grid(linestyle='--', alpha=0.4)
