import matplotlib.colors as mc
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import PathPatch
from matplotlib.path import Path

# Near-black ink for spines / ticks / titles (announcement-clean look).
INK = '#1a1a1a'
# Human-cohort neutrals: dark = primary human series, soft = secondary.
HUMAN_DARK = '#2b2b2b'
HUMAN_SOFT = '#8a8a8a'
# Reference-line convention: grey dashed, one dash pattern everywhere.
REF_GREY = '#828589'
REF_DASH = (0, (3, 2.2))


def _register_pagella():
    """Register TeX Gyre Pagella (Palatino clone) from a TeX Live install.
    macOS ships Palatino only as a .ttc, from which matplotlib registers just
    the regular face — bold text then SILENTLY renders regular. Pagella ships
    one .otf per face, so bold titles actually come out bold. No-op when no
    TeX Live is present (the serif stack then falls through to Palatino).
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
        # Match arxiv_template (mathpazo): Palatino body + STIX math.
        # Pagella first: it has a real bold face (see _register_pagella).
        # 'DejaVu Sans' tail-fallback handles unicode glyphs (❄ etc.) that Palatino lacks.
        'font.family': ['serif', 'DejaVu Sans'],
        'font.serif': ['TeX Gyre Pagella', 'Palatino', 'Palatino Linotype', 'Book Antiqua',
                       'Computer Modern Roman', 'Times', 'DejaVu Serif'],
        'mathtext.fontset': 'stix',
        'mathtext.rm': 'Palatino',
        'mathtext.it': 'Palatino:italic',
        'mathtext.bf': 'Palatino:bold',
        # Announcement-clean frame: L-spines only, near-black ink, no grid.
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.linewidth': 0.9,
        'axes.edgecolor': INK,
        'axes.labelcolor': INK,
        'axes.titlecolor': INK,
        'text.color': INK,
        'axes.grid': False,
        # Announcement header: every title is left-aligned bold ink, sitting
        # flush with the axes' left edge (the OpenAI-release / ICLR-deck look).
        # Titles are the ONLY bold text in a figure.
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
    """Re-assert the L-spine ink frame on axes created outside apply_style's
    reach (twinx/secondary_xaxis) or restyled by a plotting call."""
    ax.grid(False)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('left', 'bottom'):
        ax.spines[side].set_color(INK)
        ax.spines[side].set_linewidth(0.9)
    ax.tick_params(colors=INK, width=0.8, length=3.5, direction='out')


# --- Google brand colors (2015 logo, unchanged through 2026) ---
G_BLUE = '#4285F4'
G_RED = '#DB4437'
G_YELLOW = '#F4B400'
G_GREEN = '#0F9D58'
G_GREY = '#5F6368'    # Google's neutral text grey
G_PURPLE = '#AB47BC'  # Material extended (used when 5+ distinct colors needed)


def _mix(hex_color, target, amount):
    """Linear-mix hex_color toward target by `amount` ∈ [0,1]; returns hex."""
    rgb = mc.to_rgb(hex_color)
    tgt = mc.to_rgb(target)
    out = tuple(c * (1 - amount) + t * amount for c, t in zip(rgb, tgt))
    return mc.to_hex(out)


def lighten(hex_color, amount):
    return _mix(hex_color, '#ffffff', amount)


def darken(hex_color, amount):
    return _mix(hex_color, '#000000', amount)


# --- Softness tiers ---------------------------------------------------------
# Each tier is (lighten, desaturate). Lighten mixes toward white; desaturate
# mixes toward greyscale. Pick by reading context:
#   brand   logo / hero block / dashboard            (max punch)
#   medium  recognizable Google but slightly calmer
#   paper   academic figure (DEFAULT)
#   soft    slides / presentation on light bg
#   mute    supplementary material / background fills
TIERS = {
    'brand':  (0.00, 0.00),
    'medium': (0.22, 0.06),
    'paper':  (0.32, 0.10),
    'soft':   (0.42, 0.16),
    'mute':   (0.50, 0.22),
}
DEFAULT_TIER = 'paper'

# Pre-computed hex per tier (run `python style.py` to regenerate this table).
# Source of truth = TIERS dict above; this block is a grep-friendly record.
#
#  color   | brand    | medium   | paper    | soft     | mute
#  --------|----------|----------|----------|----------|----------
#  blue    | #4285f4  | #6fa1f2  | #84adf1  | #99baf0  | #a9c4ef
#  red     | #db4437  | #de6f66  | #df837b  | #e09790  | #e1a7a1
#  yellow  | #f4b400  | #f2c33f  | #f1c95b  | #efd078  | #eed58f
#  green   | #0f9d58  | #47af7d  | #61b88d  | #7ac09e  | #8fc6ab
#  purple  | #ab47bc  | #bc73c9  | #c487ce  | #cc9bd4  | #d2abd9
#  grey    | #5f6368  (neutral; not tier-shifted)


def apply_tier(base, tier=DEFAULT_TIER):
    """Soften a brand color by (lighten, desaturate) per the chosen tier."""
    lighten_amt, desat_amt = TIERS[tier]
    rgb = list(mc.to_rgb(base))
    rgb = [c + (1 - c) * lighten_amt for c in rgb]
    grey = sum(rgb) / 3
    rgb = [c * (1 - desat_amt) + grey * desat_amt for c in rgb]
    return mc.to_hex(rgb)


def paper(base):
    """Backward-compat alias: brand color at the default tier."""
    return apply_tier(base, DEFAULT_TIER)


def twotone(base, tier=DEFAULT_TIER):
    """Same-hue (dark, light) pair for a 2-series chart, OpenAI-announcement
    style: one brand hue at two lightness levels instead of two hues.
    Dark is the tier color deepened a further notch (announcement charts
    want a richer dark end than paper figures); light is a pale tint of it.
    Works for every palette color. Bars: draw the light series with
    `edgecolor=dark` so it keeps a crisp outline on white.
    """
    dark = darken(apply_tier(base, tier), 0.30)
    return dark, lighten(dark, 0.55)


def hue_ramp(base, n, tier='medium', light=0.55, dark=0.32):
    """Single-hue ordered ramp: n steps of ONE brand color from light to dark.
    This is the one-primary-color-per-figure rule — multi-series figures
    encode series identity as lightness of the figure's hue, never as a
    second hue. Index 0 = lightest, index n-1 = darkest.
    """
    anchor = apply_tier(base, tier)
    if n == 1:
        return [anchor]
    stops = [light - (light + dark) * i / (n - 1) for i in range(n)]
    return [lighten(anchor, s) if s >= 0 else darken(anchor, -s) for s in stops]


def legend_handles(entries):
    """White-edged proxy handles for the announcement legend row. `entries`
    is a list of (label, color) or (label, color, marker) tuples. marker 'o'
    (default) or any marker char gives a dot proxy; marker '--' gives a
    dashed-line proxy (for reference lines); marker '-' a solid-line proxy.
    """
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


def header_legend(ax, entries, ncol=None, legend_size=9.5, y=1.0):
    """Announcement-style legend row: white-edged dot/line proxies laid out
    horizontally, left-aligned, directly ABOVE the axes and BELOW the
    left-aligned bold title (the rc default slot). Call after set_title, and
    call finalize_headers(fig) once before savefig — it measures the real
    legend heights and locks the title/legend/plot spacing. Returns the
    legend.
    """
    handles = legend_handles(entries)
    n = ncol or len(handles)
    rows = -(-len(handles) // n)
    title = ax.get_title(loc='left')
    if title:
        # rough reservation only; finalize_headers replaces it with the
        # measured value
        ax.set_title(title, loc='left', pad=8 + rows * (legend_size + 4.5))
    return ax.legend(handles=handles, loc='lower left',
                     bbox_to_anchor=(-0.01, y), ncol=n,
                     frameon=False, fontsize=legend_size,
                     handletextpad=0.3, columnspacing=0.9,
                     borderpad=0.0, borderaxespad=0.0)


def finalize_headers(fig, gap_title=4.0, gap_axes=6.0, min_pad=8.0,
                     level_all=True):
    """Measure-and-level pass for announcement headers. Call ONCE per figure,
    after every set_title / header_legend and right before savefig.

    Draws the canvas, measures each per-axes header legend's true height in
    points, then (1) sets every left title to ONE pad — the tallest legend
    plus gap_title above it and gap_axes below it — so sibling titles sit
    level regardless of per-panel row counts, and (2) re-anchors each legend
    so its TOP edge hangs gap_title below the title. Title -> legend -> plot
    spacing is therefore constant across panels and independent of font
    sizes. Returns the applied pad (points).

    level_all=False re-pads only axes that carry a legend, leaving
    legend-less titles at their default pad — use it when legend-less panels
    sit in a DIFFERENT row from the legend-carrying ones (a figure-level
    header row carries their series identity instead).
    """
    fig.canvas.draw()
    dpi = fig.dpi
    heights = {}
    for ax in fig.axes:
        leg = ax.get_legend()
        if leg is not None:
            heights[ax] = leg.get_window_extent().height * 72.0 / dpi
    pad = max([min_pad] + [h + gap_title + gap_axes for h in heights.values()])
    for ax in fig.axes:
        title = ax.get_title(loc='left')
        if title and (level_all or ax in heights):
            ax.set_title(title, loc='left', pad=pad)
        leg = ax.get_legend()
        if leg is not None:
            ax_h = ax.get_window_extent().height * 72.0 / dpi
            y_top = 1.0 + (pad - gap_title) / ax_h
            leg.set_bbox_to_anchor((-0.01, y_top), transform=ax.transAxes)
            if hasattr(leg, 'set_loc'):
                leg.set_loc('upper left')
            else:
                leg._loc = 2
    return pad


def fig_header_legend(fig, entries, ncol=None, legend_size=9.5):
    """Figure-level announcement legend row for multi-panel figures: one
    horizontal white-edged proxy row across the top, left-aligned, above all
    panels. Requires constrained_layout (uses loc='outside upper left').
    """
    handles = legend_handles(entries)
    return fig.legend(handles=handles, loc='outside upper left',
                      ncol=ncol or len(handles), frameon=False,
                      fontsize=legend_size, handletextpad=0.3,
                      columnspacing=0.9)


def title_legend(ax, title, entries, ncol=None, title_size=12.5,
                 legend_size=9.5, y_title=1.15, y_legend=1.01):
    """Announcement-style header for a single-axes figure: left-aligned bold
    title above the axes, with the horizontal white-edged legend row between
    title and plot. Returns the legend so callers can tweak it.
    """
    ax.text(-0.01, y_title, title, transform=ax.transAxes,
            fontsize=title_size, fontweight='bold', color=INK,
            va='bottom', ha='left')
    return ax.legend(handles=legend_handles(entries), loc='lower left',
                     bbox_to_anchor=(-0.01, y_legend), ncol=ncol or len(entries),
                     frameon=False, fontsize=legend_size,
                     handletextpad=0.3, columnspacing=0.9)


def rounded_bar(ax, cx, top, w, r_frac=0.10, **kw):
    """Bar with rounded TOP corners only; the base sits square on ylim[0].
    `top` is the data value (bar apex), `w` the width in x data units,
    `r_frac` the corner radius as a fraction of bar width. The vertical
    radius is derived from the axes geometry so corners read as circular.
    Call after xlim/ylim are final.
    """
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


def family_4(base, tier=DEFAULT_TIER):
    """4-step gradient: lightest, light, mid (`apply_tier`), dark.
    The mid fill follows the active tier so flooded fills never read
    oversaturated; dark end is gentle for low-contrast readability.
    """
    return [lighten(base, 0.65), lighten(base, 0.42),
            apply_tier(base, tier), darken(base, 0.22)]


def all_tiers_table():
    """Print the precomputed hex per (color, tier). Run as `python style.py`
    to regenerate the table comment above.
    """
    cols = ['blue', 'red', 'yellow', 'green', 'purple']
    bases = [G_BLUE, G_RED, G_YELLOW, G_GREEN, G_PURPLE]
    tiers = list(TIERS.keys())
    header = ' color   | ' + ' | '.join(f'{t:8s}' for t in tiers)
    print(header)
    print(' --------|' + '|'.join(['----------'] * len(tiers)))
    for name, base in zip(cols, bases):
        cells = [apply_tier(base, t) for t in tiers]
        print(f' {name:7s} | ' + ' | '.join(f'{c:8s}' for c in cells))
    print(f' grey    | {G_GREY}  (used as-is, not tier-shifted)')


def arrow(text, direction='down'):
    arr = r'$\downarrow$' if direction == 'down' else r'$\uparrow$'
    return f'{text} {arr}'


if __name__ == '__main__':
    all_tiers_table()
