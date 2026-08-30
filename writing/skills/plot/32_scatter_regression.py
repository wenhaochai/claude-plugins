"""Template 32: two-cohort scatter with one pooled regression line,
announcement-chart look. Use when: many interval observations from two
settings share one hypothesized linear relation — both clouds in one hue
at two lightness levels (`twotone`), the pooled least-squares fit in a
deeper shade of the same hue.
"""
import numpy as np
import matplotlib.pyplot as plt

from style import (apply_style, header_legend, finalize_headers,
                   G_BLUE, darken, twotone)

apply_style()

rng = np.random.default_rng(3)
# (x, y) observations per cohort; y rises roughly linearly with x
n1, n2 = 150, 118
x1 = rng.uniform(2, 210, n1)
y1 = (4.0 + 0.11 * x1 + rng.normal(0, 3.2, n1)).clip(0)
x2 = rng.uniform(2, 160, n2)
y2 = (5.5 + 0.10 * x2 + rng.normal(0, 3.6, n2)).clip(0)

dark, light = twotone(G_BLUE, 'medium')
fit_color = darken(dark, 0.25)

xs, ys = np.concatenate([x1, x2]), np.concatenate([y1, y2])
slope, intercept = np.polyfit(xs, ys, 1)
x_fit = np.linspace(xs.min(), xs.max(), 100)

fig, ax = plt.subplots(figsize=(6.4, 2.8), constrained_layout=True)

ax.scatter(x1, y1, color=dark, alpha=0.38, s=18, edgecolors='none', zorder=3)
ax.scatter(x2, y2, color=light, alpha=0.42, s=18, edgecolors='none', zorder=3)
ax.plot(x_fit, slope * x_fit + intercept, color=fit_color, lw=2.0, zorder=4)

ax.set_xlim(0, 215)
ax.set_ylim(0, 38)
ax.set_xlabel('Metric A')
ax.set_ylabel('Metric B (%)')
ax.set_title('Metric B vs. Metric A')

header_legend(ax, [('Setting A', dark), ('Setting B', light),
                   ('Pooled fit', fit_color, '-')])
finalize_headers(fig)
