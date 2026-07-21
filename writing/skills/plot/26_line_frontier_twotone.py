"""Running-max frontier line — the best-so-far metric climbing over a run.

The frontier is the running maximum of a noisy series: at each step keep the
point only if it sets a new high, so the line is monotone non-decreasing and
traces the "best recipe found so far" over the run. Announcement-clean look
(OpenAI-release style, recolored to Google palette + Palatino): one deep hue
via `twotone`, thick round-cap line + solid round markers, NO background
scatter, NO grid, L-spine only, dot legend above the axes, y starts at the
baseline floor (1). Swap `G_BLUE` for any palette color.
"""

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from style import apply_style, G_BLUE, twotone

apply_style()

# --- data (illustrative — replace) ------------------------------------------
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
INK = '#1a1a1a'

fig, ax = plt.subplots(figsize=(4.8, 3.5), constrained_layout=True)
ax.grid(False)

# frontier spine: deep-blue round-cap line + solid round markers
fx, fy = zip(*frontier)
ax.plot(fx, fy, '-', color=dark, linewidth=2.6, alpha=0.98, zorder=3,
        marker='o', markersize=10, solid_capstyle='round',
        markeredgecolor='white', markeredgewidth=0.8)

ax.set_ylim(1.0, max(fy) + 0.4)      # y floor = baseline efficiency (1x)
ax.set_xlim(fx[0] - 2, fx[-1] * 1.12)
ax.set_xlabel('Session Step')
ax.set_ylabel('Compute Efficiency (CE)')

# announcement-clean axes: L-shaped spines, outward ticks, no grid
for side in ('top', 'right'):
    ax.spines[side].set_visible(False)
for side in ('left', 'bottom'):
    ax.spines[side].set_color(INK)
    ax.spines[side].set_linewidth(0.9)
ax.tick_params(direction='out', colors=INK)

# single-dot legend above the axes, flush left
handles = [Line2D([], [], marker='o', linestyle='', markersize=10,
                  color=dark, label='Frontier')]
ax.legend(handles=handles, loc='lower left', bbox_to_anchor=(0, 1.0),
          ncol=1, frameon=False, handletextpad=0.4, borderaxespad=0)
