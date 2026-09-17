"""A large exploration DAG with a handful of groups picked out of it.

The whole graph is drawn once in grey at hairline weight so its shape and scale
are visible, and only the groups the argument is about carry colour, marker and
arrowheads. Drawing every edge in colour turns a graph this size into texture;
drawing only the highlighted part hides the haystack the needle was found in.

Contains no measured results; the graph below is generated from a fixed seed.
Output: 5.5 in wide, placed at 1:1.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from style import (apply_style, header, finalize_headers,
                   G_YELLOW, REF_GREY, WIDTH_1COL, apply_tier, lighten)

apply_style()
HIGHLIGHT = apply_tier(G_YELLOW, 'brand')
BACKDROP = lighten(REF_GREY, 0.72)

rng = np.random.default_rng(17)
LAYERS, PER_LAYER = 14, 34
N_GROUPS = 9

# Backdrop: nodes on a jittered grid, each joined to a few in the next layer.
pos, layer_of = [], []
for layer in range(LAYERS):
    k = PER_LAYER - abs(layer - LAYERS // 2) * 2
    ys = np.linspace(0.04, 0.96, k) + rng.normal(0, 0.006, k)
    for y in ys:
        pos.append((layer + rng.normal(0, 0.10), y))
        layer_of.append(layer)
pos = np.array(pos)
layer_of = np.array(layer_of)

edges = []
for layer in range(LAYERS - 1):
    src = np.flatnonzero(layer_of == layer)
    dst = np.flatnonzero(layer_of == layer + 1)
    for s in src:
        for d in rng.choice(dst, size=min(2, dst.size), replace=False):
            edges.append((s, d))

fig, ax = plt.subplots(figsize=(WIDTH_1COL, 2.4))

for s, d in edges:
    ax.plot([pos[s, 0], pos[d, 0]], [pos[s, 1], pos[d, 1]],
            color=BACKDROP, linewidth=0.28, alpha=0.5, zorder=1)
ax.scatter(pos[:, 0], pos[:, 1], s=3.4, marker='s', color=BACKDROP, zorder=2)

# The groups: a parent, one or two diff edges, a child whose outcome is withheld.
chosen = rng.choice(np.flatnonzero(layer_of < LAYERS - 2), N_GROUPS, replace=False)
for parent in chosen:
    hops = rng.integers(1, 3)
    chain = [parent]
    for _ in range(hops):
        nxt = np.flatnonzero(layer_of == layer_of[chain[-1]] + 1)
        chain.append(int(rng.choice(nxt)))
    for a, b in zip(chain, chain[1:]):
        ax.annotate('', xy=pos[b], xytext=pos[a], zorder=4,
                    arrowprops=dict(arrowstyle='-|>', color=HIGHLIGHT,
                                    linewidth=1.15, shrinkA=3.4, shrinkB=3.8))
    ax.scatter(*pos[chain[0]], s=26, color=HIGHLIGHT, edgecolors='white',
               linewidths=0.7, zorder=5)
    ax.scatter(*pos[chain[-1]], s=30, facecolors='white', edgecolors=HIGHLIGHT,
               linewidths=1.5, zorder=5)
    ax.scatter(*pos[chain[-1]], s=6, color=HIGHLIGHT, zorder=6)

ax.set_xlim(-0.8, LAYERS - 0.2)
ax.set_ylim(-0.02, 1.02)
ax.axis('off')

header(ax, 'Every highlighted group is one question',
       [('Parent, given', HIGHLIGHT), ('Step taken', HIGHLIGHT, '-'),
        ('Child, outcome withheld', HIGHLIGHT, 'o')])
finalize_headers(fig)
