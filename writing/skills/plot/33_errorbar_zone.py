"""Template 33: binned mean +/- SEM errorbar line with a highlighted
sweet-spot zone, announcement-chart look. Use when: a metric peaks at an
intermediate value of a binned factor (Occam's-razor shape) — deep line +
round markers in one hue, a pale `axvspan` of the same hue marks the
optimal band, grey error whiskers.
"""
import numpy as np
import matplotlib.pyplot as plt

from style import (apply_style, header_legend, finalize_headers,
                   G_BLUE, lighten, twotone)

apply_style()

bin_labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9-11', '12+']
mean = [1.06, 1.18, 1.42, 1.51, 1.46, 1.33, 1.24, 1.17, 1.10, 1.02]
sem = [0.03, 0.04, 0.05, 0.06, 0.06, 0.05, 0.06, 0.07, 0.08, 0.09]
zone = (2.0, 4.5)   # x-span of the highlighted optimal band (bin indices)

dark, light = twotone(G_BLUE, 'medium')
zone_color = lighten(light, 0.55)

fig, ax = plt.subplots(figsize=(5.6, 3.2), constrained_layout=True)

x = np.arange(len(bin_labels))
ax.axvspan(*zone, color=zone_color, alpha=0.7, zorder=1)
ax.errorbar(x, mean, yerr=sem, fmt='-o', color=dark, ecolor='0.6',
            elinewidth=1.1, capsize=2.5, lw=1.7, markersize=4.5,
            markeredgecolor='white', markeredgewidth=0.7, zorder=3)

ax.set_xticks(x, bin_labels)
ax.set_xlabel('Factor A (binned)')
ax.set_ylabel('Mean Metric A')
ax.set_ylim(0.95, 1.65)
ax.set_title('Metric A Peaks at Intermediate Factor A')

header_legend(ax, [('Mean ± SEM', dark, 'o'),
                   ('Optimal zone', zone_color, 's')])
finalize_headers(fig)
