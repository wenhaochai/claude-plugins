---
name: plot
description: "18 matplotlib chart templates for paper, blog, and slide figures: bars, boxplot, curve grids, broken axes, IsoFLOPs and labelled-frontier scatter, quadrant plots, stacked shares, alluvial ribbons, sparse-group DAGs. All on one header: a left-aligned Lato Heavy title with a single legend row above the axes, never inside them, spaced by measurement. L-spines, no grid, Google palette, venue-matched serif. Use when the user wants a chart they will save and paste into a document. Skip for exploratory notebook plots. Schematics with no data axes go to `concept`."
---

# Plot

Drop-in matplotlib templates for publication-quality charts. Each template is one `.py` file producing
one figure, with no save logic: copy, swap the data, add your `savefig`.

Read `${CLAUDE_PLUGIN_ROOT}/figures/DOCTRINE.md` first. It holds the eleven rules every figure follows,
including canvas width, venue fonts, colour meaning, and the no-tight-crop rule. This file covers only
what is specific to charts.

## The one header format

Every chart in this plugin carries the same two things in the same place: a
left-aligned Lato Heavy title, and under it one Lato Regular legend row that sits
above the axes. `header()` writes both, and `finalize_headers(fig)` measures the
real heights and makes the gaps equal.

```python
header(ax, 'What the figure claims', [('Model A', blue), ('Model B', red)])
...
finalize_headers(fig)          # once, after every header call, before savefig
```

A panel grid uses the figure-level pair instead, and its panels carry only their
own title:

```python
for ax, name in zip(axes.flat, PANELS):
    header(ax, name, size=PANEL_PT)
fig_header(fig, 'What the grid claims', [('Model A', blue), ('Model B', red)])
finalize_headers(fig, level_all=False)
```

Legend entries are `(label, color)` for a white-edged dot, `(label, color, '-')`
for a line proxy, `(label, color, '--')` for the reference dash, or any marker
character. Never hand-roll proxy handles, never pass `legend_size`, and never put
a legend inside the axes. A figure whose series are read off the axis, such as a
bar chart, passes no entries at all.

Two more rules keep the header uniform:

- **Titles carry no panel letters.** No `(a)` or `(b)`; refer to panels in the
  caption as Left, Middle, Right.
- **Direct labels beat legend rows.** When a handful of points or bands carry the
  argument, name them in place with `note(ax, x, y, text)` rather than adding
  entries the reader has to match by colour.

## The rest of the frame

`style.py` encodes all of this as rc defaults, so a template never restates them.

1. **Frame.** L-spines only, near-black ink `#1a1a1a`, no grid, outward ticks.
   `clean_axes(ax)` re-asserts it on twin and secondary axes the rc cannot reach.
2. **Type.** Ticks, axis labels and math take the venue's body serif; the headline
   and legend row take Lato. One scale, no sixth size:
   `HEADLINE 10.5 / PANEL 8.5 / LEGEND 8.0 / LABEL 8.0 / TICK 7.5 / NOTE 7.0`.
3. **Hue count follows series count.** Two series take `twotone(base)`, an
   ordered set of four takes `family_4(base)`, both one hue. More than that
   means distinct Google hues at the medium tier. Grey never counts as a hue.
4. **References: one grey, one dash.** Every reference or baseline line is
   `REF_GREY` with `REF_DASH`. A second dashed series separates by colour and
   label, reusing the same pattern.
5. **Markers and bands.** An emphasized marker gets `markeredgecolor='white'` at
   width 0.6 to 0.8. A confidence band takes the hue of its line at `alpha` 0.12
   to 0.18 and `linewidth=0`.
6. **Geometry.** `WIDTH_1COL` (5.5 in) for a single-column figure, `WIDTH_FULL`
   (7.6 in) for a full-width one, placed at 1:1 and never tight-cropped. The rc
   turns the layout engine on so the content fits the fixed canvas; a template
   that places its own axes turns it off with `fig.set_layout_engine('none')`.
7. **Output.** Save `out.pdf` as the shipping artifact plus a `dpi=200` PNG
   preview. Call `matplotlib.use('Agg')` before pyplot, and anchor paths on
   `HERE = Path(__file__).resolve().parent`.

## Templates

| File | Type | Use when |
|---|---|---|
| `02_bar_grouped_twotone.py` | Grouped 2-series bar with error bars, same-hue pair | Two models across task categories with uncertainty |
| `03_bar_highlight_twotone.py` | Single-series bar, hero bar dark against light outlined rest | One model showcased against competitors on one benchmark |
| `04_bar_stacked_segments.py` | Horizontal 2-segment stacked bar, percent inside plus totals | Each row splits into two exhaustive parts and the split is the story |
| `05_bar_panel_grid.py` | 2x3 small-multiples bar grid, one twin log line | Telemetry-style summary of many categorical distributions |
| `10_box_horizontal.py` | Horizontal boxplot, 4-step family gradient | One categorical factor with ordered levels, such as more compute |
| `21_line_broken_y.py` | Multi-line with broken y-axis | Two groups of curves on disjoint y-ranges, both must stay visible |
| `22_line_panel_grid.py` | Metric rows by setting columns, bands, one figure legend | Many metrics across many settings, compared down each column |
| `23_line_grid_reference.py` | One panel per setting, each against one shared reference dash | The same question per panel: who beats the reference, and where |
| `24_line_twotone.py` | 2-line sweep, round markers, same-hue pair | Two models across an inference or compute budget |
| `27_line_band_scatter.py` | Smoothed mean, ±1σ band, raw event cloud | Per-event score over a long run where trend and spread both matter |
| `31_scatter_isoflops.py` | Multi-curve parabola scatter with fits | IsoFLOPs-style, each compute budget yielding a U-shape |
| `32_scatter_regression.py` | Two-cohort scatter, pooled regression line | Many observations from two settings sharing one linear relation |
| `34_scatter_labeled_frontier.py` | Log-x scatter with error bars, frontier traced and its points named | Capability against cost, where the frontier is the argument |
| `35_scatter_quadrant.py` | Bubble scatter split at the medians, target quadrant shaded | Two properties at once, and the corner that holds the claim |
| `40_area_share_stack.py` | 100% stacked share area, in-band labels | A categorical mix evolving over one run |
| `41_sankey_alluvial.py` | Alluvial ribbons across ordered stages, optional grey majority | Population re-partitioning across 3 to 4 stages |
| `42_dag_sparse_groups.py` | Large grey DAG with a few groups picked out in colour | A search explored thousands of nodes and a handful matter |
| `43_area_share_compare.py` | Two 100% stacked shares side by side, one band vocabulary | The same mix under two runs, compared by band shape |

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
    header, fig_header, finalize_headers, note,   # the header format, and nothing else
    clean_axes,           # re-assert the frame on twin/secondary axes
    G_BLUE, G_RED, G_YELLOW, G_GREEN, G_GREY, G_PURPLE, INK, REF_GREY, REF_DASH,
    apply_tier, paper,             # softness control
    twotone, family_4,             # a same-hue pair, a 4-step gradient
    HEADLINE_PT, PANEL_PT, WIDTH_1COL, WIDTH_FULL,
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
- `figsize` takes `WIDTH_1COL` for a single-column figure at 1:1, `WIDTH_FULL` for a full-width one.

## Dependencies

`matplotlib >= 3.6`, `numpy >= 1.20`. For real bold, and on Linux for any correct face, install TeX
Live's `tex-gyre`; `apply_style()` picks it up automatically and falls back silently when it is absent.
