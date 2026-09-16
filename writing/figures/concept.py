"""Shared print-scale design system for concept diagrams (templates 50-52).

Coordinates are inches; canvas width equals the manuscript's 5.5-in textwidth.
Blue: agent work / visible exchanges. Red: authors' contribution / private
reference. Grey: infrastructure. Labels carry meaning independently of colour.
Exports preserve the canvas and editable text, irrespective of working directory.
"""
import glob
import os
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import style

# The two faces the arxiv template's Figure 1 uses: Lato Heavy for the headline,
# the same face as arxivtmpl's section titles, and Lato Regular for everything
# else. TeX Live ships both; register them rather than letting matplotlib pick
# an OS substitute.
LATO_DIRS = [os.path.expanduser('~/texmf/fonts/truetype/typoland/lato'),
             '/usr/local/texlive/*/texmf-dist/fonts/truetype/typoland/lato',
             '/usr/share/texlive/texmf-dist/fonts/truetype/typoland/lato',
             '/usr/share/texmf/fonts/truetype/typoland/lato']
_faces = [f for d in LATO_DIRS for f in glob.glob(d + '/Lato-*.ttf')]
for _face in _faces:
    fm.fontManager.addfont(_face)
SANS = 'Lato' if _faces else 'DejaVu Sans'
HEAVY = fm.FontProperties(fname=next(f for f in _faces if f.endswith('Lato-Heavy.ttf'))) \
    if _faces else fm.FontProperties(weight='bold')

OUT = Path.cwd()
INK, GREY = '#333333', style.G_GREY
# House rule: the paper tier is the default for figures, the brand tier is kept
# for places that need maximum recognition. Lines and marks therefore sit one
# step darker than paper so a hairline still reads, and fills are tints of the
# same Google hues.
BLUE, RED = style.apply_tier(style.G_BLUE, 'medium'), style.apply_tier(style.G_RED, 'medium')
EDGE = style.lighten(GREY, 0.72)
PALE = style.lighten(GREY, 0.965)
BLUE_FILL, RED_FILL = style.lighten(style.G_BLUE, 0.93), style.lighten(style.G_RED, 0.93)

# A node's band colour says whose side the node is on, and nothing else. Every
# figure in the paper uses these three and no others:
#
#   BLUE_FILL   the agent's side: what it holds, what it may change
#   RED_FILL    withheld from the agent: the authors' contribution, the
#               reference restored from it, the videos it is graded on
#   PALE        neither side: the channel between them, and the criteria
#
# Connectors are always grey, in both figures, because an arrow is a relation
# rather than a party to it.
# The type scale every figure in this paper uses. Two faces only, so the three
# Heavy levels separate by size and the two Regular levels separate by size and
# colour. Nothing else is permitted; a sixth level means the figure is trying
# to say too much.
#
#   H1    11.0  Heavy    the figure's headline claim
#   H2     8.5  Heavy    panel heading, the a / b / c row
#   H3     7.5  Heavy    node title, inside the coloured band
#   BODY   7.0  Regular  node body, the substance
#   META   6.5  Regular  secondary line, always grey
H1, H2, H3, BODY, META = 11.0, 8.5, 7.5, 7.0, 6.5
SMALL, HEAD = BODY, H2      # older names, kept so no call site breaks

# Headline geometry, shared by every figure so the gap above the blocks is the
# same everywhere. H1_HALF is the measured half-height of one 11.0pt Heavy line
# box, which matplotlib centres on the y passed to text().
TOP_PAD, TITLE_GAP, H1_HALF = 0.10, 0.14, 0.0917


def half_for(size):
    """Half-height of one text line box at `size`. Matplotlib centres that box
    on the y passed to text(), and its height scales linearly with the font
    size, so every figure derives its spacing from the measured H1 box rather
    than from a number someone eyeballed."""
    return H1_HALF * size / H1


def height_for(content_top):
    """Canvas height that seats the headline above a figure whose topmost block
    edge is at `content_top`. Call it instead of hard-coding a height."""
    return content_top + 2 * H1_HALF + TOP_PAD + TITLE_GAP


def headline_y(height):
    """The y every figure passes to headline(), derived from its canvas."""
    return height - TOP_PAD - H1_HALF


def canvas(width, height):
    plt.rcParams.update({
        'text.usetex': False,
        'font.family': SANS, 'font.size': BODY, 'text.color': INK,
        'svg.fonttype': 'path', 'savefig.bbox': None, 'savefig.pad_inches': 0,
        'figure.facecolor': 'white', 'axes.grid': False,
        'pdf.fonttype': 42, 'ps.fonttype': 42,
    })
    fig = plt.figure(figsize=(width, height))
    ax = fig.add_axes([0, 0, 1, 1], xlim=(0, width), ylim=(0, height))
    ax.set_axis_off()
    return fig, ax


def text(ax, x, y, s, *, size=BODY, color=INK, ha='left', va='center',
         weight='normal', mono=False, **kwargs):
    """Only two faces are available, so `weight='bold'` selects Lato Heavy and
    everything else is Lato Regular. `mono` is accepted for call-site clarity on
    file paths but does not switch face: a third family would break the rule."""
    if weight == 'bold':
        kwargs['fontproperties'] = HEAVY
    return ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va,
                   linespacing=1.2, zorder=6, **kwargs)



PANELS = []   # every drawn container, so save() can catch text that spills out


def box(ax, x, y, w, h, *, face='white', edge=EDGE, lw=0.55, r=0.025, track=False,
        **kwargs):
    patch = FancyBboxPatch((x, y), w, h,
                          boxstyle=f'round,pad=0,rounding_size={r}',
                          facecolor=face, edgecolor=edge, linewidth=lw, zorder=2,
                          **kwargs)
    ax.add_patch(patch)
    if track:
        PANELS.append((x, y, w, h))
    return patch


def rule(ax, x0, y0, x1, y1, *, color=EDGE, lw=0.55, ls='-'):
    ax.plot([x0, x1], [y0, y1], color=color, lw=lw, linestyle=ls,
            solid_capstyle='butt', zorder=3)


def arrow(ax, x0, y0, x1, y1, *, color=GREY, lw=0.7, ls='-', both=False, curve=0):
    # One arrow form throughout: thin line, open V head, same head size.
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1),
                 arrowstyle='<->' if both else '->', mutation_scale=7,
                 connectionstyle=f'arc3,rad={curve}',
                 color=color, linewidth=lw, linestyle=ls, shrinkA=0, shrinkB=0,
                 zorder=4))


def node(ax, x, y, w, h, title, *, tint=PALE):
    """Small coloured header identifies the object; the body stays white."""
    box(ax, x, y, w, h, face='white', track=True)
    band = box(ax, x, y + h - 0.25, w, 0.25, face=tint, edge='none')
    # Keep the header fill within the same rounded silhouette as the outline.
    band.set_clip_path(box(ax, x, y, w, h, face='none'))
    text(ax, x + 0.08, y + h - 0.125, title, size=H3, weight='bold')


def headline(ax, x, y, claim):
    """Top-left headline stating what the figure shows, as a claim rather than
    a label, following the plot skill's title rule."""
    text(ax, x, y, claim, size=H1, weight='bold', color='black')


def heading(ax, x, y, letter, title):
    text(ax, x, y, letter, size=H2, weight='bold', color='black')
    text(ax, x + 0.20, y, title, size=H2, weight='bold')


def check(fig):
    """Raise if any text leaves the canvas or runs past the panel it starts in.
    Every template ends with this; save() calls it too."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    frame = fig.bbox
    for ax in fig.axes:
        for label in ax.texts:
            bounds = label.get_window_extent(renderer)
            if not frame.contains(bounds.x0, bounds.y0) or not frame.contains(bounds.x1, bounds.y1):
                raise ValueError(f'Text outside the canvas: {label.get_text()}')
            # A label that starts inside a panel has to finish inside it too.
            # Changing face or wording silently widens text, so check rather
            # than eyeball it.
            x0, x1 = (b / fig.dpi for b in (bounds.x0, bounds.x1))
            y0, y1 = (b / fig.dpi for b in (bounds.y0, bounds.y1))
            for px, py, pw, ph in PANELS:
                inside = px <= x0 <= px + pw and py <= y0 and y1 <= py + ph
                if inside and x1 > px + pw - 0.03:
                    raise ValueError(
                        f'"{label.get_text()}" runs past its panel by '
                        f'{x1 - (px + pw):+.3f} in')
    PANELS.clear()


def save(fig, stem):
    """check(), then write <stem>.pdf / .svg / .png next to the caller.
    Never tight-crop: it changes the effective font size in LaTeX."""
    check(fig)
    for ext, options in [('pdf', {}), ('svg', {}), ('png', {'dpi': 400})]:
        target = OUT / f'{stem}.{ext}'
        fig.savefig(target, **options)
        if ext == 'svg':
            target.write_text('\n'.join(line.rstrip() for line in target.read_text().splitlines()) + '\n')
    plt.close(fig)
