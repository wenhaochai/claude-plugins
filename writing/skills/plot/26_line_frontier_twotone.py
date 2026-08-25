"""Template 26: running-max frontier line — best-so-far metric over a run.

Use when: tracing the best result found so far across a session or run; the
frontier keeps only new highs, so the line is monotone non-decreasing.
Announcement-chart look: one deep hue via `twotone`, thick round-cap line +
solid round markers, no background scatter, y floor at the baseline (1).
Swap `G_BLUE` for any palette color.
"""
import matplotlib.pyplot as plt

from style import apply_style, header_legend, finalize_headers, G_BLUE, twotone

apply_style()

# Raw per-step measurements (step, value); the frontier keeps only new highs.
raw = [(1, 1.15), (3, 1.10), (5, 1.42), (8, 1.38), (12, 1.71),
       (17, 1.66), (23, 1.95), (30, 2.28), (38, 2.20), (47, 2.61)]

# running-max frontier: keep each point that beats the best value so far
frontier, best = [], -float('inf')
for step, val in sorted(raw):
    if val > best:
        best = val
        frontier.append((step, val))

dark, _ = twotone(G_BLUE, 'brand')

fig, ax = plt.subplots(figsize=(4.8, 3.5), constrained_layout=True)

fx, fy = zip(*frontier)
ax.plot(fx, fy, '-', color=dark, linewidth=2.6, alpha=0.98, zorder=3,
        marker='o', markersize=10, solid_capstyle='round',
        markeredgecolor='white', markeredgewidth=0.8)

ax.set_ylim(1.0, max(fy) + 0.4)      # y floor = baseline efficiency (1x)
ax.set_xlim(fx[0] - 2, fx[-1] * 1.12)
ax.set_xlabel('Session Step')
ax.set_ylabel('Compute Efficiency (CE)')

header_legend(ax, [('Frontier', dark)])
finalize_headers(fig)
