---
name: plot
description: Matplotlib templates for paper / blog / report figures with a Google-brand palette, Palatino body font (matches arxiv mathpazo), and an announcement-clean default frame — L-shaped ink spines, no grid, left-aligned bold titles with a white-edged dot legend row above the axes (header_legend + finalize_headers), never in-axes legends. Color rule; up to 3 series = lightness steps of one brand hue (hue_ramp/twotone), more than 3 = distinct Google hues. Use when the user asks for a chart they will save and paste into a paper, slide deck, or write-up — bar, boxplot, line, scatter variants. Templates ship pre-genericized (Model A/B, Metric A/B); replace with real names when applying. Skip for one-off exploratory plots inside notebooks where styling does not matter.
---

# Plot

Drop-in matplotlib templates for publication-quality figures. Each template is one .py file producing one figure, with no save logic — copy, swap data, add your `savefig`.

## Principles

The complete style contract. Every figure — template-derived or written from scratch — follows all of these; `style.py` encodes most of them as rc defaults and helpers.

1. **Frame: announcement-clean.** L-shaped spines only (top/right hidden), near-black ink `#1a1a1a` for spines/ticks/labels, **no grid**, outward ticks. All rc defaults — never restate them in a script; `clean_axes(ax)` re-asserts the frame only on twin/secondary axes the rc cannot reach.
2. **Titles: left-aligned, bold, no letter prefixes.** Plain `ax.set_title(text)` is enough — the rc makes it left-aligned bold ink, and titles are the ONLY bold text in a figure. **Never prefix titles with `(a)`/`(b)`/`(c)`** — reference panels in captions as Left/Middle/Right or Top/Bottom. Multi-panel suptitles: `fig.suptitle(..., x=0.01, ha='left', fontweight='bold', color=INK)`.
3. **Legend: a header row above the axes, never inside them.** `header_legend(ax, entries)` per axes, or `fig_header_legend(fig, entries)` for one figure-level row over a multi-panel grid (needs `constrained_layout`). Entries: `(label, color)` for white-edged dots, `(label, color, '-')` solid-line proxy, `(label, color, '--')` reference-dash proxy, or any marker char. Never hand-roll proxy handles; keep labels short enough that the row fits its panel's width.
4. **Spacing: measured, not guessed.** End every figure with `finalize_headers(fig)` — after all `set_title`/`header_legend` calls, before `savefig`. It measures the real legend heights and makes title, legend, and plot **equidistant** (one 6pt gap on each side of the legend row), level across panels, at any font size. `level_all=False` when legend-less panels sit in their own row under a figure-level header. After ANY header or font change, re-render and view the output — never ship a spacing change unchecked.
5. **Palette: Google brand only.** `G_BLUE/G_RED/G_YELLOW/G_GREEN/G_PURPLE/G_GREY` softened through the tier system (`brand → medium → paper (default) → soft → mute`). Paper series colors default to the medium tier.
6. **Hue count follows series count.** At most 3 colored series → ONE brand hue, lightness steps via `hue_ramp(base, n)` (index 0 lightest) or `twotone(base)`. More than 3 series → distinct Google hues at the medium tier. Neutrals never count as a hue: `HUMAN_DARK`/`HUMAN_SOFT` for human/reference cohorts, greys for annotations. Legend-less encodings (bar charts read off the axis) may use longer ramps.
7. **References: one grey, one dash.** Every reference/baseline line is `REF_GREY` + `REF_DASH`. A second dashed series in the same panel is distinguished by color and label, reusing `REF_DASH` rather than inventing a new pattern.
8. **Markers and bands.** Emphasized markers get `markeredgecolor='white'`, width 0.6–0.8. Confidence bands are the same hue as their line, `alpha` 0.12–0.18, `linewidth=0`.
9. **Fonts: Palatino with real bold, one size band.** Palatino body + STIX math (matches LaTeX `mathpazo`); `apply_style()` registers TeX Gyre Pagella from TeX Live because macOS Palatino.ttc exposes no bold face to matplotlib. Sizes: title 12.5 bold / axis label 14 / tick 13 (rc), header legend rows 9.5, annotations ≥ 8.5. Dense multi-panel grids may step down (title ~10, tick ~8), and every figure in one document stays inside this one band.
10. **Output: PDF is the artifact.** Save both `out.pdf` and a `dpi=200` PNG preview; papers include only the PDF. `matplotlib.use('Agg')` before pyplot in scripts; anchor outputs on `HERE = Path(__file__).resolve().parent`.
11. **Restyle never touches data.** A styling pass changes colors, legends, fonts, and spacing — not data loading, fits, tick semantics, or panel content. After restyling a figure with computed values, verify the numbers are identical to the pre-restyle run.

## Templates

| File | Type | Use when |
|---|---|---|
| `00_bar_vertical.py` | Vertical bar with reference baseline | Comparing a metric across discrete methods, optionally vs. a baseline value |
| `01_bar_horizontal.py` | Horizontal bar with value labels + dashed group separators | Component ablation rows where each row adds/removes a piece, value-labeled |
| `02_bar_grouped_twotone.py` | Grouped 2-series bar + error bars, same-hue dark/light pair | Two models compared across task categories with uncertainty |
| `03_bar_highlight_twotone.py` | Single-series bar, value labels, hero bar dark vs. light outlined rest | One model showcased against competitors on a single benchmark |
| `04_bar_stacked_segments.py` | Horizontal 2-segment stacked bar, % inside + totals | Each row splits into two exhaustive parts and the split share is the story |
| `05_bar_panel_grid.py` | 2×3 small-multiples bar grid, value labels, one twin log line | Telemetry-style summary of many categorical distributions in one figure |
| `10_box_horizontal.py` | Horizontal boxplot with 4-step family gradient | One categorical factor with ordered levels (e.g. progressively more compute) |
| `20_line_multi.py` | Multi-line plot with markers (linear xy) | Multiple model variants tracked across a hyperparameter sweep |
| `21_line_broken_y.py` | Multi-line with broken y-axis | Two groups of curves on disjoint y-ranges, both must stay visible |
| `22_line_logx.py` | Single line on log-x scale | Saturation as x sweeps orders of magnitude (data fraction, token count) |
| `23_line_loglog_compare.py` | Log-log multi-line with reference dashed line | Comparing scaling exponents across settings against a known reference |
| `24_line_twotone.py` | 2-line sweep with round markers, same-hue dark/light pair | Two models tracked across an inference/compute budget sweep |
| `25_scatter_twotone.py` | Metric-vs-compute scatter + baseline / best-recipe scaling lines | Showing a recipe's compute speedup over a baseline ladder |
| `26_line_frontier_twotone.py` | Running-max frontier line | Tracing the best-so-far result across a session or run |
| `27_line_band_scatter.py` | Smoothed mean + ±1σ band + raw event cloud | Per-event score over a long run where trend and spread both matter |
| `28_line_dual_axis.py` | Twin-y two-metric line, tinted axis labels | Two related series on incompatible scales across one x sweep |
| `29_line_event_annotations.py` | Dual-panel smoothed trajectory + pointed event callouts | Same derived metric over two runs with specific moments to call out |
| `30_scatter_powerlaw.py` | Log-log scatter + linear fit line | Clean power-law `y = a · C^b`; closed-form line + sample points |
| `31_scatter_isoflops.py` | Multi-curve parabola scatter with fits | IsoFLOPs-style — each compute budget yields a U-shape |
| `32_scatter_regression.py` | Two-cohort scatter + pooled regression line | Many observations from two settings sharing one linear relation |
| `33_errorbar_zone.py` | Binned mean ± SEM line + highlighted sweet-spot span | Metric peaks at an intermediate value of a binned factor |
| `40_area_share_stack.py` | 100%-stacked share area with direct in-band labels | A categorical mix evolving over a run, shares summing to 100% |
| `41_sankey_alluvial.py` | Alluvial/Sankey ribbons across ordered stages | Population re-partitioning across 3–4 stages with flows that matter |
| `42_dag_lineage.py` | Exploration DAG with highlighted winner lineage | Search/evolution explored many branches and one lineage won |
| `43_taxonomy_table.py` | Pill-table taxonomy figure (drawn table, not a chart) | Categorized checklist rows spanning lifecycle stages + metric columns |

## Quick start

1. Copy `style.py` and the chosen template into your figures directory.
2. Replace the data block and the placeholder labels (`Model A`, `Metric A`, ...) with real names.
3. Append the save call — after `finalize_headers(fig)`, which every header-bearing template already ends with:
   ```python
   fig.savefig('out.pdf')
   fig.savefig('out.png', dpi=200)
   ```
4. Run it, then LOOK at the output (Principle 4).

## Style knobs

```python
from style import (
    apply_style,          # one-shot rc setup — call once, first
    clean_axes,           # re-assert the frame on twin/secondary axes
    G_BLUE, G_RED, G_YELLOW, G_GREEN, G_GREY, G_PURPLE,
    INK, HUMAN_DARK, HUMAN_SOFT,   # ink + neutral greys
    REF_GREY, REF_DASH,            # the reference-line convention
    apply_tier, paper,             # softness control
    hue_ramp, twotone, family_4,   # single-hue ramps / pairs / gradients
    header_legend, fig_header_legend, finalize_headers,  # the header
    rounded_bar, lighten, darken, arrow,
)
```

- **Global softness**: edit `DEFAULT_TIER = 'paper'` in `style.py` (`brand`/`medium`/`paper`/`soft`/`mute`).
- **Per-use softness**: `apply_tier(G_BLUE, 'soft')`.
- **Hex-per-tier table**: `python style.py` prints it (mirrored as a comment in `style.py`).

## Naming convention (pre-genericized)

Every template label is a placeholder: `Model A/B` (methods), `Metric A` (metrics), `Task A` (categories), `Modality A` (domains), `Component 1..4` (ablation increments), `Setup A` (configurations), `Baseline` / `Reference` (comparison values and curves). Replace before saving — never ship a figure with placeholder names.

## Conventions

- One figure per file; multi-panel needs are composed by the caller.
- Templates never call `plt.show()` or `fig.savefig(...)` — add yours after `finalize_headers`.
- `style.py` must be importable from the template's directory.
- `figsize` targets single-column / half-page paper figures (≈4×3 to 6×3.5 in); full-width paper figures use 7.6 in.

## Dependencies

- `matplotlib >= 3.6`, `numpy >= 1.20`
- Fonts: macOS ships Palatino; for real bold (and on Linux) install TeX Live's `tex-gyre` (TeX Gyre Pagella) — `apply_style()` picks it up automatically.
