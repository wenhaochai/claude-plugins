"""Template 42: exploration DAG with a highlighted winner lineage,
announcement-chart look. Use when: a search/evolution process explored
many branches and one lineage won — grey cloud = all explorations, deep
line + nodes = the winner's ancestor path, biggest dot = the winner;
axes off, layered left-to-right. One hue via `twotone` plus neutral grey.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from style import (apply_style, header_legend, finalize_headers,
                   G_BLUE, darken, twotone)

apply_style()

rng = np.random.default_rng(2)
dark, _ = twotone(G_BLUE, 'brand')
path_color = darken(dark, 0.15)
node_grey, edge_grey = '0.65', '0.88'

# Placeholder DAG: layered nodes, each with 1-2 parents one layer back.
layers = [1, 5, 8, 9, 8, 6]
nodes, edges = [], []          # nodes: (id, layer, y); edges: (src, tgt)
nid = 0
for li, n in enumerate(layers):
    ys = np.linspace(-(n - 1) / 2, (n - 1) / 2, n) + \
        (rng.uniform(-0.15, 0.15, n) if n > 1 else 0)
    for y in np.atleast_1d(ys):
        nodes.append((nid, li, float(y)))
        if li > 0:
            prev = [m for m in nodes if m[1] == li - 1]
            k = min(len(prev), 1 + int(rng.random() < 0.15))
            for p in rng.choice(len(prev), k, replace=False):
                edges.append((prev[p][0], nid))
        nid += 1

# winner = a last-layer node; lineage = all its ancestors
winner = [n for n in nodes if n[1] == len(layers) - 1][3][0]
parents = {}
for s, t in edges:
    parents.setdefault(t, set()).add(s)
path_nodes, queue = {winner}, [winner]
path_edges = set()
while queue:
    cur = queue.pop()
    for p in parents.get(cur, []):
        path_edges.add((p, cur))
        if p not in path_nodes:
            path_nodes.add(p)
            queue.append(p)

pos = {n[0]: (n[1], n[2]) for n in nodes}

fig, ax = plt.subplots(figsize=(6.8, 2.9), constrained_layout=True)

for s, t in edges:      # background edges first, lineage on top
    on_path = (s, t) in path_edges
    ax.annotate('', xy=pos[t], xytext=pos[s],
                arrowprops=dict(arrowstyle='->',
                                color=path_color if on_path else edge_grey,
                                lw=1.2 if on_path else 0.45,
                                mutation_scale=5.5 if on_path else 4.0,
                                shrinkA=3, shrinkB=3),
                zorder=5 if on_path else 1)
for n, li, y in nodes:
    if n == winner:
        col, size, z = darken(path_color, 0.2), 55, 10
    elif n in path_nodes:
        col, size, z = path_color, 32, 8
    else:
        col, size, z = node_grey, 18, 2
    ax.scatter([li], [y], s=size, color=col, edgecolors='white',
               linewidths=0.6, zorder=z)

ax.set_xlim(-0.4, len(layers) - 0.6)
ax.margins(y=0.12)
ax.set_axis_off()

# axes are off, so place the title/legend on a shadow axes frame
ax.set_axis_on()
for side in ax.spines.values():
    side.set_visible(False)
ax.set_xticks([])
ax.set_yticks([])
ax.set_title('Exploration Lineage')
header_legend(ax, [('Winner lineage', path_color, 'o'),
                   ('Winner', darken(path_color, 0.2), 'o'),
                   ('Explorations', node_grey, 'o')])
finalize_headers(fig)
