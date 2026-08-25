---
name: plot
description: Matplotlib templates for paper / blog / report figures with a Google-brand palette, Palatino body font (matches arxiv mathpazo), and an announcement-clean default frame — L-shaped ink spines, no grid, left-aligned bold titles with a white-edged dot legend row above the axes (header_legend), never in-axes legends. Color rule; up to 3 series = lightness steps of one brand hue (hue_ramp/twotone), more than 3 = distinct Google hues. Use when the user asks for a chart they will save and paste into a paper, slide deck, or write-up — bar, boxplot, line, scatter variants. Templates ship pre-genericized (Model A/B, Metric A/B); replace with real names when applying. Skip for one-off exploratory plots inside notebooks where styling does not matter.
---

# Plot

Drop-in matplotlib templates for publication-quality figures. Each template is one .py file producing one subplot, with no save logic — copy, swap data, add your `savefig`.

## Principles

The complete style contract. Every figure — template-derived or written from scratch — follows all of these; `style.py` encodes most of them as rc defaults and helpers.

1. **Frame: announcement-clean.** L-shaped spines only (top/right hidden), near-black ink `#1a1a1a` for spines/ticks/labels, **no grid**, outward ticks. `clean_axes(ax)` re-asserts the frame on twin/secondary axes.
2. **Titles: left-aligned, bold, no letter prefixes.** Every title is left-aligned bold ink — the rc default, so plain `ax.set_title(text)` is enough. Titles are the ONLY bold text in a figure. **Never prefix titles with `(a)`/`(b)`/`(c)`** — reference panels in captions as Left/Middle/Right or Top/Bottom instead. Multi-panel suptitles: `fig.suptitle(..., x=0.01, ha='left', fontweight='bold', color=INK)`.
3. **Legend: a header row above the axes, never inside them.** The series legend is a horizontal white-edged proxy row BELOW the title and ABOVE the plot: `header_legend(ax, entries)` per axes, `fig_header_legend(fig, entries)` for one figure-level row over a multi-panel grid (needs `constrained_layout`), `title_legend(ax, title, entries)` when the title is drawn as text on a single-axes figure. Entries are `(label, color)` for dots, `(label, color, '--')` for a dashed line proxy, `(label, color, '-')` for a solid line proxy, or any marker char. Keep labels short enough that the row stays inside its panel's width.
4. **Spacing: measured, not guessed.** Call `finalize_headers(fig)` once per figure, after every `set_title`/`header_legend` and right before `savefig`: it draws the canvas, measures each header legend's true height in points, levels every left title to one pad (tallest legend + fixed gaps), and re-anchors each legend so its top hangs a constant 4pt below the title — title/legend/plot gaps stay uniform across panels regardless of row counts or font sizes. After ANY header or font change, re-render and view the output; never ship a spacing change unchecked.
5. **Palette: Google brand only.** `G_BLUE/G_RED/G_YELLOW/G_GREEN/G_PURPLE/G_GREY` softened through the tier system (`brand → medium → paper (default) → soft → mute`). Paper series colors default to the medium tier.
6. **Hue count follows series count.** At most 3 colored series → ONE brand hue, lightness steps via `hue_ramp(base, n)` (index 0 lightest → n-1 darkest) or `twotone(base)`. More than 3 series → distinct Google hues at the medium tier (single-hue ramps stop being tellable apart past three steps). Neutrals never count as a hue: `HUMAN_DARK`/`HUMAN_SOFT` for human/reference cohorts, greys for annotations. Legend-less encodings (bar charts read off the axis) may use longer ramps.
7. **References: one grey, one dash.** Every reference/baseline line is `REF_GREY` + `REF_DASH` — no other dash vocabulary for references. A second dashed series in the same panel is distinguished by color and label, reusing `REF_DASH` rather than inventing a new pattern.
8. **Markers and bands.** Emphasized scatter/line markers get `markeredgecolor='white'`, width 0.6–0.8. Confidence bands are the same hue as their line, `alpha` 0.12–0.18, `linewidth=0`.
9. **Fonts: Palatino with real bold, one size band.** Palatino body + STIX math (matches LaTeX `mathpazo`); `apply_style()` registers TeX Gyre Pagella from a TeX Live install because macOS Palatino.ttc exposes no bold face to matplotlib — without it, bold silently renders regular. Sizes: title 12.5 bold / axis label 14 / tick 13 (rc), header legend rows 9.5, annotations ≥ 8.5. Dense multi-panel grids may step down (title ~10, tick ~8) but never below annotation-floor legibility, and every figure in one document stays inside this one band.
10. **Output: PDF is the artifact.** Save both `fig.savefig(out.pdf)` and a `dpi=200` PNG; the PDF is what ships (papers include only `.pdf`), the PNG is for preview. `matplotlib.use('Agg')` before pyplot; anchor outputs on `HERE = Path(__file__).resolve().parent`.
11. **Restyle never touches data.** A styling pass changes colors, legends, fonts, and spacing — not data loading, fits, tick semantics, or panel content. After restyling a figure with computed values, verify the printed/fitted numbers are identical to the pre-restyle run.

The shared `style.py` also provides: `legend_handles(entries)` proxy builder; `family_4(base)` for ordered categorical gradients; `rounded_bar(ax, cx, top, w)` for bars with rounded top corners (base sits square on `ylim[0]`); `paper(base)` / `lighten` / `darken` for one-off color tweaks; `arrow(label, 'down'|'up')` to append `↓` / `↑` to titles.

## Templates

| File | Type | Use when |
|---|---|---|
| `00_bar_vertical.py` | Vertical bar with reference baseline | Comparing a metric across discrete methods, optionally vs. a baseline value |
| `01_bar_horizontal.py` | Horizontal bar with value labels + dashed group separators | Component ablation rows where each row adds/removes a piece, value-labeled |
| `02_bar_grouped_twotone.py` | Grouped 2-series bar + error bars, announcement-clean (no grid, L-spines, dot legend, same-hue dark/light pair) | Two models compared across task categories with uncertainty, blog-post look |
| `03_bar_highlight_twotone.py` | Single-series bar, value labels on top, hero bar dark vs. light outlined rest, non-zero baseline | One model showcased against competitors on a single benchmark, release-chart look |
| `10_box_horizontal.py` | Horizontal boxplot with 4-step family gradient | One categorical factor with ordered levels (e.g. progressively more compute) |
| `20_line_multi.py` | Multi-line plot with markers (linear xy) | Multiple model variants tracked across a hyperparameter sweep |
| `21_line_broken_y.py` | Multi-line with broken y-axis | Two groups of curves on disjoint y-ranges, both must stay visible |
| `22_line_logx.py` | Single line on log-x scale | Saturation as x sweeps orders of magnitude (data fraction, token count) |
| `23_line_loglog_compare.py` | Log-log multi-line with reference dashed line | Comparing scaling exponents across settings against a known reference |
| `24_line_twotone.py` | 2-line sweep with round markers, announcement-clean (no grid, L-spines, dot legend, same-hue dark/light pair) | Two models tracked across an inference/compute budget sweep, blog-post look |
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
    apply_style,                           # one-shot rcParams setup (L-spines, ink, no grid)
    clean_axes,                            # re-assert the frame on twin/secondary axes
    G_BLUE, G_RED, G_YELLOW, G_GREEN,
    G_GREY, G_PURPLE,                      # Google brand constants
    INK, HUMAN_DARK, HUMAN_SOFT,           # near-black ink + neutral cohort greys
    REF_GREY, REF_DASH,                    # reference-line convention (grey + one dash pattern)
    apply_tier, paper,                     # softness control
    hue_ramp,                              # n-step single-hue ramp (idx 0=lightest)
    family_4,                              # 4-step gradient (idx 0=lightest, 3=darkest)
    twotone,                               # same-hue (dark, light) 2-series pair
    title_legend,                          # announcement header: title + dot legend above axes
    rounded_bar,                           # bar with rounded top corners
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
