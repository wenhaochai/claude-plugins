---
name: plot
description: Matplotlib templates for paper / blog / report figures with a Google-brand palette, Palatino body font (matches arxiv mathpazo), and an announcement-clean default frame — L-shaped ink spines, no grid, left-aligned bold titles with a white-edged dot legend row above the axes (header_legend), never in-axes legends. Color rule; up to 3 series = lightness steps of one brand hue (hue_ramp/twotone), more than 3 = distinct Google hues. Use when the user asks for a chart they will save and paste into a paper, slide deck, or write-up — bar, boxplot, line, scatter variants. Templates ship pre-genericized (Model A/B, Metric A/B); replace with real names when applying. Skip for one-off exploratory plots inside notebooks where styling does not matter.
---

# Plot

Drop-in matplotlib templates for publication-quality figures. Each template is one .py file producing one subplot, with no save logic — copy, swap data, add your `savefig`.

The shared `style.py` provides:

- **Frame (announcement-clean, the default for every template).** L-shaped spines only (top/right hidden), near-black ink `#1a1a1a` for spines/ticks/labels, **no grid**, outward ticks. `clean_axes(ax)` re-asserts the frame on twin/secondary axes.
- **Header (title + legend, the OpenAI-release look).** Every title is **left-aligned bold** ink — that is the rc default, so plain `ax.set_title(text)` is enough, and titles are the ONLY bold text in a figure. The series legend is a horizontal white-edged proxy row sitting ABOVE the axes, BELOW the title: `header_legend(ax, entries)` per axes, `fig_header_legend(fig, entries)` for one figure-level row over a multi-panel grid (needs `constrained_layout`), `title_legend(ax, title, entries)` when the title is drawn as text on a single-axes figure. **Never park a legend inside the axes.** Entries are `(label, color)` for dots, `(label, color, '--')` for a dashed reference proxy, `(label, color, '-')` for a solid line proxy, or any marker char.
- **Font.** Palatino body + STIX math, matching the LaTeX `mathpazo` package used in arxiv-style templates. DejaVu Sans tail-fallback handles unicode glyphs (`❄`, `⚡`) that Palatino lacks. Generous rc sizes (title 11 bold / label 14 / tick 13 / legend 12.5); dense multi-panel figures override downward locally, header legend rows usually 7.5–8.5.
- **Palette.** Google brand colors (Blue/Red/Yellow/Green/Grey + extended Purple) softened to a paper-friendly tier by default.
- **Color rule: hue count follows series count.** At most 3 colored series → ONE brand hue, lightness steps via `hue_ramp(base, n)` (index 0 lightest → n-1 darkest) or `twotone(base)`. **More than 3 series → distinct Google hues** at the medium tier (single-hue ramps stop being tellable apart past three steps). Neutrals never count as a hue: `HUMAN_DARK`/`HUMAN_SOFT` for human/reference cohorts, `REF_GREY` + `REF_DASH` for reference lines, greys for annotations. Legend-less encodings (bar charts read off the axis) may use longer ramps.
- **Tier system.** Same color, five softness levels: `brand → medium → paper (default) → soft → mute`. One knob switches the global feel.
- **Helpers.** `hue_ramp(base, n)` single-hue ordered ramps; `twotone(base)` for same-hue dark/light 2-series pairs; `legend_handles(entries)` / `header_legend` / `fig_header_legend` / `title_legend` for the announcement header; `family_4(base)` for ordered categorical gradients; `rounded_bar(ax, cx, top, w)` for bars with rounded top corners (base sits square on `ylim[0]`); `paper(base)` / `lighten` / `darken` for one-off color tweaks; `arrow(label, 'down'|'up')` to append `↓` / `↑` to titles.

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
