---
name: plot
description: "Matplotlib chart templates for paper, blog, and slide figures: bar, boxplot, line, scatter, errorbar, area, sankey, DAG. Announcement-clean frame with L-spines, no grid, left-aligned bold titles, and a legend row above the axes. Google palette, venue-matched serif type. Use when the user wants a chart they will save and paste into a document. Skip for exploratory notebook plots. Schematics with no data axes go to `concept`; figures drawn in LaTeX go to `tikz`."
---

# Plot

Drop-in matplotlib templates for publication-quality charts. Each template is one `.py` file producing
one figure, with no save logic: copy, swap the data, add your `savefig`.

Read `${CLAUDE_PLUGIN_ROOT}/figures/DOCTRINE.md` first. It holds the ten rules every figure follows,
including canvas width, venue fonts, colour meaning, and the no-tight-crop rule. This file covers only
what is specific to charts.

## The chart frame

`style.py` encodes the frame as rc defaults, so a template never restates them.

1. **Frame.** L-spines only, near-black ink `#1a1a1a`, no grid, outward ticks. `clean_axes(ax)`
   re-asserts it on twin and secondary axes the rc cannot reach.
2. **Titles.** Plain `ax.set_title(text)`: the rc makes it left-aligned bold ink, and titles are the
   only bold text in a figure. Never prefix a title with `(a)` or `(b)`; refer to panels in the
   caption as Left, Middle, Right. Multi-panel suptitles take
   `fig.suptitle(..., x=0.01, ha='left', fontweight='bold', color=INK)`.
3. **Legend.** A header row above the axes, never inside them. `header_legend(ax, entries)` per axes,
   or `fig_header_legend(fig, entries)` for one row over a grid, which needs `constrained_layout`.
   Entries are `(label, color)` for a white-edged dot, `(label, color, '-')` for a line proxy,
   `(label, color, '--')` for a reference dash, or any marker character. Never hand-roll proxy handles.
4. **Spacing is measured, not guessed.** End every figure with `finalize_headers(fig)`, after all
   `set_title` and `header_legend` calls and before `savefig`. It measures the real legend heights and
   makes title, legend, and plot equidistant, level across panels, at any font size. Pass
   `level_all=False` when legend-less panels sit in their own row under a figure-level header.
5. **Hue count follows series count.** At most 3 coloured series means one brand hue with lightness
   steps, `hue_ramp(base, n)` with index 0 lightest, or `twotone(base)`. More than 3 means distinct
   Google hues at the medium tier. Neutrals never count as a hue: `HUMAN_DARK` and `HUMAN_SOFT` for
   human or reference cohorts, greys for annotations. A legend-less encoding read off the axis, such
   as a bar chart, may use a longer ramp.
6. **References: one grey, one dash.** Every reference or baseline line is `REF_GREY` with `REF_DASH`.
   A second dashed series in the same panel separates by colour and label, reusing the same pattern.
7. **Markers and bands.** An emphasized marker gets `markeredgecolor='white'` at width 0.6 to 0.8.
   A confidence band takes the hue of its line at `alpha` 0.12 to 0.18 and `linewidth=0`.
8. **Sizes.** Title 12.5 bold, axis label 14, tick 13 from the rc; header legend rows 9.5; annotations
   at least 8.5. A dense multi-panel grid may step down to title 10 and tick 8, and every figure in one
   document stays inside that one band.
9. **Output.** Save `out.pdf` as the shipping artifact plus a `dpi=200` PNG preview; the paper includes
   only the PDF. Call `matplotlib.use('Agg')` before pyplot, and anchor paths on
   `HERE = Path(__file__).resolve().parent`.

## Templates

| File | Type | Use when |
|---|---|---|
| `00_bar_vertical.py` | Vertical bar with reference baseline | Comparing a metric across discrete methods, optionally against a baseline value |
| `01_bar_horizontal.py` | Horizontal bar, value labels, dashed group separators | Component ablation rows where each row adds or removes a piece |
| `02_bar_grouped_twotone.py` | Grouped 2-series bar with error bars, same-hue pair | Two models across task categories with uncertainty |
| `03_bar_highlight_twotone.py` | Single-series bar, hero bar dark against light outlined rest | One model showcased against competitors on one benchmark |
| `04_bar_stacked_segments.py` | Horizontal 2-segment stacked bar, percent inside plus totals | Each row splits into two exhaustive parts and the split is the story |
| `05_bar_panel_grid.py` | 2x3 small-multiples bar grid, one twin log line | Telemetry-style summary of many categorical distributions |
| `10_box_horizontal.py` | Horizontal boxplot, 4-step family gradient | One categorical factor with ordered levels, such as more compute |
| `20_line_multi.py` | Multi-line with markers, linear axes | Model variants across a hyperparameter sweep |
| `21_line_broken_y.py` | Multi-line with broken y-axis | Two groups of curves on disjoint y-ranges, both must stay visible |
| `22_line_logx.py` | Single line on log-x | Saturation as x sweeps orders of magnitude |
| `23_line_loglog_compare.py` | Log-log multi-line with reference dash | Comparing scaling exponents against a known reference |
| `24_line_twotone.py` | 2-line sweep, round markers, same-hue pair | Two models across an inference or compute budget |
| `25_scatter_twotone.py` | Metric-vs-compute scatter with baseline and best-recipe lines | A recipe's compute speedup over a baseline ladder |
| `26_line_frontier_twotone.py` | Running-max frontier line | Best-so-far result across a session or run |
| `27_line_band_scatter.py` | Smoothed mean, ±1σ band, raw event cloud | Per-event score over a long run where trend and spread both matter |
| `28_line_dual_axis.py` | Twin-y two-metric line, tinted axis labels | Two related series on incompatible scales |
| `29_line_event_annotations.py` | Dual-panel trajectory with pointed callouts | One derived metric over two runs with moments to call out |
| `30_scatter_powerlaw.py` | Log-log scatter with linear fit | Clean power law `y = a · C^b` |
| `31_scatter_isoflops.py` | Multi-curve parabola scatter with fits | IsoFLOPs-style, each compute budget yielding a U-shape |
| `32_scatter_regression.py` | Two-cohort scatter, pooled regression line | Many observations from two settings sharing one linear relation |
| `33_errorbar_zone.py` | Binned mean ± SEM with highlighted span | A metric peaking at an intermediate value of a binned factor |
| `40_area_share_stack.py` | 100% stacked share area, in-band labels | A categorical mix evolving over a run |
| `41_sankey_alluvial.py` | Alluvial ribbons across ordered stages | Population re-partitioning across 3 to 4 stages |
| `42_dag_lineage.py` | Exploration DAG with highlighted winner lineage | A search explored many branches and one lineage won |
| `43_taxonomy_table.py` | Pill-table taxonomy figure, drawn rather than plotted | Categorized checklist rows across lifecycle stages |

## Quick start

1. Copy `${CLAUDE_PLUGIN_ROOT}/figures/style.py` and the chosen template into your figures directory.
2. Replace the data block and the placeholder labels with real names.
3. Append the save call, after the `finalize_headers(fig)` that every header-bearing template ends with:
   ```python
   fig.savefig('out.pdf')
   fig.savefig('out.png', dpi=200)
   ```
4. Run it, then look at the output.

## Style knobs

```python
from style import (
    apply_style,          # one-shot rc setup, call once, first; venue='arxiv'|'iclr'|...
    clean_axes,           # re-assert the frame on twin/secondary axes
    G_BLUE, G_RED, G_YELLOW, G_GREEN, G_GREY, G_PURPLE,
    INK, HUMAN_DARK, HUMAN_SOFT,   # ink + neutral greys
    REF_GREY, REF_DASH,            # the reference-line convention
    apply_tier, paper,             # softness control
    hue_ramp, twotone, family_4,   # single-hue ramps, pairs, gradients
    header_legend, fig_header_legend, finalize_headers,
    rounded_bar, lighten, darken, arrow,
)
```

Global softness lives in `DEFAULT_TIER` in `style.py`, one of `brand`, `medium`, `paper`, `soft`,
`mute`. Per-use softness is `apply_tier(G_BLUE, 'soft')`. `python style.py` prints the hex-per-tier
table.

## Conventions

- One figure per file; the caller composes multi-panel needs.
- Templates never call `plt.show()` or `fig.savefig(...)`; add yours after `finalize_headers`.
- Every label ships pre-genericized: `Model A/B`, `Metric A`, `Task A`, `Modality A`, `Component 1..4`,
  `Setup A`, `Baseline`, `Reference`. Replace them before saving.
- `figsize` targets 5.5 in for a single-column figure at 1:1, 7.6 in for a full-width one.

## Dependencies

`matplotlib >= 3.6`, `numpy >= 1.20`. For real bold, and on Linux for any correct face, install TeX
Live's `tex-gyre`; `apply_style()` picks it up automatically and falls back silently when it is absent.
