"""Template 27: smoothed mean line + dispersion band + raw event cloud,
announcement-chart look. Use when: a per-event score evolves over a long
run and both the trend and its spread matter — pale scatter = raw events,
band = +/-1 sigma of a Gaussian-kernel local mean, deep line = the mean;
one hue via `twotone` (Principle 8 band alpha).
"""
import numpy as np
import matplotlib.pyplot as plt

from style import apply_style, header_legend, finalize_headers, G_BLUE, twotone

apply_style()

rng = np.random.default_rng(7)
n_events = 420
days = np.sort(rng.uniform(0, 50, n_events))            # event timestamps
scores = (38 - 0.35 * days + 8 * np.exp(-((days - 9) / 5) ** 2)
          + rng.normal(0, 7.5, n_events)).clip(0, 100)  # per-event score

# Gaussian-kernel local mean and sigma on a uniform grid
grid = np.linspace(0, 50, 150)
bandwidth = 3.5
mu, sd = np.zeros_like(grid), np.zeros_like(grid)
for i, t in enumerate(grid):
    w = np.exp(-0.5 * ((days - t) / bandwidth) ** 2)
    mu[i] = np.sum(w * scores) / np.sum(w)
    sd[i] = np.sqrt(np.sum(w * (scores - mu[i]) ** 2) / np.sum(w))

dark, light = twotone(G_BLUE, 'medium')

fig, ax = plt.subplots(figsize=(5.4, 3.3), constrained_layout=True)

ax.scatter(days, scores, s=7, color=light, alpha=0.30,
           edgecolors='none', zorder=2)
ax.fill_between(grid, mu - sd, mu + sd, color=dark, alpha=0.15,
                linewidth=0, zorder=2)
ax.plot(grid, mu, color=dark, linewidth=1.9, zorder=4)

ax.set_xlim(0, 50)
ax.set_ylim(0, 75)
ax.set_xlabel('Run Days')
ax.set_ylabel('Metric A')
ax.set_title('Metric A over the Run')

header_legend(ax, [('Mean', dark, '-'), ('Events', light),
                   (r'$\pm 1\sigma$', dark, 's')])
finalize_headers(fig)
