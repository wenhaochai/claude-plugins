"""Template 04: horizontal two-segment stacked bar, announcement-chart
look. Use when: each row splits into two exhaustive parts (e.g. false vs
true rejections) and the split share matters more than the totals; one hue
at two lightness levels via `twotone`, share label inside the dark
segment, total count at the row end.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

from style import (apply_style, header_legend, finalize_headers,
                   G_BLUE, INK, darken, twotone)

apply_style()

rows = ['Cause A', 'Cause B', 'Cause C', 'Cause D', 'Cause E', 'Cause F']
totals = [1063, 784, 426, 385, 241, 112]          # row totals
part_pcts = [15.6, 21.2, 15.7, 21.6, 24.1, 19.6]  # light-segment share (%)

dark, light = twotone(G_BLUE, 'medium')
edge_d, edge_l = darken(dark, 0.25), darken(light, 0.25)
stroke_white = [pe.withStroke(linewidth=2.0, foreground='white')]

part = np.array(totals) * np.array(part_pcts) / 100.0
rest = np.array(totals) - part

fig, ax = plt.subplots(figsize=(6.4, 3.2), constrained_layout=True)

y = np.arange(len(rows))
ax.barh(y, part, height=0.55, color=light, edgecolor=edge_l,
        linewidth=0.85, zorder=3)
ax.barh(y, rest, left=part, height=0.55, color=dark, edgecolor=edge_d,
        linewidth=0.85, zorder=3)

# share label inside the dark segment, total at the row end
for i, (tot, p) in enumerate(zip(totals, part)):
    ax.text(p + (tot - p) / 2, i, f'{100 - part_pcts[i]:.1f}%',
            va='center', ha='center', fontsize=9, color='white',
            fontweight='bold', zorder=4)
    ax.text(tot + max(totals) * 0.012, i, f'{tot:,}', va='center',
            ha='left', fontsize=9, color=INK,
            path_effects=stroke_white, zorder=4)

ax.set_yticks(y, rows)
ax.invert_yaxis()
ax.set_xlabel('Count')
ax.set_xlim(0, max(totals) * 1.14)
ax.set_title('Metric A Split by Cause')

header_legend(ax, [('Segment A', light, 's'), ('Segment B', dark, 's')])
finalize_headers(fig)
