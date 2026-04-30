---
name: plot
description: Matplotlib templates for paper / blog / report figures with a Google-brand palette and Palatino body font (matches arxiv mathpazo). Use when the user asks for a chart they will save and paste into a paper, slide deck, or write-up — bar, boxplot, line, scatter variants. Templates ship pre-genericized (Model A/B, Metric A/B); replace with real names when applying. Skip for one-off exploratory plots inside notebooks where styling does not matter.
---

# Plot

Drop-in matplotlib templates for publication-quality figures. Each template is one .py file producing one subplot, with no save logic — copy, swap data, add your `savefig`.

The shared `style.py` provides:

- **Font.** Palatino body + STIX math, matching the LaTeX `mathpazo` package used in arxiv-style templates. DejaVu Sans tail-fallback handles unicode glyphs (`❄`, `⚡`) that Palatino lacks.
- **Palette.** Google brand colors (Blue/Red/Yellow/Green/Grey + extended Purple) softened to a paper-friendly tier by default.
- **Tier system.** Same color, five softness levels: `brand → medium → paper (default) → soft → mute`. One knob switches the global feel.
- **Helpers.** `family_4(base)` for ordered categorical gradients; `paper(base)` / `lighten` / `darken` for one-off color tweaks; `arrow(label, 'down'|'up')` to append `↓` / `↑` to titles.

## Templates

| File | Type | Use when |
|---|---|---|
| `00_bar_vertical.py` | Vertical bar with reference baseline | Comparing a metric across discrete methods, optionally vs. a baseline value |
| `01_bar_horizontal.py` | Horizontal bar with value labels + dashed group separators | Component ablation rows where each row adds/removes a piece, value-labeled |
| `10_box_horizontal.py` | Horizontal boxplot with 4-step family gradient | One categorical factor with ordered levels (e.g. progressively more compute) |
| `20_line_multi.py` | Multi-line plot with markers (linear xy) | Multiple model variants tracked across a hyperparameter sweep |
| `21_line_broken_y.py` | Multi-line with broken y-axis | Two groups of curves on disjoint y-ranges, both must stay visible |
| `22_line_logx.py` | Single line on log-x scale | Saturation as x sweeps orders of magnitude (data fraction, token count) |
| `23_line_loglog_compare.py` | Log-log multi-line with reference dashed line | Comparing scaling exponents across settings against a known reference |
| `30_scatter_powerlaw.py` | Log-log scatter + linear fit line | Clean power-law `y = a · C^b`; closed-form line + sample points |
| `31_scatter_isoflops.py` | Multi-curve parabola scatter with fits | IsoFLOPs-style — each compute budget yields a U-shape, marker size scales with parameter count |

## Quick start

1. Copy `style.py` and the chosen template into your figures directory.
2. Edit the data block at the top of the template (data is illustrative — replace with yours).
3. Replace placeholder labels (`Model A`, `Metric A`, `Task A`, `Modality A`, `Component 1`, `Setup A`, `Baseline`, `Reference`) with the real names.
4. Add a save call before the script ends:
   ```python
   fig.savefig('out.pdf')
   fig.savefig('out.png', dpi=200)
   ```
5. Run `python <template>.py`.

## Style knobs

```python
from style import (
    apply_style,                           # one-shot rcParams setup
    G_BLUE, G_RED, G_YELLOW, G_GREEN,
    G_GREY, G_PURPLE,                      # Google brand constants
    apply_tier, paper,                     # softness control
    family_4,                              # 4-step gradient (idx 0=lightest, 3=darkest)
    lighten, darken,                       # one-off color adjustments
    arrow,                                 # `Metric A ↓` title helper
)

apply_style()                              # call once at the top of every figure script
```

**Switch the global softness tier**: edit `DEFAULT_TIER = 'paper'` in `style.py` to one of `brand` / `medium` / `paper` / `soft` / `mute`. All `paper(base)` and `family_4(base)` calls follow.

**Per-color tier**: `apply_tier(G_BLUE, 'soft')` overrides the default for one usage.

**Regenerate the per-tier hex table** in `style.py`'s docstring: `python style.py`.

## Naming convention (pre-genericized)

Every label in the templates is a placeholder, picked so the figure parses without context:

| Placeholder | Replace with |
|---|---|
| `Model A`, `Model B`, ... | Method / model names |
| `Metric A`, `Metric B`, ... | Metric names (PPL, accuracy, FID, ...) |
| `Task A`, `Task B`, ... | Task / dataset categories |
| `Method A`, `Method B`, ... | Approach categories |
| `Modality A`, `Modality B` | Domain / modality (vision, language, ...) |
| `Component 1..4` | Ablation increments |
| `Setup A`, `Setup A (2×)` | Configuration / scale variants |
| `Baseline` | The reference value (e.g. text-only PPL) |
| `Reference` | A canonical comparison curve (e.g. Chinchilla scaling) |

Replace before saving — never ship a figure with placeholder names in a paper.

## Conventions

- One subplot per file. If a figure needs two panels of the same type, call the template twice on different axes; if it needs two different types, copy two templates and lay them out with `gridspec`.
- Templates do not call `plt.show()` or `fig.savefig(...)` — add yours.
- All templates assume `style.py` is importable from the same directory.
- Output sizes target a single-column or half-page paper figure (`figsize` ranges roughly 4×3 to 5.6×3.4 inches). Adjust as needed.

## Dependencies

- `matplotlib >= 3.6` (per-glyph font fallback)
- `numpy >= 1.20`
- macOS: `Palatino` ships with the system; on Linux install `tex-gyre` (`TeX Gyre Pagella`) or any Palatino clone listed in `font.serif` of `style.py`.
