"""The same categorical mix over two runs, side by side, labelled inside the bands.

Two 100% stacked areas sharing one band vocabulary and one y-axis, so the shapes
are directly comparable. Each band carries its own name where it is thick enough
to hold it, which is what removes the legend: a legend for a stack forces the
reader to match four greys top to bottom while counting.

Contains no measured results; the mixes below come from a fixed seed.
Output: 5.5 in wide, placed at 1:1.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from style import (apply_style, header, finalize_headers,
                   G_BLUE, INK, PANEL_PT, WIDTH_1COL, family_4)

apply_style()
CATEGORIES = ['Category A', 'Category B', 'Category C', 'Category D']
COLORS = family_4(G_BLUE)[::-1]          # darkest at the bottom of the stack
PANELS = [('Run A', 52), ('Run B', 36)]
MIN_BAND_TO_LABEL = 9.0                  # percentage points

rng = np.random.default_rng(8)
fig, axes = plt.subplots(1, 2, figsize=(WIDTH_1COL, 2.4), sharey=True)

for ax, (panel, days) in zip(axes, PANELS):
    x = np.arange(days)
    raw = np.abs(rng.normal([34, 30, 14, 12], 4, size=(days, 4)))
    for j in range(4):                    # a slow drift, so the mix has a story
        raw[:, j] *= np.linspace(1.0, 0.7 + 0.25 * j, days)
    # A share plot reads the SHAPE of each band, so per-step noise has to go:
    # smooth the composition before normalising, never the normalised shares.
    k = np.ones(7) / 7
    raw = np.stack([np.convolve(np.pad(raw[:, j], 3, mode='edge'), k, 'valid')
                    for j in range(4)], axis=1)
    share = 100 * raw / raw.sum(axis=1, keepdims=True)
    stack = np.cumsum(share, axis=1)

    lower = np.zeros(days)
    for j, (name, color) in enumerate(zip(CATEGORIES, COLORS)):
        ax.fill_between(x, lower, stack[:, j], color=color, linewidth=0.5,
                        edgecolor='white')
        mid = days // 2
        thickness = stack[mid, j] - lower[mid]
        if thickness >= MIN_BAND_TO_LABEL:
            ax.text(x[mid], (stack[mid, j] + lower[mid]) / 2, name,
                    ha='center', va='center', fontsize=6.6,
                    color='white' if j == 0 else INK)
        lower = stack[:, j]

    ax.set_xlim(0, days - 1)
    ax.set_ylim(0, 100)
    ax.set_xlabel('Run day')
    header(ax, panel, size=PANEL_PT)

axes[0].set_ylabel('Share (%)')
finalize_headers(fig)
