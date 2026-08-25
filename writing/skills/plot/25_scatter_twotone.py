"""Template 25: scatter of a metric vs compute with baseline + best-recipe
scaling lines, announcement-chart look. Use when: showing a recipe's
compute speedup over a baseline — pale line = baseline ladder, deep line =
best recipe (one hue via `twotone`), grey cloud = every experiment (light
early -> dark late), horizontal arrow = N-times speedup at a fixed metric.
Log x, faint vertical-only grid. Swap `G_BLUE` for any palette color.
"""
import numpy as np
import matplotlib.pyplot as plt

from style import apply_style, header_legend, finalize_headers, G_BLUE, twotone

apply_style()

# (flops, metric) rungs; lower metric is better.
baseline = [(3e17, 21.0), (1e18, 17.4), (4e18, 14.6), (1.5e19, 12.4)]  # pale line
recipe   = [(3e17, 18.6), (1e18, 15.2), (4e18, 12.7), (1.5e19, 10.8)]  # deep line
cloud = [  # (flops, metric, run_order 0..1)
    (5e17, 20.1, 0.05), (8e17, 18.9, 0.15), (2e18, 16.8, 0.30),
    (3e18, 15.6, 0.42), (6e18, 14.1, 0.58), (9e18, 13.3, 0.72),
    (1.2e19, 12.6, 0.85), (7e17, 19.4, 0.22), (2.5e18, 16.1, 0.50),
]
speedup = 2.3   # best-recipe compute speedup at fixed metric

dark, light = twotone(G_BLUE, 'brand')
base_color, champ_color = light, dark

fig, ax = plt.subplots(figsize=(5.0, 3.6), constrained_layout=True)

# faint vertical-only grid, drawn first so points sit on top
ax.grid(axis='x', which='major', linestyle='--', alpha=0.28, color='0.7', zorder=0)

# grey experiment cloud: early runs light, late runs dark
for f, v, order in cloud:
    g = 0.90 * (1 - order)
    ax.scatter([f], [v], s=32, color=(g, g, g), edgecolor='white',
               linewidth=0.25, alpha=0.85, zorder=2)

# two scaling lines + their rung markers
bx, by = zip(*baseline)
rx, ry = zip(*recipe)
ax.plot(bx, by, '-', color=base_color, linewidth=2.6, alpha=0.95,
        solid_capstyle='round', zorder=3)
ax.plot(rx, ry, '-', color=champ_color, linewidth=2.6, alpha=0.98,
        solid_capstyle='round', zorder=5)
ax.scatter(bx, by, s=54, color=base_color, edgecolor='white', linewidth=0.6, zorder=4)
ax.scatter(rx, ry, s=60, color=champ_color, edgecolor='white', linewidth=0.6, zorder=6)

# horizontal N-times speedup arrow at a mid metric level (head = compute-saving side)
Lmid = 14.0
cb = float(np.interp(Lmid, by[::-1], bx[::-1]))   # baseline flops at Lmid
cr = float(np.interp(Lmid, ry[::-1], rx[::-1]))   # recipe flops at Lmid
ax.annotate('', xy=(cr, Lmid), xytext=(cb, Lmid),
            arrowprops=dict(arrowstyle='->', color='0.25', lw=1.6,
                            shrinkA=0, shrinkB=0), zorder=7)
ax.text((cb * cr) ** 0.5, Lmid, f'{speedup:.2f}×', fontsize=15,
        fontweight='bold', color='0.12', ha='center', va='bottom', zorder=8)

ax.set_xscale('log')
ax.set_xlabel('Training FLOPs')
ax.set_ylabel('Metric')      # lower is better — replace
ax.margins(y=0.06)

header_legend(ax, [('Baseline', base_color), ('Best Recipe', champ_color),
                   ('Experiments', '0.55')])
finalize_headers(fig)
