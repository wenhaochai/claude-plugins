"""Chart style for posts and papers, after Epoch AI's charts: one sans face, a light grid in both
directions, only the baseline axis drawn, y values sitting just above their grid lines, the quantity
named above each column of panels, the panel's name inside it, and Google's GM2 tones.

    from style import *
    apply_style()
    fig, axes = canvas(rows=1, cols=2, title='...', legend=[('Model A', BLUE), ('Model B', LIGHT)],
                       quantity='Throughput (MB/s)')
    for ax in axes.flat:
        ax.plot(x, y, color=BLUE)
        nice_y(ax, lo, hi)             # ticks, range, and the values on their grid lines
        panel_label(ax, 'Setting A')
    save(fig, HERE / 'out')           # out.pdf + out.png, fitted and checked for text off the canvas

The layout is set in inches, top down (title, subtitle, legend row, the column's quantity, the panels,
the x-axis name, a footnote), so every gap is the same in every figure. Epoch's exported charts use a
second tick style, ticks='left': tick values left of the panel with short tick marks, the quantity
starting at the left margin. SKILL.md has the rules the helpers leave to you.
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

# --- Type: one face, four sizes ---------------------------------------------------------------------
# Epoch AI sets its charts in Messina Sans (commercial, Luzi Type). Instrument Sans (SIL OFL, bundled
# in fonts/ as static 400, 500, 600 and italic 400 instances) was the closest of six free faces compared.
FONT_DIR = Path(__file__).resolve().parent / 'fonts'
FACE = 'Instrument Sans'

# Sizes match Epoch's 2400 px exports scaled to WIDTH_TEXT, the width they were measured at. Words match on
# the lowercase (x-height and width): at equal capitals Instrument Sans's lowercase runs about 5% smaller
# than Messina Sans's. The title splits x-height (12.4) and width (12.0), so it breaks where Epoch's
# does. Tick values, mostly digits, which run wider in Instrument Sans, match on the capitals. Weight,
# not size, tells the roles apart below the title.
#   TITLE   12.2  semibold the figure's title, wrapped between the side margins
#   SUB      9.3  regular  a subtitle under the title, muted
#   TEXT     7.35 medium   the quantity above each column, panel names, axis names
#            7.35 regular  the legend, callouts, footnotes
#   TICK     7    regular  tick values, point labels
TITLE_PT, SUB_PT, TEXT_PT, TICK_PT = 12.2, 9.3, 7.35, 7.0

# Canvas widths, placed at 1:1: a 5.5 in text width (NeurIPS, ICML, ICLR), a one-column paper with
# narrower margins (6.32 in, 457 pt), a full two-column spread, and a post (a 1600 px PNG).
WIDTH_1COL, WIDTH_TEXT, WIDTH_FULL, WIDTH_POST = 5.5, 6.32, 7.6, 4.4
POST_PX = 1600

# --- Colour: Google's GM2 tones, nothing computed ---------------------------------------------------
# Every colour in a chart is one of these, grades 50 to 900.
GRADES = (50, 100, 200, 300, 400, 500, 600, 700, 800, 900)
GM2 = {
    'blue': ['#E8F0FE', '#D2E3FC', '#AECBFA', '#8AB4F8', '#669DF6', '#4285F4', '#1A73E8', '#1967D2', '#185ABC',
             '#174EA6'],
    'red': ['#FCE8E6', '#FAD2CF', '#F6AEA9', '#F28B82', '#EE675C', '#EA4335', '#D93025', '#C5221F', '#B31412',
            '#A50E0E'],
    'yellow': ['#FEF7E0', '#FEEFC3', '#FDE293', '#FDD663', '#FCC934', '#FBBC04', '#F9AB00', '#F29900', '#EA8600',
               '#E37400'],
    'green': ['#E6F4EA', '#CEEAD6', '#A8DAB5', '#81C995', '#5BB974', '#34A853', '#1E8E3E', '#188038', '#137333',
              '#0D652D'],
    'purple': ['#F3E8FD', '#E9D2FD', '#D7AEFB', '#C58AF9', '#AF5CF7', '#A142F4', '#9334E6', '#8430CE', '#7627BB',
               '#681DA8'],
    'grey': ['#F8F9FA', '#F1F3F4', '#E8EAED', '#DADCE0', '#BDC1C6', '#9AA0A6', '#80868B', '#5F6368', '#3C4043',
             '#202124'],
}


def tone(hue, grade):
    """Google's GM2 tone of `hue` at `grade` (50 to 900)."""
    return GM2[hue][GRADES.index(grade)]


GREY_50, GREY_100, GREY_200, GREY_300, GREY_400, GREY_500, GREY_600, GREY_700, GREY_800, GREY_900 = GM2['grey']
INK = GREY_900        # title, legend, quantity, panel names
TICK = GREY_800       # tick values, point labels
MUTED = GREY_700      # subtitle, footnote, second lines of category names
GRID = GREY_200       # grid lines, both directions
AXIS = GREY_700       # the baseline axis, the one spine drawn
MARK = GREY_500       # tick marks (ticks='left'), frames, leader lines

# --- Layout, inches (measured off Epoch AI's 2400 px exports scaled to WIDTH_TEXT) -----------------
M_SIDE, M_TOP, M_BOTTOM = 0.19, 0.19, 0.24   # Epoch's exports keep 0.19 in clear on three sides
TITLE_LINESPACING = 1.37     # a wrapped title's baselines 0.21 in apart
GAP_SUBTITLE = 0.13          # title's last line to the subtitle
GAP_TITLE_LEGEND = 0.235     # title (or subtitle) to the top of the legend row or the quantity
LEGEND_H = 0.10              # the legend row
GAP_LEGEND_QUANTITY = 0.16   # legend row's bottom to the top of the quantity
QUANTITY_H = 0.10            # the quantity above each column
GAP_QUANTITY_PANEL = 0.24    # quantity's bottom to the panel's top grid line; the top value sits between
GAP_QUANTITY_LEFT = 0.125    # the same with ticks='left': quantity to the top of the plot
GAP_COLUMNS, GAP_ROWS = 0.16, 0.44
GAP_XLABEL = 0.28            # bottom panel edge to an x-axis name, when there is one
GAP_NOTE = 0.23              # the lowest axis text (x values or the x-axis name) to a footnote
TICKS_BELOW, XLABEL_BELOW = 0.15, 0.18   # what x values and an x-axis name take under a panel
M_EDGE = 0.13                # a footnote's last line to the canvas bottom
SWATCH, SWATCH_GAP, ITEM_GAP = 0.09, 0.035, 0.16   # legend: swatch, swatch to name, name to next swatch
BOX = 0.07                   # a square legend swatch
GAP_LEGEND_COLUMN = 0.16     # panels' right edge to a legend column
COLUMN_PITCH = 0.155         # a legend column's row pitch
LIFT_PT = 2.4                # a value sits this far above its grid line: nothing touches the grid
MARK_PT = 2.5                # tick-mark length with ticks='left'


def apply_style():
    """Register the bundled face and set the frame: grid both ways, baseline only, no tick marks."""
    for path in FONT_DIR.glob('InstrumentSans-*.ttf'):
        font_manager.fontManager.addfont(str(path))
    plt.rcParams.update({
        'font.family': [FACE, 'DejaVu Sans'],
        'mathtext.fontset': 'custom',
        'mathtext.rm': FACE,
        'mathtext.it': f'{FACE}:italic',
        'mathtext.bf': f'{FACE}:semibold',    # $\mathbf{10^{23}}$ inside a semibold title
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


# --- Palette ---------------------------------------------------------------------------------------
# Distinct categories take the hues in this order, toned by the size of the mark as FiveThirtyEight and
# Datawrapper do: the larger the inked area, the lighter the tone (Muth,
# datawrapper.de/blog/colors-for-data-vis-style-guides). Small marks need 3:1 against white (WCAG, IBM
# Carbon) and words 4:1 (Datawrapper). No Google yellow below 900 reaches 3:1, so yellow lines and words
# take yellow 900 (3.1:1); in the fills every hue takes the same grade.
ORDER = ('blue', 'red', 'yellow', 'green', 'purple')
STRONG = [tone(h, 900 if h == 'yellow' else 600) for h in ORDER]   # lines, points, small marks
MEDIUM = [tone(h, 400) for h in ORDER]                             # bars and columns
SOFT = [tone(h, 300) for h in ORDER]                               # stacked areas, treemap cells
WORDS = [tone(h, 900 if h == 'yellow' else 700) for h in ORDER]    # text set in a series' colour
# Context (the cloud behind a highlighted series) steps down a set, or goes grey, so the highlight
# reads first (Datawrapper, "Emphasize with color"). Stacked neighbours are split by thin white edges.

# A compared pair: one hue, a strong and a soft tone. A third series: grey.
BLUE, LIGHT = tone('blue', 600), tone('blue', 300)
GREY = GREY_600
BLUE_RAMP = GM2['blue']   # a sequential scale, light to dark


def family_4(hue='blue'):
    """Four ordered steps of one hue, light to dark (grades 300, 500, 700, 900)."""
    return [tone(hue, g) for g in (300, 500, 700, 900)]


# --- Canvas ------------------------------------------------------------------------------------------
def _renderer(fig):
    fig.canvas.draw()
    return fig.canvas.get_renderer()


def _wrap(fig, text, width_in, size, weight, style='normal', warn=True):
    """Greedy word wrap of `text` to `width_in` inches at `size`, measured with the real face. Existing
    line breaks are kept."""
    r = _renderer(fig)
    probe = fig.text(0, 0, '', fontsize=size, weight=weight, style=style)
    lines = []
    for para in text.split('\n'):
        cur = ''
        for word in para.split():
            trial = f'{cur} {word}'.strip()
            probe.set_text(trial)
            if cur and probe.get_window_extent(r).width / fig.dpi > width_in:
                lines.append(cur)
                cur = word
            else:
                cur = trial
        lines.append(cur)
    probe.remove()
    if warn and len(lines) > 1 and len(lines[-1].split()) == 1:
        warnings.warn(f'{text[:40]!r}... ends on a one-word line ({lines[-1]!r}): rephrase it rather than shrink it')
    return '\n'.join(lines)


def _height(fig, t):
    return t.get_window_extent(_renderer(fig)).height / fig.dpi


def _width(fig, text, size, weight='normal'):
    probe = fig.text(0, 0, text, fontsize=size, weight=weight)
    w = probe.get_window_extent(_renderer(fig)).width / fig.dpi
    probe.remove()
    return w


def _swatch(fig, x, y, color, kind):
    """A legend swatch at (x, y) inches from the bottom left: 'line', 'dash', 'dot', 'ring' (Epoch's
    translucent marker), 'box' or 'ci' (a capped whisker). Returns its width."""
    W, H = fig.get_size_inches()
    if kind in ('line', 'dash'):
        fig.add_artist(Line2D([x / W, (x + SWATCH) / W], [y / H] * 2, color=color, linewidth=2.0,
                              solid_capstyle='butt', dashes=(2.2, 1.4) if kind == 'dash' else (None, None)))
        return SWATCH
    if kind == 'box':
        fig.add_artist(Rectangle((x / W, (y - BOX / 2) / H), BOX / W, BOX / H, color=color,
                                 transform=fig.transFigure))
        return BOX
    if kind == 'ci':
        w, c = 0.16, 0.035
        for xs, ys in (([x, x + w], [y, y]), ([x, x], [y - c, y + c]), ([x + w, x + w], [y - c, y + c])):
            fig.add_artist(Line2D([v / W for v in xs], [v / H for v in ys], color=color, linewidth=0.9))
        return w
    ring = kind == 'ring'
    fig.add_artist(Line2D([(x + BOX / 2) / W], [y / H], marker='o', markersize=4.6, linestyle='none', color=color,
                          markerfacecolor=mc.to_rgba(color, 0.55) if ring else color,
                          markeredgecolor=color,
                          markeredgewidth=0.6 if ring else 0))
    return BOX


def _legend_items(legend):
    for entry in legend:
        name, color, kind = entry if len(entry) == 3 else (*entry, 'line')
        yield name, color, kind


def _legend_row(fig, legend, x, y, align='left'):
    """One legend row centred on height y (inches), starting at x ('left') or ending at x ('right')."""
    W, H = fig.get_size_inches()
    items = list(_legend_items(legend))
    if align == 'right':
        widths = [_width(fig, n, TEXT_PT) for n, _, _ in items]
        sw = {'line': SWATCH, 'dash': SWATCH, 'ci': 0.16}
        total = sum(sw.get(k, BOX) + SWATCH_GAP + w for (_, _, k), w in zip(items, widths))
        x -= total + ITEM_GAP * (len(items) - 1)
    rend = _renderer(fig)
    for name, color, kind in items:
        x += _swatch(fig, x, y, color, kind) + SWATCH_GAP
        t = fig.text(x / W, y / H, name, fontsize=TEXT_PT, color=INK, ha='left', va='center')
        x += t.get_window_extent(rend).width / fig.dpi + ITEM_GAP


def canvas(rows=1, cols=1, width=WIDTH_TEXT, panel_height=1.5, title=None, subtitle=None,
           legend=None, legend_loc='row', legend_title=None, quantity=None, xlabel=None, note=None,
           note_style='normal', ticks='above', extra=(0, 0, 0, 0), gap_rows=GAP_ROWS, title_pt=TITLE_PT,
           subtitle_pt=SUB_PT, tick_pt=TICK_PT, note_pt=TEXT_PT, side=M_SIDE):
    """The figure and its panels, laid out top down in inches.

    title       the owner's wording (a draft is marked as one until confirmed), wrapped between the
                side margins; a one-word last line warns, and the fix is to rephrase it.
    subtitle    a muted line under the title (what the numbers are, when the title makes a claim).
    legend      [(name, colour), ...] or [(name, colour, kind), ...], kind one of 'line' (default),
                'dash', 'dot', 'ring', 'box', 'ci'.
    legend_loc  'row' a row under the title, left aligned; 'right' the same row, right aligned;
                'inline' right aligned on the quantity's row; 'column' a column right of the panels,
                headed by `legend_title` (medium; break it with '\\n').
    quantity    the y quantity and unit, e.g. 'Throughput (MB/s)', written once above each column's
                top panel. Method details (statistics, transforms, workloads) go in the caption.
    xlabel      the x quantity and unit under each bottom panel, or None when the ticks speak for
                themselves.
    note        a footnote under everything, muted, wrapped like the title ('italic' note_style).
    ticks       'above': values sit on their grid lines inside the panel (nice_y / y_values);
                'left': Epoch's export style, values left of the panel with short tick marks.
    extra       (top, right, bottom, left) inches kept free around the panels, for text the panels
                carry outside themselves (rotated names, labels above the top grid line). Labels
                left and right of the panels are fitted automatically at save(). A negative top
                brings the quantity closer, for panels without y values.
    gap_rows    inches between rows of panels; less when upper rows carry no x values.
    title_pt    the title's size; Epoch's narrower web charts set it smaller against the text (about
                9.2 pt at WIDTH_POST, measured by where the first line breaks).
    subtitle_pt the subtitle's size; Epoch sets a short methods line at TEXT_PT.
    tick_pt     the tick values' size; Epoch's web charts set them at TEXT_PT.
    note_pt     the footnote's size; Epoch's web charts set it at TICK_PT.
    side        inches kept clear left and right of all text; Epoch's web charts run nearly to the
                edge (0.10).
    Returns (fig, axes) with axes a rows x cols array.
    """
    fig = plt.figure(figsize=(width, 4))
    full = width - 2 * side
    header, texts = M_TOP, []

    def block(text, size, weight, color, style='normal', gap=0.0, warn=True, linespacing=1.2):
        nonlocal header
        t = fig.text(0, 0, _wrap(fig, text, full, size, weight, style, warn), fontsize=size, weight=weight,
                     color=color, style=style, ha='left', va='top', linespacing=linespacing)
        header += gap
        texts.append((t, header))
        header += _height(fig, t)

    if title:
        block(title, title_pt, 'semibold', INK, linespacing=TITLE_LINESPACING)
    if subtitle:
        block(subtitle, subtitle_pt, 'normal', MUTED, gap=GAP_SUBTITLE if title else 0, warn=False)
    if title or subtitle:
        header += GAP_TITLE_LEGEND
    if legend_loc == 'inline' and not quantity:
        legend_loc = 'right'
    legend_from_top = None
    if legend and legend_loc in ('row', 'right'):
        legend_from_top = header + LEGEND_H / 2
        header += LEGEND_H + GAP_LEGEND_QUANTITY
    quantity_from_top = header if quantity else None
    if quantity:
        header += QUANTITY_H + (GAP_QUANTITY_PANEL if ticks == 'above' else GAP_QUANTITY_LEFT)
    else:
        header += 0.14 if ticks == 'above' else 0.08
    header += extra[0]

    bottom = M_BOTTOM + (GAP_XLABEL if xlabel else 0) + extra[2]
    note_text = None
    if note:
        note_text = fig.text(0, 0, _wrap(fig, note, full, note_pt, 'normal', note_style, warn=False),
                             fontsize=note_pt, color=MUTED, style=note_style, ha='left', va='bottom',
                             linespacing=1.35)
        bottom = (TICKS_BELOW + (XLABEL_BELOW if xlabel else 0) + extra[2] + GAP_NOTE
                  + _height(fig, note_text) + M_EDGE)

    right_edge = width - side - extra[1]
    column_w = 0.0
    if legend and legend_loc == 'column':
        names = [n for n, _, _ in _legend_items(legend)]
        column_w = max(BOX + SWATCH_GAP + max(_width(fig, n, TEXT_PT) for n in names),
                       max((_width(fig, l, TEXT_PT, 'medium') for l in (legend_title or '').split('\n')),
                           default=0.0))
        right_edge -= column_w + GAP_LEGEND_COLUMN

    W, H = width, header + rows * panel_height + (rows - 1) * gap_rows + bottom
    fig.set_size_inches(W, H)
    left_edge = side + extra[3]
    pw = (right_edge - left_edge - (cols - 1) * GAP_COLUMNS) / cols
    axes = np.empty((rows, cols), dtype=object)
    for r in range(rows):
        for c in range(cols):
            x0 = left_edge + c * (pw + GAP_COLUMNS)
            y0 = bottom + (rows - 1 - r) * (panel_height + gap_rows)
            ax = fig.add_axes([x0 / W, y0 / H, pw / W, panel_height / H])
            ax._style_ticks, ax._style_tick_pt = ticks, tick_pt
            ax.tick_params(labelsize=tick_pt)
            if ticks == 'left':
                ax.tick_params(axis='both', length=MARK_PT, width=0.6, color=MARK, pad=2.5)
            axes[r, c] = ax
    for t, top in texts:
        t.set_position((side / W, 1 - top / H))
    if note_text is not None:
        note_text.set_position((side / W, M_EDGE / H))

    panel_top = H - header + extra[0]
    if legend and legend_loc in ('row', 'right'):
        y = H - legend_from_top
        _legend_row(fig, legend, side if legend_loc == 'row' else W - side, y, legend_loc)
    elif legend and legend_loc == 'inline':
        _legend_row(fig, legend, W - side, H - quantity_from_top - QUANTITY_H / 2, 'right')
    elif legend and legend_loc == 'column':
        x, y = W - side - column_w, panel_top - 0.02
        if legend_title:
            t = fig.text(x / W, y / H, legend_title, fontsize=TEXT_PT, weight='medium', color=INK, ha='left',
                         va='top', linespacing=1.2)
            y -= _height(fig, t) + 0.10
        else:
            y -= 0.06
        for name, color, kind in _legend_items(legend):
            fig.text((x + BOX + SWATCH_GAP) / W, y / H, name, fontsize=TEXT_PT, color=INK, ha='left',
                     va='center')
            _swatch(fig, x, y, color, kind)
            y -= COLUMN_PITCH

    quantities = []
    for c in range(cols):
        if quantity:
            if ticks == 'above':
                quantities.append(axes[0, c].text(0.0, 1 + (GAP_QUANTITY_PANEL + extra[0]) / panel_height,
                                                  quantity, transform=axes[0, c].transAxes, ha='left',
                                                  va='bottom', fontsize=TEXT_PT, weight='medium', color=INK))
            else:
                quantities.append(fig.text(0, (H - quantity_from_top - QUANTITY_H) / H, quantity, ha='left',
                                           va='bottom', fontsize=TEXT_PT, weight='medium', color=INK))
        if xlabel:
            axes[-1, c].set_xlabel(xlabel, fontsize=TEXT_PT, weight='medium', color=INK, labelpad=6)
    fig._style = dict(axes=axes, block=(left_edge, right_edge), ticks=ticks, quantities=quantities)
    return fig, axes


# --- Per panel -------------------------------------------------------------------------------------
_STEPS = (1, 1.5, 2, 2.5, 3, 5)          # x 10^k; Epoch's own axes step by 300
MIN_BAND_IN = 0.30                     # the top band holds the panel's name above the next value


def _formatter(fmt):
    return fmt if callable(fmt) else fmt.format


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
    """The y values: each just above its grid line at the panel's left edge (ticks='above'), or left
    of the panel against a short tick mark (ticks='left'). `fmt` is a format string or a callable."""
    f = _formatter(fmt)
    ax.set_yticks(ticks)
    if getattr(ax, '_style_ticks', 'above') == 'left':
        ax.set_yticklabels([f(t) for t in ticks])
        return
    ax.tick_params(axis='y', labelleft=False)
    lift = ScaledTranslation(0, LIFT_PT / 72, ax.figure.dpi_scale_trans)
    ax._style_values = [ax.text(0.0, t, f(t), transform=ax.get_yaxis_transform() + lift,
                                ha='left', va='bottom', fontsize=getattr(ax, '_style_tick_pt', TICK_PT), color=TICK)
                        for t in ticks]


def room(ax, right_in=0.12, gap_in=0.08):
    """Widen a linear x range so the data start `gap_in` past the widest y value (call after nice_y)
    and run `right_in` past the last grid line. Other scales set their x range by hand."""
    fig = ax.figure
    width_in = ax.get_position().width * fig.get_size_inches()[0]
    r = _renderer(fig)
    values_in = max((t.get_window_extent(r).width / fig.dpi for t in getattr(ax, '_style_values', [])),
                    default=0.0)
    f_left, f_right = (values_in + gap_in) / width_in, right_in / width_in
    a, b = ax.get_xlim()
    total = (b - a) / (1 - f_left - f_right)
    ax.set_xlim(a - f_left * total, b + f_right * total)


def panel_label(ax, text, x=None):
    """The panel's name inside it, top left, on a white ground the grid stops at. `x` in data units
    (default: the first x tick inside the range), nudged right of that grid line."""
    lo, hi = ax.get_xlim()
    if x is None:
        inside = [t for t in ax.get_xticks() if lo <= t <= hi]
        x = inside[0] if inside else lo
    xa = ax.transAxes.inverted().transform(ax.transData.transform((x, 0)))[0] + 0.025
    height_in = ax.get_position().height * ax.figure.get_size_inches()[1]
    ax.text(xa, 1 - 0.035 / height_in, text, transform=ax.transAxes, ha='left', va='top', fontsize=TEXT_PT,
            weight='medium', color=INK, zorder=4, bbox=dict(facecolor='white', edgecolor='none', pad=1.6))


# --- Marks and words on the data -------------------------------------------------------------------
def dots(ax, x, y, color, size=18, alpha=0.5, **kw):
    """Epoch's scatter marker: a translucent fill inside a solid edge of the same hue."""
    kw.setdefault('zorder', 3)
    return ax.scatter(x, y, s=size, facecolor=mc.to_rgba(color, alpha), edgecolor=color,
                      linewidth=0.6, **kw)


def stack(ax, xy, lines, styles=None, ha='left', va='center', size=TEXT_PT, color=INK, **kw):
    """Several lines set as one block, each with its own weight or colour ({'weight': 'medium'},
    {'color': MUTED}). Line i is drawn as the whole block with the other lines blanked, so the lines
    sit exactly where one multi-line text would put them."""
    out = []
    for i, line in enumerate(lines):
        st = dict(color=color)
        st.update((styles or [{}] * len(lines))[i] or {})
        block = '\n'.join(l if j == i else ' ' for j, l in enumerate(lines))
        out.append(ax.text(*xy, block, ha=ha, va=va, multialignment=ha, fontsize=size, linespacing=1.25,
                           **st, **kw))
    return out


def callout(ax, xy, target, lines, color=INK, ha='left', va='center', rad=0.3, relpos=(0.5, 0.5),
            styles=None, size=TEXT_PT, arrow_color=None):
    """A note at `xy` with a curved arrow to `target` (both data coordinates): the first line medium,
    the rest regular unless `styles` says otherwise. The arrow leaves the text's box at its edge."""
    lines = [lines] if isinstance(lines, str) else list(lines)
    styles = styles or [{'weight': 'medium'}] + [{}] * (len(lines) - 1)
    ax.annotate('\n'.join(lines), xy=target, xytext=xy, ha=ha, va=va, multialignment=ha, fontsize=size,
                linespacing=1.25, color='none', weight='medium', zorder=5,
                arrowprops=dict(arrowstyle='-|>,head_length=0.32,head_width=0.16',
                                connectionstyle=f'arc3,rad={rad}', color=arrow_color or color,
                                linewidth=0.8, shrinkA=2, shrinkB=2.5, relpos=relpos, mutation_scale=10))
    return stack(ax, xy, lines, styles, ha=ha, va=va, size=size, color=color, zorder=5)


def end_labels(ax, items, x=None, pad_pt=10, gap_in=0.14, size=TEXT_PT):
    """Name lines at their right ends instead of a legend. items: [(y_end, name, colour)]. Labels
    are spread to at least `gap_in` apart, each tied to its line's end by a short grey leader.
    Set the y range first."""
    fig = ax.figure
    x = ax.get_xlim()[1] if x is None else x
    ys = [ax.transData.transform((x, y))[1] / fig.dpi for y, _, _ in items]
    order = sorted(range(len(items)), key=lambda i: ys[i])
    placed = [ys[i] for i in order]
    for _ in range(200):
        moved = False
        for k in range(1, len(placed)):
            short = gap_in - (placed[k] - placed[k - 1])
            if short > 1e-6:
                placed[k] += short / 2
                placed[k - 1] -= short / 2
                moved = True
        if not moved:
            break
    for k, i in enumerate(order):
        y, name, color = items[i]
        ax.annotate(name, xy=(x, y), xytext=(pad_pt, (placed[k] - ys[i]) * 72), textcoords='offset points',
                    ha='left', va='center', fontsize=size, color=color, annotation_clip=False,
                    arrowprops=dict(arrowstyle='-', color=MARK, linewidth=0.6, shrinkA=1, shrinkB=1.5))


# --- Output ------------------------------------------------------------------------------------------
def _outside(ax, r):
    """Visible text an axes carries: tick values, its axis names, its own texts and annotations."""
    items = []
    if ax.axison:
        items += [t for t in ax.get_yticklabels() + ax.get_xticklabels() if t.get_visible() and t.get_text()]
        items += [ax.yaxis.label] if ax.yaxis.label.get_text() else []
    items += [t for t in ax.texts if t.get_visible() and t.get_text().strip()
              and mc.to_rgba(t.get_color())[3] > 0]
    return [t.get_window_extent(r) for t in items]


def fit(fig):
    """Move the panels sideways so the labels they carry outside themselves fit the canvas: tick values
    with ticks='left', category names, end labels. Each column is shifted right by its widest label on
    the left, and the last column narrowed by the widest one on the right, so the leftmost text starts
    at the left margin. Called by save(); call it yourself before adding axes placed off the panels."""
    st = getattr(fig, '_style', None)
    if st is None:
        return
    axes, (left, right) = st['axes'], st['block']
    rows, cols = axes.shape
    W = fig.get_size_inches()[0]
    for _ in range(2):
        r = _renderer(fig)
        L = []
        for c in range(cols):
            need = 0.0
            for ax in axes[:, c]:
                x0 = ax.get_window_extent(r).x0
                need = max([need] + [(x0 - e.x0) / fig.dpi for e in _outside(ax, r)])
            L.append(need)
        R = 0.0
        for ax in axes[:, -1]:
            x1 = ax.get_window_extent(r).x1
            R = max([R] + [(e.x1 - x1) / fig.dpi for e in _outside(ax, r)])
        pw = (right - left - sum(L) - R - (cols - 1) * GAP_COLUMNS) / cols
        x = left
        for c in range(cols):
            x += L[c]
            for ax in axes[:, c]:
                p = ax.get_position()
                ax.set_position([x / W, p.y0, pw / W, p.height])
            for q in st['quantities'][c:c + 1]:
                if st['ticks'] == 'left':
                    q.set_x((x - L[c]) / W)
            x += pw + GAP_COLUMNS


def check(fig):
    """Raise if any text runs off the canvas."""
    r = _renderer(fig)
    box = fig.bbox
    for t in fig.findobj(lambda a: hasattr(a, 'get_text') and hasattr(a, 'get_window_extent')):
        if not t.get_visible() or not t.get_text().strip():
            continue
        e = t.get_window_extent(r)
        if e.x0 < box.x0 - 0.5 or e.x1 > box.x1 + 0.5 or e.y0 < box.y0 - 0.5 or e.y1 > box.y1 + 0.5:
            raise ValueError(f'text off the canvas: {t.get_text()!r}')


def save(fig, stem, png_px=POST_PX):
    """stem.pdf (the paper's artifact) and stem.png, `png_px` wide (a post's artifact), after fit() and
    check()."""
    fit(fig)
    check(fig)
    stem = Path(stem)
    fig.savefig(stem.with_suffix('.pdf'))
    fig.savefig(stem.with_suffix('.png'), dpi=png_px / fig.get_size_inches()[0])


__all__ = ['apply_style', 'canvas', 'nice_y', 'y_values', 'room', 'panel_label', 'dots', 'stack', 'callout',
           'end_labels', 'fit', 'check', 'save', 'tone', 'family_4', 'GM2', 'GRADES', 'ORDER', 'STRONG',
           'MEDIUM', 'SOFT', 'WORDS', 'BLUE', 'LIGHT', 'GREY', 'BLUE_RAMP', 'GREY_50', 'GREY_100', 'GREY_200',
           'GREY_300', 'GREY_400', 'GREY_500', 'GREY_600', 'GREY_700', 'GREY_800', 'GREY_900', 'INK', 'TICK',
           'MUTED', 'GRID', 'AXIS', 'MARK', 'TITLE_PT', 'SUB_PT', 'TEXT_PT', 'TICK_PT', 'WIDTH_1COL',
           'WIDTH_TEXT', 'WIDTH_FULL', 'WIDTH_POST']
