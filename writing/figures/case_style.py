"""Shared look for a set of small case-study figures, so they read as one set
and match the concept diagrams drawn with concept.py: Lato Heavy for the
headline and the panel titles, Lato Regular for everything else, the type scale
of concept.py (H1 11 for the headline claim, H2 8.5 for panel titles, BODY 7 for
ticks and labels, META 6.5 for notes). Canvas 5.5 in wide, inserted at 1:1.

One hue carries the subject of the figure and grey carries everything set aside,
which lets a reader compare panels without a legend: see DOCTRINE.md rule 4 for
what a colour is allowed to mean.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import concept as C
import style

BLUE = style.apply_tier(style.G_BLUE, 'medium')
DARK = style.apply_tier(style.G_BLUE, 'brand')
LIGHT = style.lighten(style.G_BLUE, 0.55)
GREY = style.lighten(style.G_GREY, 0.30)
ANN = style.G_GREY
INK = C.INK

H1, H2, BODY, META = 10.0, C.H2, C.BODY, C.META
MK = dict(marker='o', ms=3.6, markeredgecolor='white', markeredgewidth=0.6)
LW = 1.2
WIDTH, HEIGHT = 5.5, 2.05
HEAD_Y = 0.955           # headline baseline, figure fraction
TOP, BOTTOM = 0.73, 0.20


def setup():
    style.apply_style()
    plt.rcParams.update({
        'font.family': C.SANS, 'text.usetex': False,
        'axes.grid': False, 'axes.spines.top': False, 'axes.spines.right': False,
        'axes.edgecolor': INK, 'xtick.color': INK, 'ytick.color': INK,
        'axes.labelcolor': INK, 'text.color': INK,
        'font.size': BODY, 'axes.labelsize': BODY,
        'xtick.labelsize': BODY, 'ytick.labelsize': BODY,
        'xtick.major.size': 2.5, 'ytick.major.size': 2.5,
        'xtick.major.width': 0.6, 'ytick.major.width': 0.6, 'axes.linewidth': 0.6,
        'savefig.bbox': None, 'pdf.fonttype': 42,
    })


def canvas(width_ratios, wspace):
    fig, axes = plt.subplots(1, len(width_ratios), figsize=(WIDTH, HEIGHT), squeeze=False,
                             gridspec_kw=dict(left=0.075, right=0.99, bottom=BOTTOM, top=TOP,
                                              wspace=wspace, width_ratios=width_ratios))
    return fig, list(axes[0])


def headline(fig, claim):
    """The figure's claim, Lato Heavy H1, top left, as in Figures 1 and 2."""
    fig.text(0.075, HEAD_Y, claim, fontproperties=C.HEAVY, fontsize=H1, color='black',
             ha='left', va='top')


def title(ax, s):
    """Panel title, Lato Heavy H2, left-aligned above the axes."""
    ax.set_title(s, fontproperties=C.HEAVY, fontsize=H2, loc='left', pad=5, color=INK)


def note(ax, x, y, s, **kw):
    """A short label placed directly at a point, no leader line."""
    kw.setdefault('ha', 'center')
    kw.setdefault('va', 'bottom')
    kw.setdefault('color', ANN)
    ax.text(x, y, s, fontsize=META, **kw)
