import matplotlib.colors as mc
import matplotlib.pyplot as plt


def apply_style():
    plt.rcParams.update({
        # Match arxiv_template (mathpazo): Palatino body + STIX math.
        # 'DejaVu Sans' tail-fallback handles unicode glyphs (❄ etc.) that Palatino lacks.
        'font.family': ['serif', 'DejaVu Sans'],
        'font.serif': ['Palatino', 'TeX Gyre Pagella', 'Palatino Linotype', 'Book Antiqua',
                       'Computer Modern Roman', 'Times', 'DejaVu Serif'],
        'mathtext.fontset': 'stix',
        'mathtext.rm': 'Palatino',
        'mathtext.it': 'Palatino:italic',
        'mathtext.bf': 'Palatino:bold',
        'axes.linewidth': 0.8,
        'axes.edgecolor': '#333333',
        'axes.grid': True,
        'grid.linestyle': '--',
        'grid.linewidth': 0.5,
        'grid.alpha': 0.4,
        'grid.color': '#cccccc',
        'axes.titlesize': 13,
        'axes.titleweight': 'bold',
        'axes.labelsize': 12,
        'xtick.labelsize': 11,
        'ytick.labelsize': 11,
        'xtick.direction': 'out',
        'ytick.direction': 'out',
        'xtick.major.size': 3,
        'ytick.major.size': 3,
        'xtick.major.width': 0.7,
        'ytick.major.width': 0.7,
        'legend.fontsize': 10.5,
        'legend.frameon': False,
        'lines.linewidth': 1.6,
        'lines.markersize': 6,
        'figure.dpi': 110,
        'savefig.dpi': 200,
        'savefig.bbox': 'tight',
    })


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
