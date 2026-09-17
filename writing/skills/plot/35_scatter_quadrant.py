"""Two properties on one plane, split at the medians, with the target quadrant shaded.

Every object is placed by two measured properties; the median of each splits the
plane into four quadrants, and the one the argument is about is shaded. Bubble
area carries a third quantity. Only the objects that make the point are named,
because a scatter with every point labelled is a table.

Contains no measured results; the cloud below is drawn from a fixed seed.
Output: 5.5 in wide, placed at 1:1.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from style import (apply_style, header, finalize_headers, note,
                   G_BLUE, G_RED, REF_GREY, REF_DASH, WIDTH_1COL, paper, lighten)

apply_style()
COHORT_A, COHORT_B = paper(G_BLUE), paper(G_RED)

rng = np.random.default_rng(11)
n_a, n_b = 58, 35
x = np.concatenate([rng.beta(2.6, 8.0, n_a) * 0.9, rng.beta(1.7, 9.0, n_b) * 0.9])
y = np.concatenate([rng.normal(14, 10, n_a), rng.normal(-4, 9, n_b)])
size = np.concatenate([rng.gamma(2.0, 9, n_a), rng.gamma(2.6, 13, n_b)])
cohort = np.array(['A'] * n_a + ['B'] * n_b)

# the handful worth naming: the extremes on each axis, plus the target corner
CALLOUTS = [(0.043, 61.0, 'Object A'), (0.060, 45.0, 'Object B'),
            (0.079, 38.5, 'Object C'), (0.118, 38.0, 'Object D'),
            (0.305, 31.0, 'Object E'), (0.315, 9.0, 'Object F')]

fig, ax = plt.subplots(figsize=(WIDTH_1COL, 3.1))

mx, my = 0.152, 9.5           # the two medians, computed upstream in real use
ax.axvspan(mx, 0.35, ymin=0, ymax=1, color=lighten(G_BLUE, 0.93), zorder=0)
ax.axhspan(-24, my, xmin=0, xmax=1, color='white', zorder=1)
ax.axvline(mx, color=REF_GREY, linestyle=REF_DASH, linewidth=0.9, zorder=2)
ax.axhline(my, color=REF_GREY, linestyle=REF_DASH, linewidth=0.9, zorder=2)

for c, col in (('A', COHORT_A), ('B', COHORT_B)):
    m = cohort == c
    ax.scatter(x[m], y[m], s=size[m], color=col, alpha=0.72,
               edgecolors='white', linewidths=0.5, zorder=3)

for cx, cy, label in CALLOUTS:
    note(ax, cx + 0.006, cy, label, ha='left', va='center')

ax.set_xlim(0, 0.35)
ax.set_ylim(-24, 68)
ax.set_xlabel('Property A (share)')
ax.set_ylabel('Property B (percentage points)')
note(ax, 0.345, 64, 'Both above median', ha='right', va='top', color=COHORT_A)

header(ax, 'Property B against Property A, split at the medians',
       [('Cohort A', COHORT_A), ('Cohort B', COHORT_B),
        ('Median', REF_GREY, '--')])
finalize_headers(fig)
