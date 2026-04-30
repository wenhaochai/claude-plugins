"""Template 00: vertical bar chart with reference baseline + arrow title.

Use when: comparing a metric across discrete methods/models, optionally with
a baseline value to beat (dashed reference line).
"""
import numpy as np
import matplotlib.pyplot as plt
from style import apply_style, paper, lighten, arrow, G_BLUE, G_RED, G_YELLOW, G_GREEN

apply_style()

METHODS = ['Model A', 'Model B', 'Model C', 'Model D', 'Model E', 'Model F', 'Model G']
VALUES = [13.85, 13.85, 13.90, 13.70, 13.78, 13.60, 13.65]
BASELINE = 13.85

# Paired light/dark within each color family — tweak per use case
COLORS = [
    paper(G_BLUE),
    lighten(G_GREEN, 0.45),
    paper(G_GREEN),
    lighten(G_RED, 0.45),
    paper(G_RED),
    lighten(G_YELLOW, 0.32),
    paper(G_YELLOW),
]

fig, ax = plt.subplots(figsize=(5.6, 3.4), constrained_layout=True)

xpos = np.arange(len(METHODS))
ax.bar(xpos, VALUES, color=COLORS, edgecolor='#333333', linewidth=0.6, width=0.78)
ax.axhline(BASELINE, linestyle='--', color='#888888', linewidth=1.0,
           zorder=0, label='Baseline')

ax.set_title(arrow('Metric A', 'down'))
ax.set_ylabel('Value')
ax.set_ylim(11.5, 14.0)
ax.set_xticks(xpos)
ax.set_xticklabels(METHODS, rotation=30, ha='right')
ax.tick_params(axis='x', length=0)
ax.grid(axis='y', linestyle='--', alpha=0.4)
ax.grid(axis='x', visible=False)
ax.legend(loc='best')  # auto-pick the emptiest quadrant
