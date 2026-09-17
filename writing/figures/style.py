"""Announcement-clean matplotlib style: Google palette, venue-matched serif
type, L-spine ink frame, and left-aligned bold titles with a legend row
above the axes.

Usage: apply_style(venue='arxiv'|'iclr'|...) once, plot, set_title() per axes,
header_legend() or fig_header_legend() for series identity, finalize_headers(fig)
before savefig. Save PDF (the shipping artifact) plus a dpi=200 PNG preview.

The venue picks the figure's body face so a figure placed at 1:1 matches the
page it sits on: Palatino for a mathpazo template, Times for one that loads
times. See VENUE_FONT.
"""
import glob
import os

import matplotlib.colors as mc
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from matplotlib.transforms import ScaledTranslation

# Ink frame + neutrals. Neutrals never count as series hues.
INK = '#1a1a1a'          # spines / ticks / titles
HUMAN_DARK = '#2b2b2b'   # primary human/neutral series
HUMAN_SOFT = '#8a8a8a'   # secondary human/neutral series
REF_GREY = '#828589'     # every reference line: this grey ...
REF_DASH = (0, (3, 2.2))  # ... with this one dash pattern


# Figure text matches the body text of the venue, so a figure placed at 1:1
# reads as part of the page. Pick with apply_style(venue=...).
#   'arxiv'  mathpazo  -> Palatino, via TeX Gyre Pagella
#   'iclr'   times     -> Times, via TeX Gyre Termes
# matplotlib bundles neither face: without registration the stack falls back to
# DejaVu Serif and the figure silently stops matching the page.
VENUE_FONT = {
    'arxiv': ('texgyrepagella-*.otf', ['TeX Gyre Pagella', 'Palatino', 'Palatino Linotype',
                                       'Book Antiqua', 'Computer Modern Roman', 'DejaVu Serif'],
              'Palatino'),
    'iclr': ('texgyretermes-*.otf', ['TeX Gyre Termes', 'Nimbus Roman', 'Times New Roman',
                                     'Times', 'STIXGeneral', 'DejaVu Serif'],
             'STIX'),
}
VENUE_FONT['neurips'] = VENUE_FONT['icml'] = VENUE_FONT['colm'] = VENUE_FONT['arxiv']
VENUE_FONT['cvpr'] = VENUE_FONT['iccv'] = VENUE_FONT['acl'] = VENUE_FONT['iclr']
DEFAULT_VENUE = 'arxiv'


def _register_venue_face(pattern):
    """Register a TeX Gyre face from a TeX Live install, if present.
    macOS exposes Palatino only as a .ttc whose bold face matplotlib cannot
    see, so bold silently renders regular; TeX Gyre ships one .otf per face.
    """
    import glob
    from matplotlib import font_manager
    for root in (
        '/usr/local/texlive/*/texmf-dist/fonts/opentype/public/tex-gyre/',
        '/opt/homebrew/texlive/*/texmf-dist/fonts/opentype/public/tex-gyre/',
        '/usr/share/texmf/fonts/opentype/public/tex-gyre/',
        '/usr/share/texlive/texmf-dist/fonts/opentype/public/tex-gyre/',
    ):
        for path in glob.glob(root + pattern):
            try:
                font_manager.fontManager.addfont(path)
            except Exception:
                pass


# --- Type: two faces, one scale ---------------------------------------------
# Ticks, axis labels and math take the venue's body serif, so the figure reads
# as part of the page. The headline and the legend row take Lato, the face the
# arxiv template sets its section titles in. Every figure in this plugin uses
# that split and this scale; a figure that wants a sixth size is saying too much.
#
#   HEADLINE  10.5  Lato Heavy    the figure's claim, or a grid's figure title
#   PANEL      8.5  Lato Heavy    one panel's title inside a grid
#   LEGEND     8.0  Lato Regular  the header legend row
#   LABEL      8.0  serif         axis labels
#   TICK       7.5  serif         tick labels
#   NOTE       7.0  Lato Regular  annotations placed in the plot
#
# The scale assumes the shipping geometry: 5.5 in wide, placed at 1:1.
HEADLINE_PT, PANEL_PT, LEGEND_PT, LABEL_PT, TICK_PT, NOTE_PT = 10.5, 8.5, 8.0, 8.0, 7.5, 7.0
WIDTH_1COL, WIDTH_FULL = 5.5, 7.6

LATO_DIRS = [os.path.expanduser('~/texmf/fonts/truetype/typoland/lato'),
             '/usr/local/texlive/*/texmf-dist/fonts/truetype/typoland/lato',
             '/opt/homebrew/texlive/*/texmf-dist/fonts/truetype/typoland/lato',
             '/usr/share/texlive/texmf-dist/fonts/truetype/typoland/lato',
             '/usr/share/texmf/fonts/truetype/typoland/lato']


def sized(fp, pt):
    """A copy of a FontProperties at `pt`. A face loaded from a file carries
    its own size, and matplotlib's `prop=` beats `fontsize=`, so anything that
    passes `prop` must size it here first."""
    fp = fp.copy()
    fp.set_size(pt)
    return fp


def lato_fonts():
    """(HEAVY, REGULAR) FontProperties for the headline face, registering Lato
    from TeX Live on the first call. Falls back to the default sans, which
    changes the metrics, so check a figure rendered without Lato before it
    ships."""
    global _LATO_CACHE
    if _LATO_CACHE is None:
        faces = [f for d in LATO_DIRS for f in glob.glob(d + '/Lato-*.ttf')]
        for face in faces:
            try:
                from matplotlib import font_manager
                font_manager.fontManager.addfont(face)
            except Exception:
                pass
        heavy = next((f for f in faces if f.endswith('Lato-Heavy.ttf')), None)
        regular = next((f for f in faces if f.endswith('Lato-Regular.ttf')), None)
        _LATO_CACHE = (
            fm.FontProperties(fname=heavy) if heavy else fm.FontProperties(weight='bold'),
            fm.FontProperties(fname=regular) if regular else fm.FontProperties(),
            'Lato' if faces else 'DejaVu Sans',
        )
    return _LATO_CACHE[0], _LATO_CACHE[1]


def sans_name():
    """The registered headline family name, for rcParams that take a name."""
    lato_fonts()
    return _LATO_CACHE[2]


_LATO_CACHE = None


def apply_style(venue=DEFAULT_VENUE):
    face_glob, serif_stack, math_rm = VENUE_FONT[venue]
    _register_venue_face(face_glob)
    lato_fonts()
    plt.rcParams.update({
        # Body face of the venue + STIX math. The first entry is the TeX Gyre
        # clone, for its real bold face; the DejaVu tail catches unicode glyphs.
        'font.family': ['serif', 'DejaVu Sans'],
        'font.serif': serif_stack,
        'mathtext.fontset': 'stix',
        'mathtext.rm': math_rm,
        'mathtext.it': f'{math_rm}:italic',
        'mathtext.bf': f'{math_rm}:bold',
        # Frame: L-spines only, ink, no grid.
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.linewidth': 0.9,
        'axes.edgecolor': INK,
        'axes.labelcolor': INK,
        'axes.titlecolor': INK,
        'text.color': INK,
        'axes.grid': False,
        # Titles: left-aligned, Lato Heavy, the only heavy text in a figure.
        # header() sets the face per call; these cover a bare set_title.
        'axes.titlelocation': 'left',
        'axes.titlesize': HEADLINE_PT,
        'axes.titleweight': 'bold',
        'axes.labelsize': LABEL_PT,
        'xtick.labelsize': TICK_PT,
        'ytick.labelsize': TICK_PT,
        'xtick.color': INK,
        'ytick.color': INK,
        'xtick.direction': 'out',
        'ytick.direction': 'out',
        'xtick.major.size': 3.5,
        'ytick.major.size': 3.5,
        'xtick.major.width': 0.7,
        'ytick.major.width': 0.7,
        'legend.fontsize': LEGEND_PT,
        'legend.frameon': False,
        'lines.linewidth': 1.3,
        'lines.markersize': 4.2,
        'figure.dpi': 120,
        'savefig.dpi': 200,
        # Never tight-crop: it changes the canvas, so LaTeX rescales the figure
        # and every font inside it. DOCTRINE.md rule 1.
        'savefig.bbox': None,
        # With no tight crop the canvas is fixed, so the layout engine has to
        # fit the content inside it. A template that sets its own margins turns
        # this off with fig.set_layout_engine('none').
        'figure.constrained_layout.use': True,
        'figure.constrained_layout.h_pad': 0.03,
        'figure.constrained_layout.w_pad': 0.03,
        'pdf.fonttype': 42,
    })


def clean_axes(ax):
    """Re-assert the L-spine ink frame on axes the rc cannot reach
    (twinx / secondary_xaxis) or that a plotting call restyled."""
    ax.grid(False)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('left', 'bottom'):
        ax.spines[side].set_color(INK)
        ax.spines[side].set_linewidth(0.9)
    ax.tick_params(colors=INK, width=0.8, length=3.5, direction='out')


# --- Palette: Google brand colors -------------------------------------------
G_BLUE = '#4285F4'
G_RED = '#DB4437'
G_YELLOW = '#F4B400'
G_GREEN = '#0F9D58'
G_GREY = '#5F6368'    # neutral text grey, used as-is
G_PURPLE = '#AB47BC'  # Material extension for a 5th distinct hue


def _mix(hex_color, target, amount):
    rgb = mc.to_rgb(hex_color)
    tgt = mc.to_rgb(target)
    return mc.to_hex(tuple(c * (1 - amount) + t * amount
                           for c, t in zip(rgb, tgt)))


def lighten(hex_color, amount):
    return _mix(hex_color, '#ffffff', amount)


def darken(hex_color, amount):
    return _mix(hex_color, '#000000', amount)


# Softness tiers: (lighten, desaturate) toward white / greyscale.
# brand = hero graphics, medium = paper series colors, paper = default
# softened tone, soft = slides, mute = background fills.
TIERS = {
    'brand':  (0.00, 0.00),
    'medium': (0.22, 0.06),
    'paper':  (0.32, 0.10),
    'soft':   (0.42, 0.16),
    'mute':   (0.50, 0.22),
}
DEFAULT_TIER = 'paper'

# Hex per (color, tier) — regenerate with `python style.py`:
#  color   | brand    | medium   | paper    | soft     | mute
#  --------|----------|----------|----------|----------|----------
#  blue    | #4285f4  | #6fa1f2  | #84adf1  | #99baf0  | #a9c4ef
#  red     | #db4437  | #de6f66  | #df837b  | #e09790  | #e1a7a1
#  yellow  | #f4b400  | #f2c33f  | #f1c95b  | #efd078  | #eed58f
#  green   | #0f9d58  | #47af7d  | #61b88d  | #7ac09e  | #8fc6ab
#  purple  | #ab47bc  | #bc73c9  | #c487ce  | #cc9bd4  | #d2abd9


def apply_tier(base, tier=DEFAULT_TIER):
    """Soften a brand color by the tier's (lighten, desaturate) amounts."""
    lighten_amt, desat_amt = TIERS[tier]
    rgb = [c + (1 - c) * lighten_amt for c in mc.to_rgb(base)]
    grey = sum(rgb) / 3
    return mc.to_hex([c * (1 - desat_amt) + grey * desat_amt for c in rgb])


def paper(base):
    """Alias: brand color at the default tier."""
    return apply_tier(base, DEFAULT_TIER)


def twotone(base, tier=DEFAULT_TIER):
    """(dark, light) pair of ONE hue for a 2-series chart. For bars, draw
    the light series with edgecolor=dark to keep a crisp outline."""
    dark = darken(apply_tier(base, tier), 0.30)
    return dark, lighten(dark, 0.55)


def hue_ramp(base, n, tier='medium', light=0.55, dark=0.32):
    """n lightness steps of ONE hue, index 0 lightest -> n-1 darkest.
    The single-hue rule for figures with at most 3 series; use distinct
    Google hues once a figure has more."""
    anchor = apply_tier(base, tier)
    if n == 1:
        return [anchor]
    stops = [light - (light + dark) * i / (n - 1) for i in range(n)]
    return [lighten(anchor, s) if s >= 0 else darken(anchor, -s)
            for s in stops]


def family_4(base, tier=DEFAULT_TIER):
    """4-step ordered gradient: lightest, light, tier mid, gentle dark."""
    return [lighten(base, 0.65), lighten(base, 0.42),
            apply_tier(base, tier), darken(base, 0.22)]


# --- Announcement header: title + legend row above the axes -----------------

def legend_handles(entries):
    """Proxy handles for header rows. Each entry is (label, color) for a
    white-edged dot, or (label, color, marker) where marker is a marker
    char, '-' for a solid-line proxy, or '--' for the reference dash."""
    handles = []
    for entry in entries:
        label, color, marker = (entry if len(entry) == 3 else (*entry, 'o'))
        if marker == '--':
            handles.append(Line2D([0], [0], color=color, linestyle=REF_DASH,
                                  linewidth=1.4, label=label))
        elif marker == '-':
            handles.append(Line2D([0], [0], color=color, linestyle='-',
                                  linewidth=1.6, label=label))
        else:
            handles.append(Line2D([0], [0], marker=marker, color='none',
                                  markerfacecolor=color,
                                  markeredgecolor='white',
                                  markeredgewidth=0.8, markersize=6.0,
                                  label=label))
    return handles


def _left_title(ax):
    """The left-title artist. `ax.title` is the CENTRE one, so reading it for a
    figure titled with loc='left' silently returns an empty text."""
    return getattr(ax, '_left_title', ax.title)


def header(ax, title, entries=None, ncol=None, size=None):
    """THE standard header: a left-aligned Lato Heavy title with, under it, a
    single Lato Regular legend row above the axes. Every chart in this plugin
    ends with one `header(...)` per axes and one `finalize_headers(fig)`.

    `size` defaults to HEADLINE_PT for a single-panel figure; pass PANEL_PT for
    one panel of a grid whose figure-level title comes from fig_header().
    `entries` may be None for a figure that needs no legend.
    """
    heavy, _ = lato_fonts()
    ax.set_title(title, loc='left', fontproperties=heavy,
                 fontsize=size or HEADLINE_PT, color=INK)
    if entries:
        header_legend(ax, entries, ncol=ncol)
    return ax


def fig_header(fig, title, entries=None, ncol=None):
    """Figure-level title and one legend row above a whole panel grid, both
    left-aligned to the figure. Needs constrained_layout. Panels then take
    header(ax, 'Panel title', size=PANEL_PT) with no entries of their own."""
    heavy, _ = lato_fonts()
    fig.suptitle(title, x=0.008, ha='left', fontproperties=heavy,
                 fontsize=HEADLINE_PT, color=INK)
    if entries:
        fig_header_legend(fig, entries, ncol=ncol)
    return fig


def header_legend(ax, entries, ncol=None, legend_size=None):
    """The legend row on its own, between an already-set title and the plot.
    Prefer header(); this stays for a figure that titles its axes elsewhere."""
    _, regular = lato_fonts()
    size = legend_size or LEGEND_PT
    handles = legend_handles(entries)
    n = ncol or len(handles)
    rows = -(-len(handles) // n)
    t = _left_title(ax)
    if t.get_text():  # rough reservation; finalize_headers measures the real pad
        ax.set_title(t.get_text(), loc='left', pad=8 + rows * (size + 4.5),
                     fontproperties=t.get_fontproperties())
    return ax.legend(handles=handles, loc='lower left',
                     bbox_to_anchor=(-0.01, 1.0), ncol=n,
                     frameon=False, prop=sized(regular, size),
                     handletextpad=0.3, columnspacing=0.9,
                     labelcolor=INK, borderpad=0.0, borderaxespad=0.0)


def fig_header_legend(fig, entries, ncol=None, legend_size=None):
    """Figure-level legend row above all panels, left-aligned.
    Requires constrained_layout."""
    _, regular = lato_fonts()
    # Plain loc, not 'outside ...': finalize_headers reserves the band itself and
    # seats this row under the figure title, which the outside placement cannot
    # do -- both artists land at the top of the same band and collide.
    return fig.legend(handles=legend_handles(entries),
                      loc='upper left', bbox_to_anchor=(0.008, 1.0),
                      bbox_transform=fig.transFigure,
                      ncol=ncol or len(entries), frameon=False,
                      prop=sized(regular, legend_size or LEGEND_PT),
                      labelcolor=INK, handletextpad=0.3, columnspacing=0.9)


def note(ax, x, y, text, **kw):
    """A short label placed directly at a point, Lato Regular, no leader line.
    The standard replacement for an in-axes legend entry."""
    _, regular = lato_fonts()
    kw.setdefault('ha', 'center')
    kw.setdefault('va', 'bottom')
    kw.setdefault('color', G_GREY)
    return ax.text(x, y, text, fontproperties=sized(regular, kw.pop('fontsize', NOTE_PT)), **kw)


def finalize_headers(fig, gap=6.0, min_pad=8.0, level_all=True):
    """Measure-and-level pass; call ONCE, after all set_title /
    header_legend calls and right before savefig.

    Draws the canvas, measures each header legend's height in points, sets
    every left title to one shared pad (tallest legend + a `gap` on each
    side), and re-anchors each legend so its top hangs `gap` below the
    title. Title, legend, and plot are therefore equidistant, level across
    panels, and independent of font sizes. Returns the pad.

    level_all=False pads only axes that carry a legend — for figures whose
    legend-less panels sit in their own row under a figure-level header.
    """
    fig.canvas.draw()
    dpi = fig.dpi
    heights = {}
    for ax in fig.axes:
        leg = ax.get_legend()
        if leg is not None:
            heights[ax] = leg.get_window_extent().height * 72.0 / dpi
    pad = max([min_pad] + [h + 2 * gap for h in heights.values()])
    for ax in fig.axes:
        t = _left_title(ax)
        if t.get_text() and (level_all or ax in heights):
            ax.set_title(t.get_text(), loc='left', pad=pad,
                         fontproperties=t.get_fontproperties())
        leg = ax.get_legend()
        if leg is not None:
            # loc first: set_loc() resets the anchor, so anchoring before it
            # leaves the legend hanging from its lower edge, on top of the title.
            if hasattr(leg, 'set_loc'):
                leg.set_loc('upper left')
            else:
                leg._loc = 2
            # Offset in POINTS off the axes' top-left, not in axes fractions: a
            # layout engine resizes the axes after this runs, and a fractional
            # anchor would then land somewhere else while the title pad, in
            # points, stayed put.
            off = ScaledTranslation(0, (pad - gap) / 72.0, fig.dpi_scale_trans)
            leg.set_bbox_to_anchor((-0.01, 1.0), transform=ax.transAxes + off)
    _stack_figure_header(fig, gap)
    return pad


def _stack_figure_header(fig, gap):
    """Reserve a band at the top of the canvas for a figure-level title and its
    legend row, then seat them in it with one `gap` between and around them.

    The layout engine reserves nothing for either artist once they are placed by
    hand, so the band is measured here and handed back to the engine as `rect`.
    """
    leg = fig.legends[0] if fig.legends else None
    sup = getattr(fig, '_suptitle', None)
    if leg is None and sup is None:
        return
    fig.canvas.draw()
    height = fig.get_window_extent().height
    gpx = gap * fig.dpi / 72.0
    h_leg = leg.get_window_extent().height if leg is not None else 0.0
    h_sup = sup.get_window_extent().height if sup is not None and sup.get_text() else 0.0
    band = h_leg + h_sup + gpx * (1 + (1 if h_leg and h_sup else 0))
    engine = fig.get_layout_engine()
    if engine is not None and hasattr(engine, 'set'):
        try:
            engine.set(rect=(0, 0, 1, max(0.35, 1.0 - band / height)))
            fig.canvas.draw()
        except (TypeError, ValueError):
            pass
    if h_sup:
        sup.set_verticalalignment('top')
        sup.set_y(1.0)
    if leg is not None:
        if hasattr(leg, 'set_loc'):
            leg.set_loc('upper left')
        leg.set_bbox_to_anchor((0.008, 1.0 - (h_sup + (gpx if h_sup else 0)) / height),
                               transform=fig.transFigure)


# --- Extras -----------------------------------------------------------------

def rounded_bar(ax, cx, top, w, r_frac=0.10, **kw):
    """Bar with rounded TOP corners; the base sits square on ylim[0].
    Call after xlim/ylim are final so the corners read as circular."""
    rx = w * r_frac
    (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()
    pos, (fw, fh) = ax.get_position(), ax.figure.get_size_inches()
    ry = rx * (pos.width * fw / (x1 - x0)) / (pos.height * fh / (y1 - y0))
    ry = min(ry, (top - y0) / 2)
    left, right = cx - w / 2, cx + w / 2
    verts = [(left, y0), (left, top - ry), (left, top), (left + rx, top),
             (right - rx, top), (right, top), (right, top - ry),
             (right, y0), (left, y0)]
    codes = [Path.MOVETO, Path.LINETO, Path.CURVE3, Path.CURVE3,
             Path.LINETO, Path.CURVE3, Path.CURVE3, Path.LINETO,
             Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts, codes), **kw))


def arrow(text, direction='down'):
    """Append a direction arrow to a label: arrow('Loss') -> 'Loss ↓'."""
    arr = r'$\downarrow$' if direction == 'down' else r'$\uparrow$'
    return f'{text} {arr}'


def all_tiers_table():
    """Print the hex-per-tier table (source of the comment block above)."""
    names = ['blue', 'red', 'yellow', 'green', 'purple']
    bases = [G_BLUE, G_RED, G_YELLOW, G_GREEN, G_PURPLE]
    tiers = list(TIERS)
    print(' color   | ' + ' | '.join(f'{t:8s}' for t in tiers))
    print(' --------|' + '|'.join(['----------'] * len(tiers)))
    for name, base in zip(names, bases):
        cells = [apply_tier(base, t) for t in tiers]
        print(f' {name:7s} | ' + ' | '.join(f'{c:8s}' for c in cells))


if __name__ == '__main__':
    all_tiers_table()
