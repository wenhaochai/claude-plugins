"""Concept diagram: how one thing is taken apart into the pieces a task needs.

Four nodes in a row, each a white box with a tinted title band that carries
the panel letter and the panel name, so nothing floats above the blocks. The
band colour follows concept.py's rule: blue is the agent's side, red is what
is withheld from the agent, grey is neither. Connectors are grey open-V arrows.

Copy, swap the labels, keep the geometry. Text that would run past its panel
raises in C.check(), so widen a node or shorten a label rather than eyeball it.
"""
import concept as C
from concept import text, arrow, rule

TOP, BOT = 1.50, 0.10
fig, ax = C.canvas(5.5, C.height_for(TOP))
A, B, D = 0.08, 2.03, 3.86            # column lefts
AW, BW, DW = 1.66, 1.58, 1.56         # column widths

C.headline(ax, A, C.headline_y(C.height_for(TOP)), 'A task is built from one source artifact')

# a: the artifact, and the parts taken out of it
C.node(ax, A, BOT, AW, TOP - BOT, 'a   Removed component', tint=C.RED_FILL)
text(ax, A + 0.08, 1.15, 'Artifact A, Model A', size=C.BODY)
for y, label, detail in [(0.92, 'path/to/module_a.py', 'one class'),
                         (0.73, 'utils_b.py', 'three functions'),
                         (0.54, 'path/to/module_c.py', 'duplicate')]:
    text(ax, A + 0.08, y, label, size=C.BODY)
    text(ax, A + AW - 0.08, y, detail, size=C.META, ha='right', color=C.GREY)
text(ax, A + 0.08, 0.30, 'Keep the rest of the pipeline', size=C.META, color=C.GREY)

# one removal, two recipients
rule(ax, A + AW + 0.03, 0.80, A + AW + 0.13, 0.80, lw=0.7)
rule(ax, A + AW + 0.13, 0.48, A + AW + 0.13, 1.16, lw=0.7)
arrow(ax, A + AW + 0.13, 1.16, B - 0.03, 1.16)
arrow(ax, A + AW + 0.13, 0.48, B - 0.03, 0.48)

C.node(ax, B, 0.88, BW, 0.62, 'b   Agent workspace', tint=C.BLUE_FILL)
text(ax, B + 0.08, 1.15, 'The interfaces are still there', size=C.BODY)
text(ax, B + 0.08, 0.96, 'and the agent has to fill them', size=C.BODY)

C.node(ax, B, BOT, BW, 0.62, 'c   Private reference', tint=C.RED_FILL)
text(ax, B + 0.08, 0.37, 'reference.patch', size=C.BODY)
text(ax, B + 0.08, 0.18, 'Restores the removed code', size=C.BODY)

rule(ax, B + BW + 0.03, 1.16, B + BW + 0.13, 1.16, lw=0.7)
rule(ax, B + BW + 0.03, 0.48, B + BW + 0.13, 0.48, lw=0.7)
rule(ax, B + BW + 0.13, 0.48, B + BW + 0.13, 1.16, lw=0.7)
arrow(ax, B + BW + 0.13, 0.80, D - 0.03, 0.80)

# d: the criteria, a small ruled table; the leading row is the one that matters
C.node(ax, D, BOT, DW, TOP - BOT, 'd   Acceptance criteria')
for y, metric, threshold in [(1.15, 'Metric A', 'at most 0.96 of theirs'),
                             (0.92, 'Metric B', 'under 0.25'),
                             (0.73, 'Metric C', 'under 0.01'),
                             (0.54, 'Metric D', 'under 0.005')]:
    weight = 'bold' if metric == 'Metric A' else 'normal'
    text(ax, D + 0.08, y, metric, size=C.BODY, weight=weight)
    text(ax, D + DW - 0.08, y, threshold, size=C.BODY, ha='right', weight=weight)
    rule(ax, D + 0.08, y - 0.095, D + DW - 0.08, y - 0.095)
text(ax, D + 0.08, 0.30, 'Reference scores 25.8 of 100', size=C.META, color=C.GREY)

C.check(fig)
# C.save(fig, 'out')   # writes out.pdf / out.svg / out.png in the working directory
