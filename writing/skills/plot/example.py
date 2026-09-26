"""Contains no measured results: the rounds below come from a fixed seed.

Best-so-far steps, one panel per setting: three runs improve something over their own rounds, and
each line holds the best version kept so far, so it never goes down. A step changes at the round's
integer tick, and every round up to the last has a tick and a grid line. The x values are the runs'
own round numbers; a round a run rejected keeps the level. Method details (how each point was
measured, what "best" is taken over) go in the caption, not on the chart.
Output: example.pdf and example.png, WIDTH_POST wide (the PNG 1600 px, for a post).
"""
from pathlib import Path

import numpy as np

from style import *

HERE = Path(__file__).resolve().parent
apply_style()

rng = np.random.default_rng(7)
SETTINGS = ['Setting A', 'Setting B', 'Setting C', 'Setting D']
RUNS = [('Model A', BLUE, 9), ('Model B', LIGHT, 10), ('Model C', GREY, 10)]   # name, colour, last round


def best_so_far(start, gains):
    """Round 0 is the starting point; each later round keeps the better of the new version and the
    best so far."""
    levels = [start]
    for g in gains:
        levels.append(max(levels[-1], levels[-1] * (1 + g)))
    return levels


fig, axes = canvas(rows=2, cols=2, width=WIDTH_POST, panel_height=1.3,
                   title='Title in the owner\'s words, full width, one size',
                   legend=[(name, color) for name, color, _ in RUNS],
                   quantity='Throughput (MB/s)')
for k, (ax, setting) in enumerate(zip(axes.flat, SETTINGS)):
    start = 1000 * (1 + k)
    top = start
    for name, color, last in RUNS[::-1]:
        gains = rng.normal(0.08 if color == BLUE else 0.04, 0.1, last)
        levels = best_so_far(start, gains)
        # every corner on an integer tick; the last level runs half a round so it shows
        ax.step([*range(last + 1), last + 0.5], [*levels, levels[-1]], where='post', color=color, zorder=3)
        top = max(top, max(levels))
    ax.set_xticks(range(0, 11), [str(t) for t in range(0, 11)])
    ax.set_xlim(0, 10.5)
    nice_y(ax, start, top)          # the values first: room() measures them
    room(ax)
    panel_label(ax, setting)
save(fig, HERE / 'example')
