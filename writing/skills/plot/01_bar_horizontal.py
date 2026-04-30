"""Template 01: horizontal bar chart with value labels + dashed group separators.

Use when: ablation rows where each row adds/removes a component, and you
want value labels at the bar end + visual grouping (baseline / increments /
re-baseline) via dashed separators.
"""
import numpy as np
import matplotlib.pyplot as plt
from style import apply_style, paper, arrow, G_BLUE, G_GREEN, G_YELLOW, G_RED, G_PURPLE

apply_style()

LABELS = ['Setup A', '+ Component 1', '+ Component 2', '+ Component 3', '+ Component 4', 'Setup A (2×)']
VALUES = [1.974, 1.801, 1.657, 1.448, 1.410, 1.669]

# Per-row colors: baseline + 4 distinct components, last row mirrors baseline
PAL_5 = [paper(c) for c in (G_BLUE, G_GREEN, G_YELLOW, G_RED, G_PURPLE)]
COLORS = PAL_5 + [PAL_5[0]]

fig, ax = plt.subplots(figsize=(4.6, 2.8), constrained_layout=True)

ypos = np.arange(len(LABELS))[::-1]  # top → bottom
bars = ax.barh(ypos, VALUES, color=COLORS, edgecolor='#333333', linewidth=0.6, height=0.65)

ax.set_yticks(ypos)
ax.set_yticklabels(LABELS)
ax.set_xlabel(arrow('Metric A', 'down'), fontweight='bold')
ax.bar_label(bars, fmt='%.3f', padding=4, fontsize=10, fontweight='bold')
ax.set_xlim(0, max(VALUES) * 1.18)
ax.grid(axis='x', linestyle='--', alpha=0.4)
ax.grid(axis='y', visible=False)
# Dashed separators around the "baseline" rows (top single + bottom single)
ax.axhline(ypos[0] - 0.5, linestyle='--', color='#888888', linewidth=0.7)
ax.axhline(ypos[-1] + 0.5, linestyle='--', color='#888888', linewidth=0.7)
