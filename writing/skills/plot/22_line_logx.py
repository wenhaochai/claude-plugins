"""Template 22: single-line plot on log-x scale.

Use when: a metric saturates as you sweep x over orders of magnitude (data
fraction, training tokens, etc.). Single line + circle markers reads cleanly.
"""
import numpy as np
import matplotlib.pyplot as plt
from style import apply_style, paper, arrow, G_BLUE

apply_style()

X = np.array([0.1, 0.5, 1.0, 10.0, 15.0, 25.0])
Y = [1.80, 1.40, 1.22, 1.25, 1.20, 1.23]

color = paper(G_BLUE)

fig, ax = plt.subplots(figsize=(4.0, 2.8), constrained_layout=True)

ax.plot(X, Y, color=color, marker='o', linewidth=1.6, markersize=7,
        markerfacecolor=color, markeredgecolor='white', markeredgewidth=0.8)
ax.set_xscale('log')
ax.set_xlabel('Subset (%)')
ax.set_ylabel(arrow('Metric A', 'down'))
ax.set_xticks([0.1, 0.5, 1, 10, 15, 25])
ax.set_xticklabels(['0.1', '0.5', '1', '10', '15', '25'])
ax.grid(linestyle='--', alpha=0.4)
