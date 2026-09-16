"""Concept diagram: a boundary between two parties, drawn by where arrows stop.

Two parties sit left and right; every exchange is one horizontal arrow with a
short label above it. An arrow that reaches the far side is allowed. An arrow
that ends in a red bar is stopped, and the bars line up to draw the boundary,
so no wall is drawn. A third box under the right party is reachable only
through that party, shown by the one vertical arrow.

Colour rule from concept.py: blue is the agent's side, red is withheld from the
agent, grey is neither. Labels stay on their own side of the boundary; the
check at the end raises if one straddles it.
"""
import concept as C
from concept import text, arrow, rule

TOP, BOT = 1.70, 0.10
fig, ax = C.canvas(5.5, C.height_for(TOP))
A, AW = 0.08, 1.22          # left column
D, DW = 4.20, 1.22          # right column
WALL = (A + AW + D) / 2     # the boundary, midway across the gap
L, R = A + AW + 0.03, D - 0.03

C.headline(ax, A, C.headline_y(C.height_for(TOP)),
           'What crosses the boundary and what stops at it')

# a: the agent and what it holds
C.node(ax, A, BOT, AW, TOP - BOT, 'a   Agent side', tint=C.BLUE_FILL)
text(ax, A + 0.08, 1.31, 'The repository', size=C.BODY)
text(ax, A + 0.08, 1.14, 'The allowed files', size=C.BODY)
text(ax, A + 0.08, 0.30, 'CPU only', size=C.META, color=C.GREY)

# b: the judge and what it keeps
JB = 0.70
C.node(ax, D, JB, DW, TOP - JB, 'b   Judge side', tint=C.RED_FILL)
text(ax, D + 0.08, 1.31, 'The evaluator', size=C.BODY)
text(ax, D + 0.08, 1.14, 'The hidden final suite', size=C.BODY)
text(ax, D + 0.08, 0.97, 'The reference', size=C.BODY)
text(ax, D + 0.08, 0.80, 'CPU only', size=C.META, color=C.GREY)

# c: a resource reached only through the judge
AH = 0.48
C.node(ax, D, BOT, DW, AH, 'c   Shared resource')
text(ax, D + 0.08, BOT + 0.115, 'Started by the judge', size=C.BODY)
arrow(ax, D + DW / 2, JB - 0.03, D + DW / 2, BOT + AH + 0.03)

LIFT = 0.075   # label sits this far above its arrow


def crosses(y, label, *, to_judge):
    if to_judge:
        arrow(ax, L, y, R, y)
        text(ax, L, y + LIFT, label, size=C.BODY)
    else:
        arrow(ax, R, y, L, y)
        text(ax, R, y + LIFT, label, size=C.BODY, ha='right')


def stops(y, label, *, from_agent):
    x0 = L if from_agent else R
    rule(ax, x0, y, WALL, y, color=C.GREY, lw=0.7)
    rule(ax, WALL, y - 0.055, WALL, y + 0.055, color=C.RED, lw=1.4)
    text(ax, x0, y + LIFT, label, size=C.BODY, ha='left' if from_agent else 'right')


# allowed, top group
crosses(1.36, 'Allowed exchange A', to_judge=True)
crosses(1.20, 'Allowed exchange B', to_judge=False)
crosses(1.04, 'Allowed exchange C', to_judge=False)
# stopped, bottom group
stops(0.84, 'Blocked request A', from_agent=True)
stops(0.68, 'Blocked request B', from_agent=True)
stops(0.52, 'Withheld item A', from_agent=False)
stops(0.36, 'Withheld item B', from_agent=False)
stops(0.20, 'Blocked request C', from_agent=True)

# every arrow label has to stay on its own side of the boundary
fig.canvas.draw()
rend = fig.canvas.get_renderer()
for t in ax.texts:
    b = t.get_window_extent(rend)
    x0, x1 = b.x0 / fig.dpi, b.x1 / fig.dpi
    if x0 < WALL < x1 and t.get_fontsize() == C.BODY and not (A <= x0 <= A + AW or D <= x0 <= D + DW):
        raise ValueError(f'label straddles the boundary: {t.get_text()!r} [{x0:.2f}, {x1:.2f}]')

C.check(fig)
# C.save(fig, 'out')   # writes out.pdf / out.svg / out.png in the working directory
