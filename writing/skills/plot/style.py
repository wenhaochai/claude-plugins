"""Chart style for posts and papers, after Epoch AI's charts: one sans face, a light grid in both
directions, only the baseline axis drawn, y values sitting just above their grid lines, the quantity
named above each column of panels, the panel's name inside it, and the Google palette.

    from style import *
    apply_style()
    fig, axes = canvas(rows=1, cols=2, title='...', legend=[('Model A', BLUE), ('Model B', LIGHT)],
                       quantity='Throughput (MB/s)')
    for ax in axes.flat:
        ax.plot(x, y, color=BLUE)
        nice_y(ax, lo, hi)             # ticks, range, and the values on their grid lines
        panel_label(ax, 'Setting A')
    save(fig, HERE / 'out')           # out.pdf + out.png, checked for text off the canvas

The layout is set in inches, top down (title, legend row, the column's quantity, the panels), so
every gap is the same in every figure. SKILL.md has the rules the helpers leave to you.
"""
import math
import warnings
from pathlib import Path

import matplotlib.colors as mc
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.transforms import ScaledTranslation

# --- Type: one face, one scale ---------------------------------------------------------------------
# Epoch AI sets its charts in Messina Sans (commercial, Luzi Type). Instrument Sans (SIL OFL, bundled
# in fonts/ as static 400 and 500 instances) was the closest of six free faces compared side by side.
FONT_DIR = Path(__file__).resolve().parent / 'fonts'
FACE = 'Instrument Sans'

#   TITLE   10.5  medium   the figure's title, wrapped at the full canvas width
#   TEXT     7.0  regular  legend row, the quantity above each column, panel names, axis names
#   TICK     6.3  regular  tick values
TITLE_PT, TEXT_PT, TICK_PT = 10.5, 7.0, 6.3

# Canvas widths, placed at 1:1: a paper's single column and full width, and a post (a 1600 px PNG).
WIDTH_1COL, WIDTH_FULL, WIDTH_POST = 5.5, 7.6, 4.4
POST_PX = 1600

# --- Ink ------------------------------------------------------------------------------------------
INK = '#1a1a1a'       # title, legend, quantity, panel names
TICK = '#4a5252'      # tick values
GRID = '#e4e6e6'      # grid lines, both directions
AXIS = '#5d6b6b'      # the baseline axis, the one spine drawn

# --- Layout, inches ---------------------------------------------------------------------------------
M_LEFT, M_RIGHT, M_TOP, M_BOTTOM = 0.14, 0.10, 0.14, 0.24
GAP_TITLE_LEGEND = 0.15      # title's last line to the legend row
GAP_LEGEND_QUANTITY = 0.13   # legend row's bottom to the top of the quantity above the top panels
GAP_QUANTITY_PANEL = 0.19    # quantity to the panel's top edge (the top value sits in between)
GAP_COLUMNS, GAP_ROWS = 0.34, 0.40
GAP_XLABEL = 0.30            # bottom panel edge to an x-axis name, when there is one
LIFT_PT = 2.2                # a value sits this far above its grid line: nothing touches the grid


def apply_style():
    """Register the bundled face and set the frame: grid both ways, baseline only, no tick marks."""
    for path in FONT_DIR.glob('InstrumentSans-*.ttf'):
        font_manager.fontManager.addfont(str(path))
    plt.rcParams.update({
        'font.family': [FACE, 'DejaVu Sans'],
        'mathtext.fontset': 'custom',
        'mathtext.rm': FACE,
        'mathtext.it': f'{FACE}:italic',
        'text.color': INK,
        'axes.labelcolor': INK,
        'axes.titlecolor': INK,
        'axes.spines.left': False,
        'axes.spines.right': False,
        'axes.spines.top': False,
        'axes.spines.bottom': True,
        'axes.edgecolor': AXIS,
        'axes.linewidth': 0.8,
        'axes.grid': True,
        'axes.grid.axis': 'both',
        'axes.axisbelow': True,
        'grid.color': GRID,
        'grid.linewidth': 0.5,
        'axes.labelsize': TEXT_PT,
        'xtick.labelsize': TICK_PT,
        'ytick.labelsize': TICK_PT,
        'xtick.color': TICK,
        'ytick.color': TICK,
        'xtick.major.size': 0,
        'ytick.major.size': 0,
        'xtick.minor.size': 0,
        'ytick.minor.size': 0,
        'xtick.major.pad': 3.5,
        'legend.frameon': False,
        'lines.linewidth': 1.4,
        'lines.solid_joinstyle': 'miter',
        'figure.dpi': 120,
        # Never tight-crop: it changes the canvas, so LaTeX rescales the figure and every font in it.
        'savefig.bbox': None,
        'figure.constrained_layout.use': False,
        'pdf.fonttype': 42,
    })


# --- Palette: Google brand colours -----------------------------------------------------------------
G_BLUE = '#4285F4'
G_RED = '#DB4437'
G_YELLOW = '#F4B400'
G_GREEN = '#0F9D58'
G_GREY = '#5F6368'    # neutral grey, used as-is
G_PURPLE = '#AB47BC'  # Material extension for a 5th distinct hue


def _mix(hex_color, target, amount):
    rgb, tgt = mc.to_rgb(hex_color), mc.to_rgb(target)
    return mc.to_hex(tuple(c * (1 - amount) + t * amount for c, t in zip(rgb, tgt)))


def lighten(hex_color, amount):
    return _mix(hex_color, '#ffffff', amount)


def darken(hex_color, amount):
    return _mix(hex_color, '#000000', amount)


# Softness tiers: (lighten, desaturate) toward white / greyscale.
TIERS = {'brand': (0.00, 0.00), 'medium': (0.22, 0.06), 'paper': (0.32, 0.10),
         'soft': (0.42, 0.16), 'mute': (0.50, 0.22)}
DEFAULT_TIER = 'paper'


def apply_tier(base, tier=DEFAULT_TIER):
    """Soften a brand colour by the tier's (lighten, desaturate) amounts."""
    lighten_amt, desat_amt = TIERS[tier]
    rgb = [c + (1 - c) * lighten_amt for c in mc.to_rgb(base)]
    grey = sum(rgb) / 3
    return mc.to_hex([c * (1 - desat_amt) + grey * desat_amt for c in rgb])


def twotone(base, tier='brand'):
    """(dark, light) pair of ONE hue for a two-series chart."""
    dark = darken(apply_tier(base, tier), 0.30)
    return dark, lighten(dark, 0.55)


def family_4(base, tier=DEFAULT_TIER):
    """Four-step ordered gradient of one hue: lightest, light, mid, dark."""
    return [lighten(base, 0.65), lighten(base, 0.42), apply_tier(base, tier), darken(base, 0.22)]


# The default three: a dark and a light blue for the two series being compared, grey for a third.
BLUE, LIGHT = twotone(G_BLUE)
GREY = lighten(G_GREY, 0.25)


# --- Canvas ------------------------------------------------------------------------------------------
def _renderer(fig):
    fig.canvas.draw()
    return fig.canvas.get_renderer()


def _wrap(fig, text, width_in, size, weight):
    """Greedy word wrap of `text` to `width_in` inches at `size`, measured with the real face."""
    r = _renderer(fig)
    probe = fig.text(0, 0, '', fontsize=size, weight=weight)
    lines, cur = [], ''
    for word in text.split():
        trial = f'{cur} {word}'.strip()
        probe.set_text(trial)
        if cur and probe.get_window_extent(r).width / fig.dpi > width_in:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    lines.append(cur)
    probe.remove()
    if len(lines) > 1 and len(lines[-1].split()) == 1:
        warnings.warn(f'title ends on a one-word line ({lines[-1]!r}): rephrase it rather than shrink it')
    return '\n'.join(lines)


def _swatch(fig, x, y, color, kind):
    """A legend swatch at (x, y) inches from the bottom left: 'line', 'dot' or 'box'. Returns its width."""
    W, H = fig.get_size_inches()
    if kind == 'line':
        fig.add_artist(Line2D([x / W, (x + 0.11) / W], [y / H] * 2, color=color, linewidth=1.8,
                              solid_capstyle='butt'))
        return 0.11
    if kind == 'box':
        fig.add_artist(Rectangle((x / W, (y - 0.035) / H), 0.07 / W, 0.07 / H, color=color,
                                 transform=fig.transFigure))
        return 0.07
    fig.add_artist(Line2D([(x + 0.035) / W], [y / H], marker='o', markersize=5, color=color,
                          linestyle='none'))
    return 0.07


def canvas(rows=1, cols=1, width=WIDTH_1COL, panel_height=1.5, title=None, legend=None,
           quantity=None, xlabel=None):
    """The figure and its panels, laid out top down in inches.

    title     the owner's wording (a draft is marked as one until confirmed), wrapped at the full
              width at TITLE_PT; a one-word last line warns, and the fix is to rephrase it.
    legend    [(name, colour), ...] or [(name, colour, 'line'|'dot'|'box'), ...]: one row under the
              title. Default kind: 'line'.
    quantity  the y quantity and unit, e.g. 'Throughput (MB/s)', written once above each column's
              top panel. Method details (statistics, transforms, workloads) go in the caption.
    xlabel    the x quantity and unit under each bottom panel, or None when the ticks speak for
              themselves.
    Returns (fig, axes) with axes a rows x cols array.
    """
    fig = plt.figure(figsize=(width, 4))
    header = M_TOP
    title_text = None
    if title:
        wrapped = _wrap(fig, title, width - M_LEFT - M_RIGHT, TITLE_PT, 'medium')
        title_text = fig.text(0, 0, wrapped, fontsize=TITLE_PT, weight='medium', color=INK,
                              ha='left', va='top', linespacing=1.15)
        header += title_text.get_window_extent(_renderer(fig)).height / fig.dpi + GAP_TITLE_LEGEND
    legend_from_top = None
    if legend:                                  # a row 0.10 in tall, its centre 0.05 in down
        legend_from_top = header + 0.05
        header += 0.10 + GAP_LEGEND_QUANTITY
    elif title:
        header += GAP_LEGEND_QUANTITY - GAP_TITLE_LEGEND
    header += (0.10 + GAP_QUANTITY_PANEL) if quantity else 0.14   # the top value sits above the top line
    bottom = M_BOTTOM + (GAP_XLABEL if xlabel else 0)
    W, H = width, header + rows * panel_height + (rows - 1) * GAP_ROWS + bottom
    fig.set_size_inches(W, H)
    pw = (W - M_LEFT - M_RIGHT - (cols - 1) * GAP_COLUMNS) / cols
    axes = np.empty((rows, cols), dtype=object)
    for r in range(rows):
        for c in range(cols):
            x0 = M_LEFT + c * (pw + GAP_COLUMNS)
            y0 = bottom + (rows - 1 - r) * (panel_height + GAP_ROWS)
            axes[r, c] = fig.add_axes([x0 / W, y0 / H, pw / W, panel_height / H])
    if title_text is not None:
        title_text.set_position((M_LEFT / W, 1 - M_TOP / H))
    if legend:
        x, y = M_LEFT, H - legend_from_top
        rend = _renderer(fig)
        for entry in legend:
            name, color, kind = entry if len(entry) == 3 else (*entry, 'line')
            x += _swatch(fig, x, y, color, kind) + 0.06
            t = fig.text(x / W, y / H, name, fontsize=TEXT_PT, color=INK, ha='left', va='center')
            x += t.get_window_extent(rend).width / fig.dpi + 0.20
    for c in range(cols):
        if quantity:
            axes[0, c].text(0.0, 1 + GAP_QUANTITY_PANEL / panel_height, quantity,
                            transform=axes[0, c].transAxes, ha='left', va='bottom', fontsize=TEXT_PT,
                            color=INK)
        if xlabel:
            axes[-1, c].set_xlabel(xlabel, fontsize=TEXT_PT, color=INK, labelpad=6)
    return fig, axes


# --- Per panel -------------------------------------------------------------------------------------
_STEPS = (1, 1.5, 2, 2.5, 3, 5)          # x 10^k; Epoch's own axes step by 300
MIN_BAND_IN = 0.24                     # the top band holds the panel's name above the next value


def nice_y(ax, lo, hi, zero=False, headroom=0.3, fmt='{:,.0f}'):
    """Set the y range and draw the values on their grid lines.

    The range starts at 0 only when `zero` (0 is part of the comparison); otherwise at a round value
    just below `lo`. The top leaves `headroom` x the data span free for the panel's name. Of the round
    steps (1, 1.5, 2, 2.5, 3, 5 x 10^k) giving 3 or more bands each at least MIN_BAND_IN tall, the one
    with the tightest range wins, fewer bands breaking ties. Returns the ticks."""
    fig = ax.figure
    height_in = ax.get_position().height * fig.get_size_inches()[1]
    max_bands = max(3, int(height_in / MIN_BAND_IN))
    span = max(hi - (0 if zero else lo), 1e-12)
    need = hi + headroom * span
    low = 0.0 if zero else lo - 0.08 * span
    best = None
    mag = 10 ** math.floor(math.log10(span))
    for m in (mag / 100, mag / 10, mag, mag * 10):
        for s in _STEPS:
            step = s * m
            b, t = math.floor(low / step) * step, math.ceil(need / step) * step
            bands = round((t - b) / step)
            if 3 <= bands <= max_bands and (best is None or (t - b, bands) < (best[1] - best[0], best[3])):
                best = (b, t, step, bands)
    if best is None:
        raise ValueError('no round step found')
    b, t, step, _ = best
    ticks = [round(v, 10) for v in np.arange(b, t + step / 2, step)]
    ax.set_ylim(ticks[0], ticks[-1])
    y_values(ax, ticks, fmt)
    return ticks


def y_values(ax, ticks, fmt='{:,.0f}'):
    """Each value just above its grid line, at the panel's left edge (the default labels go)."""
    ax.set_yticks(ticks)
    ax.tick_params(axis='y', labelleft=False)
    lift = ScaledTranslation(0, LIFT_PT / 72, ax.figure.dpi_scale_trans)
    for t in ticks:
        ax.text(0.0, t, fmt.format(t), transform=ax.get_yaxis_transform() + lift, ha='left',
                va='bottom', fontsize=TICK_PT, color=TICK)


def room(ax, left=0.14, right=0.04):
    """Widen a linear x range: `left` of it for the y values, `right` past the last grid line."""
    a, b = ax.get_xlim()
    span = b - a
    ax.set_xlim(a - left * span, b + right * span)


def panel_label(ax, text, x=None):
    """The panel's name inside it, top left, on a white ground the grid stops at. `x` in data units
    (default: the first x tick inside the range), nudged right of that grid line."""
    lo, hi = ax.get_xlim()
    if x is None:
        inside = [t for t in ax.get_xticks() if lo <= t <= hi]
        x = inside[0] if inside else lo
    xa = ax.transAxes.inverted().transform(ax.transData.transform((x, 0)))[0] + 0.025
    height_in = ax.get_position().height * ax.figure.get_size_inches()[1]
    ax.text(xa, 1 - 0.05 / height_in, text, transform=ax.transAxes, ha='left', va='top', fontsize=TEXT_PT,
            color=INK, zorder=4, bbox=dict(facecolor='white', edgecolor='none', pad=1.6))


# --- Output ------------------------------------------------------------------------------------------
def check(fig):
    """Raise if any text runs off the canvas."""
    r = _renderer(fig)
    box = fig.bbox
    for t in fig.findobj(lambda a: hasattr(a, 'get_text') and hasattr(a, 'get_window_extent')):
        if not t.get_visible() or not t.get_text():
            continue
        e = t.get_window_extent(r)
        if e.x0 < box.x0 - 0.5 or e.x1 > box.x1 + 0.5 or e.y0 < box.y0 - 0.5 or e.y1 > box.y1 + 0.5:
            raise ValueError(f'text off the canvas: {t.get_text()!r}')


def save(fig, stem, png_px=POST_PX):
    """stem.pdf (the paper's artifact) and stem.png, `png_px` wide (a post's artifact), after check()."""
    check(fig)
    stem = Path(stem)
    fig.savefig(stem.with_suffix('.pdf'))
    fig.savefig(stem.with_suffix('.png'), dpi=png_px / fig.get_size_inches()[0])


__all__ = ['apply_style', 'canvas', 'nice_y', 'y_values', 'room', 'panel_label', 'check', 'save',
           'lighten', 'darken', 'apply_tier', 'twotone', 'family_4', 'BLUE', 'LIGHT', 'GREY',
           'G_BLUE', 'G_RED', 'G_YELLOW', 'G_GREEN', 'G_GREY', 'G_PURPLE', 'INK', 'TICK', 'GRID',
           'AXIS', 'TITLE_PT', 'TEXT_PT', 'TICK_PT', 'WIDTH_1COL', 'WIDTH_FULL', 'WIDTH_POST']
