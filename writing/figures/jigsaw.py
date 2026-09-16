"""Jigsaw treemap shared by every task-distribution panel in the paper.

One piece per domain, sized by task count, coloured by the area the domain
belongs to; pieces of one area sit together. The areas and their hues live in
HUE, one place, so every panel that imports this module shares names and
colours by construction. A template overrides HUE before drawing:

    J.HUE.clear(); J.HUE.update([('Area 1', style.G_BLUE), ...])
"""
import collections
import math
import random

import numpy as np
from matplotlib.patches import Circle, Polygon

import concept as C
from concept import text
import style

# The shared key: area name -> Google hue. Order is the legend order.
HUE = collections.OrderedDict([
    ('Area 1', style.G_BLUE),
    ('Area 2', style.G_GREEN),
    ('Area 3', style.G_PURPLE),
    ('Area 4', style.G_RED),
    ('Area 5', style.G_YELLOW),
    ('Area 6', style.G_GREY),
])


def fill(area):
    """Piece tint for an area: its hue, lightened so the edge and label read."""
    return style.lighten(HUE[area], 0.80)

DOT_R = 0.045                           # legend dot radius
R = 0.055                               # knob radius on a long shared edge
R_MIN = 0.040                            # below this a knob reads as a wobble
DIV = 10                                 # a piece of side d caps its knob at d/DIV
MIN_SEAM = 0.75                          # shorter seams stay plain, so the
                                         # knobs read as a few deliberate marks
DEPTH_K = math.sqrt(3) / 2               # a knob of radius r pokes out r * DEPTH_K
EPS = 1e-6


def squarify(vals, x, y, w, h):
    """Bruls et al. squarified treemap; `y` grows downward, caller flips."""
    areas = [v * w * h / sum(vals) for v in vals]
    out, i = [], 0

    def worst(row, side):
        s = sum(row)
        return max(max(side * side * r / (s * s), s * s / (side * side * r)) for r in row)

    while i < len(areas):
        side = min(w, h)
        row, j = [areas[i]], i + 1
        while j < len(areas) and worst(row + [areas[j]], side) <= worst(row, side):
            row.append(areas[j])
            j += 1
        s = sum(row)
        if w >= h:
            rw, yy = s / h, y
            for r in row:
                rh = r / rw
                out.append((x, yy, rw, rh))
                yy += rh
            x, w = x + rw, w - rw
        else:
            rh, xx = s / w, x
            for r in row:
                rw = r / rh
                out.append((xx, y, rw, rh))
                xx += rw
            y, h = y + rh, h - rh
        i = j
    return out


def layout(counts, family_of, x0, x1, bot, top):
    """Two-level layout: areas by squarify, domains by squarify inside each.
    Returns [(domain, family, (x, y, w, h))] in drawing order."""
    by_family = collections.Counter()
    for d, n in counts.items():
        by_family[family_of[d]] += n
    families = [f for f in HUE if f in by_family]
    families.sort(key=lambda f: -by_family[f])
    fam_rects = squarify([by_family[f] for f in families], x0, 0, x1 - x0, top - bot)
    pieces = []
    for f, fr in zip(families, fam_rects):
        doms = sorted((d for d in counts if family_of[d] == f), key=lambda d: -counts[d])
        for d, (x, yd, w, h) in zip(doms, squarify([counts[d] for d in doms], *fr)):
            pieces.append((d, f, (x, top - yd - h, w, h)))
    return pieces


def knobs_for(pieces, seed):
    """Every shared edge gets a knob. knobs[i][edge] = [(s, sign, r)], with s
    measured along the edge in counter-clockwise order and +1 poking outward.
    The radius follows the shared edge and the two pieces, so a short edge or a
    shallow piece gets a small knob instead of none."""
    rng = random.Random(seed)
    knobs = [collections.defaultdict(list) for _ in pieces]
    for i, (_, _, a) in enumerate(pieces):
        for j, (_, _, b) in enumerate(pieces):
            if j <= i:
                continue
            for (p, q, pi, qi) in [(a, b, i, j), (b, a, j, i)]:
                px, py, pw, ph = p
                qx, qy, qw, qh = q
                vertical = abs(px + pw - qx) < EPS   # p's right meets q's left
                horizontal = abs(py + ph - qy) < EPS  # p's top meets q's bottom
                if not (vertical or horizontal):
                    continue
                if vertical:
                    lo, hi = max(py, qy), min(py + ph, qy + qh)
                    across = min(pw, qw)             # room the knob pokes into
                else:
                    lo, hi = max(px, qx), min(px + pw, qx + qw)
                    across = min(ph, qh)
                overlap = hi - lo
                if overlap < MIN_SEAM:
                    continue
                # A small piece gets a small knob, so its label still has room.
                r = min(R, overlap / 3.2, across / DIV)
                if r < R_MIN:
                    continue
                mid, sign = (lo + hi) / 2, rng.choice((1, -1))
                if vertical:
                    knobs[pi]['right'].append((mid - py, sign, r))
                    knobs[qi]['left'].append(((qy + qh) - mid, -sign, r))
                else:
                    knobs[pi]['top'].append(((px + pw) - mid, sign, r))
                    knobs[qi]['bottom'].append((mid - qx, -sign, r))
    return knobs


def outline(rect, kn):
    """Counter-clockwise polygon of a piece with its knobs and notches."""
    x, y, w, h = rect
    corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    names = ['bottom', 'right', 'top', 'left']
    pts = []
    for k in range(4):
        p0, p1 = np.array(corners[k]), np.array(corners[(k + 1) % 4])
        u = (p1 - p0) / np.linalg.norm(p1 - p0)
        n = np.array([u[1], -u[0]])
        pts.append(tuple(p0))
        for s, sign, r in sorted(kn.get(names[k], [])):
            e2 = sign * n
            c = p0 + u * s + e2 * r * DEPTH_K
            for phi in np.linspace(math.radians(-120), math.radians(-420), 28):
                pts.append(tuple(c + r * (math.cos(phi) * u + math.sin(phi) * e2)))
    return pts


class _Measure:
    def __init__(self, fig, ax):
        self.fig, self.ax = fig, ax
        fig.canvas.draw()
        self.rend = fig.canvas.get_renderer()

    def width(self, s, size, weight='normal', rotation=0):
        t = text(self.ax, 0, 0, s, size=size, weight=weight, rotation=rotation)
        self.fig.canvas.draw()
        b = t.get_window_extent(self.rend)
        t.remove()
        return b.width / self.fig.dpi, b.height / self.fig.dpi


def _wrap(s):
    words = s.split()
    if len(words) < 2:
        return None
    k = min(range(1, len(words)),
            key=lambda k: abs(len(' '.join(words[:k])) - len(' '.join(words[k:]))))
    return ' '.join(words[:k]) + '\n' + ' '.join(words[k:])


def _label(ax, m, d, n, rect, kn):
    """Name in Heavy with the count under it; falls back to a wrapped name,
    an inline count, then a rotated label, stepping the size down each pass."""
    x, y, w, h = rect

    def inset(edge):
        deep = [r for _, sign, r in kn.get(edge, []) if sign < 0]
        return max(deep) * (1 + DEPTH_K) + 0.025 if deep else 0.04
    bw = w - inset('left') - inset('right')
    bh = h - inset('top') - inset('bottom')
    area = w * h
    start = C.H2 if area >= 2.0 else C.H3 if area >= 0.8 else C.BODY if area >= 0.4 else C.META
    cx, cy = x + w / 2, y + h / 2
    for size in [s for s in (C.H2, C.H3, C.BODY, C.META) if s <= start]:
        csize = max(C.META, size - 1.0)
        pitch, cpitch = size / 72 * 1.25, csize / 72 * 1.25
        for name in (d, _wrap(d)):
            if name is None:
                continue
            lines = name.split('\n')
            wide = max(m.width(l, size, 'bold')[0] for l in lines)
            tall = len(lines) * pitch + cpitch
            if wide <= bw and tall <= bh:
                top = cy + tall / 2
                text(ax, cx, top - len(lines) * pitch / 2, name, size=size, weight='bold', ha='center')
                text(ax, cx, top - len(lines) * pitch - cpitch / 2, f'({n})', size=csize,
                     color=C.GREY, ha='center')
                return
        inline = f'{d} ({n})'
        wide = m.width(inline, size, 'bold')[0]
        if wide <= bw and pitch <= bh:
            text(ax, cx, cy, inline, size=size, weight='bold', ha='center')
            return
        if h > w:                                   # stand the label up
            if m.width(d, size, 'bold')[0] <= bh and pitch + cpitch <= bw:
                text(ax, cx + cpitch / 2, cy, d, size=size, weight='bold', ha='center', rotation=90)
                text(ax, cx - pitch / 2, cy, f'({n})', size=csize, color=C.GREY, ha='center', rotation=90)
                return
            if wide <= bh and pitch <= bw:
                text(ax, cx, cy, inline, size=size, weight='bold', ha='center', rotation=90)
                return
            wrapped = _wrap(d)
            if wrapped:                             # two rotated lines plus the count
                lines = wrapped.split('\n')
                if max(m.width(l, size, 'bold')[0] for l in lines) <= bh and 2 * pitch + cpitch <= bw:
                    text(ax, cx + cpitch / 2, cy, wrapped, size=size, weight='bold', ha='center',
                         rotation=90)
                    text(ax, cx - pitch, cy, f'({n})', size=csize, color=C.GREY, ha='center',
                         rotation=90)
                    return
    # Last resort: the name alone, at the smallest size, and say so loudly.
    wide, tall = m.width(d, C.META, 'bold')
    if wide <= bw and tall <= bh:
        text(ax, cx, cy, d, size=C.META, weight='bold', ha='center')
        print(f'WARNING: {d!r} lost its count ({n}) in a {w:.2f} x {h:.2f} in piece')
        return
    raise ValueError(f'{d!r} ({n}) does not fit a {w:.2f} x {h:.2f} in piece')


def treemap(fig, ax, counts, family_of, x0, x1, bot, top, *, seed=7):
    """Draw one jigsaw panel. `counts`: domain -> task count."""
    for f in set(family_of.values()):
        assert f in HUE, f'unknown area {f!r}; add it to jigsaw.HUE'
    pieces = layout(counts, family_of, x0, x1, bot, top)
    knobs = knobs_for(pieces, seed)
    for (d, f, rect), kn in zip(pieces, knobs):
        ax.add_patch(Polygon(outline(rect, kn), closed=True, facecolor=fill(f),
                             edgecolor=C.INK, linewidth=0.8, joinstyle='round', zorder=2))
    m = _Measure(fig, ax)
    for (d, f, rect), kn in zip(pieces, knobs):
        _label(ax, m, d, counts[d], rect, kn)
    return pieces


def legend(fig, ax, areas, x0, x1, y, pitch=0.16):
    """Legend rows of area dots, in HUE order, wrapping at x1. Counts stay on
    the pieces, since each panel has its own. Returns the rows used."""
    m = _Measure(fig, ax)
    xx, yy, rows = x0, y, 1
    for f in HUE:
        if f not in areas:
            continue
        s = f
        wd = 0.13 + m.width(s, C.BODY)[0]
        if xx + wd > x1:
            xx, yy, rows = x0, yy - pitch, rows + 1
        ax.add_patch(Circle((xx + DOT_R, yy), DOT_R, facecolor=fill(f), edgecolor=C.INK,
                            linewidth=0.6, zorder=3))
        text(ax, xx + 0.13, yy, s, size=C.BODY)
        xx += wd + 0.20
    return rows
