"""Concept diagram: two jigsaw treemaps side by side, one shared key.

Each panel is a treemap with a piece per domain, sized by count, coloured by
the area the domain belongs to; pieces of one area sit together, and the
seams between the larger pieces carry jigsaw knobs. The two panels share the
scale, so a piece of the same size means the same count in either panel, and
the panel widths follow the totals. The legend above names the areas once;
counts stay on the pieces.

Vertical stack: headline, legend rows, panel headings, panels, with one gap
(C.TITLE_GAP) between every layer. Each layer's half-height comes from its type
size (C.half_for), so the stack stays even when a size changes.

Swap the two count dicts and the family map; keep everything else. A piece
too small for its label falls back to a wrapped, inline, or rotated label, and
then to the name alone with a printed warning, so read the console.
"""
import concept as C
from concept import arrow
import jigsaw as J
import style

# The shared key, in legend order. Six areas at most: one Google hue each.
J.HUE.clear()
J.HUE.update([('Area 1', style.G_BLUE), ('Area 2', style.G_GREEN),
              ('Area 3', style.G_PURPLE), ('Area 4', style.G_RED),
              ('Area 5', style.G_YELLOW), ('Area 6', style.G_GREY)])

# Panel a: domain -> count, and domain -> area.
c1 = {'Domain A': 19, 'Domain B': 8, 'Domain C': 7, 'Domain D': 6, 'Domain E': 5, 'Domain F': 4}
f1 = {'Domain A': 'Area 1', 'Domain B': 'Area 1', 'Domain C': 'Area 5',
      'Domain D': 'Area 2', 'Domain E': 'Area 3', 'Domain F': 'Area 4'}
# Panel b: the same key, more domains.
c2 = {'Domain A': 16, 'Domain G': 15, 'Domain E': 9, 'Domain C': 6, 'Domain H': 5,
      'Domain F': 5, 'Domain I': 4, 'Domain J': 4, 'Domain K': 4, 'Domain L': 3,
      'Domain M': 2, 'Domain N': 2}
f2 = {'Domain A': 'Area 1', 'Domain G': 'Area 2', 'Domain E': 'Area 3', 'Domain C': 'Area 5',
      'Domain H': 'Area 1', 'Domain F': 'Area 4', 'Domain I': 'Area 1', 'Domain J': 'Area 4',
      'Domain K': 'Area 2', 'Domain L': 'Area 1', 'Domain M': 'Area 6', 'Domain N': 'Area 2'}
n1, n2 = sum(c1.values()), sum(c2.values())
areas = set(f1.values()) | set(f2.values())

X0, X1, COL_GAP = 0.08, 5.42, 0.34
BOT, TOP = 0.10, 2.70                   # panel band

GAP = C.TITLE_GAP
LEG_HALF = max(J.DOT_R, C.half_for(C.BODY))
HEAD_HALF = C.half_for(C.H2)
LEG_ROWS = 1                            # rows the legend needs at this width; asserted below
LEG_PITCH = 2 * LEG_HALF + 0.04         # inside the legend block, not a stack gap

HEAD_Y = TOP + GAP + HEAD_HALF                        # panel heading centre
LEG_LAST = HEAD_Y + HEAD_HALF + GAP + LEG_HALF        # last legend row centre
LEG_Y = LEG_LAST + (LEG_ROWS - 1) * LEG_PITCH         # first legend row centre
H = C.height_for(LEG_Y + LEG_HALF)

fig, ax = C.canvas(5.5, H)
C.headline(ax, X0, C.headline_y(H), 'One benchmark grows into the next')
rows = J.legend(fig, ax, areas, X0, X1, LEG_Y, LEG_PITCH)
assert rows == LEG_ROWS, f'legend used {rows} rows, the stack is built for {LEG_ROWS}'

# widths follow totals, so one unit is the same area in both panels
usable = X1 - X0 - COL_GAP
w1 = usable * n1 / (n1 + n2)
L1, R1 = X0, X0 + w1
L2, R2 = R1 + COL_GAP, X1

C.heading(ax, L1, HEAD_Y, 'a', f'Benchmark 1, {n1} tasks')
J.treemap(fig, ax, c1, f1, L1, R1, BOT, TOP, seed=3)
C.heading(ax, L2, HEAD_Y, 'b', f'Benchmark 2, {n2} tasks')
J.treemap(fig, ax, c2, f2, L2, R2, BOT, TOP, seed=7)

# one grows into the next
arrow(ax, R1 + 0.06, (BOT + TOP) / 2, L2 - 0.06, (BOT + TOP) / 2)

C.check(fig)
# C.save(fig, 'out')   # writes out.pdf / out.svg / out.png in the working directory
