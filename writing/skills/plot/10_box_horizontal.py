"""Template 10: horizontal boxplot with 4-step family gradient.

Use when: one categorical factor with ordered levels (e.g. progressively more
training compute), reading a metric distribution across runs/seeds.
"""
import numpy as np
import matplotlib.pyplot as plt
from style import apply_style, family_4, G_BLUE

apply_style()
rng = np.random.default_rng(0)

PALETTE = family_4(G_BLUE)  # 4 levels light → dark
LEVEL_LABELS = ['0× ❄', '0.5× ❄', '1× ❄', '1× ⚡']

# (median, std, n_outliers, outlier_offset) per level
SPECS = [
    (57, 6, 0, 0),
    (62, 1.0, 2, 8),
    (66, 1.2, 0, 0),
    (67, 1.0, 1, -3),
]


def gen_box(median, std, n_out, out_offset, n=12):
    s = rng.normal(median, std, n)
    s = s - np.median(s) + median
    if n_out:
        s = np.concatenate([s, np.full(n_out, median + out_offset)])
    return s


fig, ax = plt.subplots(figsize=(5.2, 2.6), constrained_layout=True)

data = [gen_box(*s) for s in SPECS]
positions = [4, 3, 2, 1]  # top → bottom: levels 0..3
bp = ax.boxplot(
    data, vert=False, positions=positions, widths=0.55, patch_artist=True,
    medianprops=dict(color='#222222', linewidth=1.2),
    whiskerprops=dict(color='#444444', linewidth=0.9),
    capprops=dict(color='#444444', linewidth=0.9),
    flierprops=dict(marker='o', markerfacecolor='none',
                    markeredgecolor='#444444', markersize=4, linewidth=0.6),
    boxprops=dict(linewidth=0.8, edgecolor='#333333'),
)
for patch, color in zip(bp['boxes'], PALETTE):
    patch.set_facecolor(color)

ax.set_yticks(positions)
ax.set_yticklabels(LEVEL_LABELS)
ax.set_xlabel('Metric value')
ax.set_ylim(0.4, 4.6)
ax.tick_params(axis='y', length=0)
ax.grid(axis='x', linestyle='--', alpha=0.4)
ax.grid(axis='y', visible=False)
ax.set_title('Method A — Task A')
