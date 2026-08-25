"""Announcement-clean matplotlib style: Google palette, Palatino/Pagella
type, L-spine ink frame, and left-aligned bold titles with a legend row
above the axes.

Usage: apply_style() once, plot, set_title() per axes, header_legend() or
fig_header_legend() for series identity, finalize_headers(fig) before
savefig. Save PDF (the shipping artifact) plus a dpi=200 PNG preview.
"""
import matplotlib.colors as mc
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import PathPatch
from matplotlib.path import Path

# Ink frame + neutrals. Neutrals never count as series hues.
INK = '#1a1a1a'          # spines / ticks / titles
HUMAN_DARK = '#2b2b2b'   # primary human/neutral series
HUMAN_SOFT = '#8a8a8a'   # secondary human/neutral series
REF_GREY = '#828589'     # every reference line: this grey ...
REF_DASH = (0, (3, 2.2))  # ... with this one dash pattern


def _register_pagella():
    """Register TeX Gyre Pagella from a TeX Live install, if present.
    macOS exposes Palatino only as a .ttc whose bold face matplotlib cannot
    see, so bold silently renders regular; Pagella ships one .otf per face.
    """
    import glob
    from matplotlib import font_manager
    for pattern in (
        '/usr/local/texlive/*/texmf-dist/fonts/opentype/public/tex-gyre/texgyrepagella-*.otf',
        '/opt/homebrew/texlive/*/texmf-dist/fonts/opentype/public/tex-gyre/texgyrepagella-*.otf',
        '/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyrepagella-*.otf',
        '/usr/share/texlive/texmf-dist/fonts/opentype/public/tex-gyre/texgyrepagella-*.otf',
    ):
        for path in glob.glob(pattern):
            try:
                font_manager.fontManager.addfont(path)
            except Exception:
                pass


def apply_style():
    _register_pagella()
    plt.rcParams.update({
        # Palatino body + STIX math, matching LaTeX mathpazo. Pagella first
        # for its real bold face; DejaVu tail catches unicode glyphs.
        'font.family': ['serif', 'DejaVu Sans'],
        'font.serif': ['TeX Gyre Pagella', 'Palatino', 'Palatino Linotype',
                       'Book Antiqua', 'Computer Modern Roman', 'Times',
                       'DejaVu Serif'],
        'mathtext.fontset': 'stix',
        'mathtext.rm': 'Palatino',
        'mathtext.it': 'Palatino:italic',
        'mathtext.bf': 'Palatino:bold',
        # Frame: L-spines only, ink, no grid.
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.linewidth': 0.9,
        'axes.edgecolor': INK,
        'axes.labelcolor': INK,
        'axes.titlecolor': INK,
        'text.color': INK,
        'axes.grid': False,
        # Titles: left-aligned bold — the only bold text in a figure.
        'axes.titlelocation': 'left',
        'axes.titlesize': 12.5,
        'axes.titleweight': 'bold',
        'axes.labelsize': 14,
        'xtick.labelsize': 13,
        'ytick.labelsize': 13,
        'xtick.color': INK,
        'ytick.color': INK,
        'xtick.direction': 'out',
        'ytick.direction': 'out',
        'xtick.major.size': 3.5,
        'ytick.major.size': 3.5,
        'xtick.major.width': 0.8,
        'ytick.major.width': 0.8,
        'legend.fontsize': 12.5,
        'legend.frameon': False,
        'lines.linewidth': 1.6,
        'lines.markersize': 6,
        'figure.dpi': 120,
        'savefig.dpi': 200,
        'savefig.bbox': 'tight',
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


def header_legend(ax, entries, ncol=None, legend_size=9.5):
    """Per-axes legend row between the bold left title and the plot.
    Call after set_title; finalize_headers(fig) locks the spacing."""
    handles = legend_handles(entries)
    n = ncol or len(handles)
    rows = -(-len(handles) // n)
    title = ax.get_title(loc='left')
    if title:  # rough reservation; finalize_headers measures the real pad
        ax.set_title(title, loc='left', pad=8 + rows * (legend_size + 4.5))
    return ax.legend(handles=handles, loc='lower left',
                     bbox_to_anchor=(-0.01, 1.0), ncol=n,
                     frameon=False, fontsize=legend_size,
                     handletextpad=0.3, columnspacing=0.9,
                     borderpad=0.0, borderaxespad=0.0)


def fig_header_legend(fig, entries, ncol=None, legend_size=9.5):
    """Figure-level legend row above all panels, left-aligned.
    Requires constrained_layout."""
    return fig.legend(handles=legend_handles(entries),
                      loc='outside upper left',
                      ncol=ncol or len(entries), frameon=False,
                      fontsize=legend_size, handletextpad=0.3,
                      columnspacing=0.9)


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
        title = ax.get_title(loc='left')
        if title and (level_all or ax in heights):
            ax.set_title(title, loc='left', pad=pad)
        leg = ax.get_legend()
        if leg is not None:
            ax_h = ax.get_window_extent().height * 72.0 / dpi
            leg.set_bbox_to_anchor((-0.01, 1.0 + (pad - gap) / ax_h),
                                   transform=ax.transAxes)
            if hasattr(leg, 'set_loc'):
                leg.set_loc('upper left')
            else:
                leg._loc = 2
    return pad


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
