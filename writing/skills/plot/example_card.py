"""Contains no measured results: the values are read off Epoch AI's card "Lower serving costs allow the
same hardware to support more agents" (CC-BY), redrawn here as the card form's worked example.

A 4:5 card: one log-log panel, a grey band of scenarios around a central line, open models as points,
closed models as ranges (a thick bar under the line between two points), each named by a label with a
bare leader. Concurrent agents = K / cost per agent-hour, K = 3.1e8 read off the central line; the band
is that line x/÷ 1.6. Epoch's footnote, sources and footer are left out; they belong in the post.
Output: example_card.pdf and example_card.png (1600 x 2000).
"""
from pathlib import Path

import numpy as np

from style import *

HERE = Path(__file__).resolve().parent
apply_style()

K, SPREAD = 3.1e8, 1.6
OPEN, CLOSED = tone('cyan', 700), tone('pink', 600)
# name, agents (one value, or the low and high ends of a range), the label's offset from the point in
# points, clear of the band, where the leader leaves the label's box, the leader's bend
MODELS = [('DeepSeek V4 Pro', (1.9e9,), (12, 17), (0, 0.5), 0.3),
          ('GLM-5.2', (5.71e8,), (-34, -32), (0.44, 1), 0.3),
          ('Kimi K3', (2.4e8,), (-12, 24), (0.48, 0), 0.3),
          ('GPT-5.6 Sol', (9.7e7, 1.95e8), (-40, -34), (0.46, 1), 0.3),
          ('Claude Fable 5', (3.0e7, 6.0e7), (-22, 27), (0.53, 0), 0.3)]


def si(v):
    """10M, 300M, 1.9B: agents at two significant figures at most."""
    for unit, scale in (('B', 1e9), ('M', 1e6)):
        if v >= scale:
            return f'{v / scale:.3g}{unit}'
    return f'{v:.0f}'


def amount(agents):
    """1.9B agents, or a range as 97–195M agents with the shared unit written once."""
    if len(agents) == 1:
        return f'{si(agents[0])} agents'
    lo, hi = map(si, agents)
    return f'{lo[:-1] if lo[-1] == hi[-1] else lo}–{hi} agents'


def dollars(v):
    return f'${v:.2f}' if v < 1 else f'${v:.0f}'


fig, axes = canvas(card=True,
                   title='Potential concurrent agents against reference serving cost',
                   subtitle='Potential capacity from memory shipped during 2025–27, assuming full deployment '
                            'for the selected workload',
                   legend=[('Open models (benchmarked)', OPEN, 'box'), ('Closed models (inferred)', CLOSED, 'box'),
                           ('Hardware scenarios', GREY_400, 'box'), ('Central estimate', INK, 'line')],
                   quantity='Potential concurrent agents', xlabel='Reference serving cost per agent-hour (US$)')
ax = axes[0, 0]
ax.set_xscale('log')
ax.set_yscale('log')
ax.minorticks_off()

cost = np.geomspace(0.1, 20, 50)
ax.fill_between(cost, K / cost / SPREAD, K / cost * SPREAD, color=GREY_400, linewidth=0, zorder=1)
ax.plot(cost, K / cost, color=INK, linewidth=1.1, zorder=3)
for name, agents, at, leave, rad in MODELS:
    x = [K / a for a in agents]
    color = OPEN if len(agents) == 1 else CLOSED
    if len(agents) == 2:
        ax.plot(x, agents, color=CLOSED, linewidth=3.4, solid_capstyle='butt', zorder=2)
    ax.scatter(x, agents, s=22, color=color, edgecolor=INK, linewidth=0.6, zorder=4)
    mid = 10 ** np.mean(np.log10(agents))
    callout(ax, at, (K / mid, mid), [name, amount(agents)], arrow=False, rad=rad,
            relpos=leave, points=True)

ax.set_ylim(7e6, 1e10)
y_values(ax, [1e7, 3e7, 1e8, 3e8, 1e9, 3e9, 1e10], si)
ax.set_xticks([0.1, 0.3, 1, 3, 10, 20], [dollars(v) for v in (0.1, 0.3, 1, 3, 10, 20)])
ax.tick_params(axis='x', length=2.5, width=0.6, color=AXIS)
ax.set_xlim(0.1, 20)
room(ax, right_in=0.0)
save(fig, HERE / 'example_card')
