"""Template 41: alluvial / Sankey flow across ordered stages,
announcement-chart look. Use when: a population re-partitions across 3-4
ordered stages (depth, phase, round) and the flows between adjacent
stages matter — rounded stage bars, cubic-Bezier ribbons colored by
source category, % labels inside bars that are tall enough. 4 categories
use one hue's `family_4`; flows are (src, tgt, weight) triples per
stage pair.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

from style import (apply_style, header_legend, finalize_headers,
                   G_BLUE, INK, darken, family_4)

apply_style()

CATS = ['Category A', 'Category B', 'Category C', 'Category D']
colors = dict(zip(CATS, family_4(G_BLUE)[::-1]))  # A darkest

stages = ['Stage 0', 'Stage 1', 'Stage 2', 'Stage 3']
# category -> count at each stage (0 = absent)
counts = {
    'Stage 0': {'Category A': 100},
    'Stage 1': {'Category A': 34, 'Category B': 28, 'Category C': 22,
                'Category D': 16},
    'Stage 2': {'Category A': 26, 'Category B': 34, 'Category C': 25,
                'Category D': 15},
    'Stage 3': {'Category A': 18, 'Category B': 40, 'Category C': 28,
                'Category D': 14},
}
# (source_cat, target_cat, weight) per adjacent stage pair
flows = [
    [('Category A', 'Category A', 34), ('Category A', 'Category B', 28),
     ('Category A', 'Category C', 22), ('Category A', 'Category D', 16)],
    [('Category A', 'Category A', 20), ('Category A', 'Category B', 10),
     ('Category B', 'Category B', 20), ('Category B', 'Category C', 8),
     ('Category C', 'Category C', 14), ('Category C', 'Category A', 6),
     ('Category C', 'Category B', 2), ('Category D', 'Category D', 13),
     ('Category D', 'Category B', 2), ('Category D', 'Category C', 3)],
    [('Category A', 'Category A', 15), ('Category A', 'Category B', 8),
     ('Category B', 'Category B', 26), ('Category B', 'Category C', 8),
     ('Category C', 'Category C', 18), ('Category C', 'Category B', 5),
     ('Category C', 'Category A', 2), ('Category D', 'Category D', 12),
     ('Category D', 'Category B', 1), ('Category D', 'Category C', 2)],
]

BAR_W, GAP = 0.22, 1.5   # stage-bar width, gap between stacked segments (%)
stage_x = list(range(len(stages)))

fig, ax = plt.subplots(figsize=(6.8, 2.9), constrained_layout=True)

# stack each stage's categories into (ymin, ymax) boxes normalized to 100
boxes = {}   # (stage_idx, cat) -> (ymin, ymax, pct)
for s, st in enumerate(stages):
    present = [(c, counts[st][c]) for c in CATS if counts[st].get(c)]
    total = sum(v for _, v in present)
    avail = 100 - (len(present) - 1) * GAP
    y = 0.0
    for c, v in present:
        h = v / total * avail
        boxes[(s, c)] = (y, y + h, v / total * 100)
        y += h + GAP

def ribbon(x0, y0b, y0t, x1, y1b, y1t, color):
    dx = (x1 - x0) * 0.46
    verts = [(x0, y0b), (x0 + dx, y0b), (x1 - dx, y1b), (x1, y1b),
             (x1, y1t), (x1 - dx, y1t), (x0 + dx, y0t), (x0, y0t), (x0, y0b)]
    codes = [Path.MOVETO] + [Path.CURVE4] * 3 + [Path.LINETO] + \
            [Path.CURVE4] * 3 + [Path.CLOSEPOLY]
    ax.add_patch(patches.PathPatch(Path(verts, codes), facecolor=color,
                                   edgecolor='none', alpha=0.28, zorder=2))

# ribbons: each side's sub-slots are allocated proportionally to the flows
for s, stage_flows in enumerate(flows):
    src_tot, tgt_tot = {}, {}
    for a, b, w in stage_flows:
        src_tot[a] = src_tot.get(a, 0) + w
        tgt_tot[b] = tgt_tot.get(b, 0) + w
    src_off = {k: 0.0 for k in src_tot}
    tgt_off = {k: 0.0 for k in tgt_tot}
    for a, b, w in sorted(stage_flows,
                          key=lambda f: (boxes[(s, f[0])][0],
                                         boxes[(s + 1, f[1])][0])):
        y0m, y0M, _ = boxes[(s, a)]
        y1m, y1M, _ = boxes[(s + 1, b)]
        h0 = w / src_tot[a] * (y0M - y0m)
        h1 = w / tgt_tot[b] * (y1M - y1m)
        ribbon(stage_x[s] + BAR_W / 2, y0m + src_off[a],
               y0m + src_off[a] + h0, stage_x[s + 1] - BAR_W / 2,
               y1m + tgt_off[b], y1m + tgt_off[b] + h1, colors[a])
        src_off[a] += h0
        tgt_off[b] += h1

# stage bars + % labels
for (s, c), (ymin, ymax, pct) in boxes.items():
    col = colors[c]
    ax.add_patch(patches.FancyBboxPatch(
        (stage_x[s] - BAR_W / 2, ymin), BAR_W, ymax - ymin,
        boxstyle='round,pad=0,rounding_size=0.012', facecolor=col,
        edgecolor=darken(col, 0.2), linewidth=0.85, zorder=4))
    if ymax - ymin >= 6.0:
        light_band = col == colors['Category D']
        ax.text(stage_x[s], (ymin + ymax) / 2,
                '100%' if s == 0 else f'{pct:.0f}%', ha='center',
                va='center', fontsize=8, fontweight='bold',
                color=INK if light_band else 'white', zorder=5)

ax.set_xlim(-0.28, len(stages) - 1 + 0.28)
ax.set_ylim(-4, 104)
ax.set_xticks(stage_x, stages)
ax.set_yticks([])
ax.spines['left'].set_visible(False)
ax.set_title('Composition Cascades Across Stages')

header_legend(ax, [(c, colors[c], 's') for c in CATS])
finalize_headers(fig)
