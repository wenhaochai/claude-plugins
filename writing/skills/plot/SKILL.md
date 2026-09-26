---
name: plot
description: "One matplotlib style for charts in posts and papers, after Epoch AI's charts: Instrument Sans at Epoch's measured sizes, margins and gaps; a light grid both ways and only the baseline axis; the quantity above each column and panel names inside; Google's GM2 tones, toned by mark size; layout set in inches. style.py plus one worked example. Use when the user wants a chart for a post or a paper. Skip for exploratory notebook plots."
---

# Plot

Two files: `style.py` (with `fonts/`) and `example.py`, a 2x2 grid of best-so-far step charts. Copy
both, plus `fonts/`, next to your script, and start from the example.

```python
from style import *
apply_style()
fig, axes = canvas(rows, cols, width=WIDTH_TEXT, panel_height=1.35, title=None,
                   legend=[('Model A', BLUE), ('Model B', LIGHT)], quantity='Throughput (MB/s)')
ax.plot(...)                      # or ax.step / ax.bar
nice_y(ax, lo, hi)                # the y range, round steps, the values on their grid lines
room(ax)                          # then x room: past the y values, and past the last grid line
panel_label(ax, 'Setting A')      # the panel's name inside it, on a white ground
save(fig, HERE / 'name')          # name.pdf + name.png, fitted, raises on text off the canvas
```

Epoch's other forms are options of the same calls; their docstrings give the details.

| Form | How |
|---|---|
| Subtitle, footnote | `canvas(subtitle=..., note=..., note_style='italic')` |
| Legend placement | `legend_loc='row'`, `'right'`, `'inline'` (on the quantity's row) or `'column'` (with `legend_title`) |
| Legend swatches | `(name, colour, kind)`, kind `'line'`, `'dash'`, `'dot'`, `'ring'`, `'box'` or `'ci'` |
| Export ticks | `canvas(ticks='left')`, then `y_values(ax, ticks, fmt)`: values left of the panel on tick marks |
| Scatter points | `dots(ax, x, y, colour)`: a translucent fill in a solid edge |
| Annotation | `callout(ax, text_xy, target_xy, lines)`: a note with a curved arrow |
| Direct labels | `end_labels(ax, [(y_end, name, colour), ...])`: line names at their ends, spread apart |
| Web-canvas charts | `title_pt`, `tick_pt`, `note_pt`, `side=0.10` (see rule 5) |

## Rules

1. **Start minimal, add on request.** The first version has a title, one legend row, the series, and
   the axes. No value labels, callouts, end-of-line numbers, notes, reference or baseline lines, or
   shading until the owner asks, one at a time.
2. **The chart shows; the caption explains.** On the chart: the quantity and unit (`Throughput (MB/s)`),
   series names, each panel's identity. In the caption: the statistic (fastest of 5 runs), transforms
   (best so far), the workload, exclusions, caveats. "Best MB/s so far, TinyLlama" is a caption written
   on an axis.
3. **The words are the owner's or the data's.** The title is the owner's sentence; until there is one,
   no title, or a draft that is called a draft. Axes use the data's own numbering (iterations 2 to 10,
   schemes 1 to 76, gaps kept). Renumber or relabel only on the owner's decision, and say so in the
   caption.
4. **The chart type follows the data.** A best-so-far chart is a step chart: the running maximum of
   what the run kept, never going down, changing at integer ticks, with a tick and grid line at every
   step so each corner sits on one. Bars start at 0. A categorical axis has no grid lines.
5. **One face at Epoch's sizes.** Instrument Sans (SIL OFL, bundled) is the closest free face to Epoch's
   Messina Sans. The sizes were measured off Epoch's 2400 px exports scaled to 6.32 in, matched on the
   lowercase and on where titles break: title 12.2 pt semibold, subtitle 9.3, every other word 7.35,
   tick values 7. Weight tells the roles apart: the quantity and axis names medium, the rest regular.
   Charts that Epoch sets on its narrower web canvas take a title near 9.2 pt and ticks at text size.
6. **Light grid, one axis, nothing touching.** Grid both ways on numeric axes, only the baseline axis,
   no tick marks: values sit just above their grid lines at the left edge, the quantity sits above
   each column, and panel names sit inside, top left, on white. Values are lifted off their lines, the
   x range runs past the last grid line, and headroom above the data holds the name. `ticks='left'` is
   Epoch's export form: values left of the panel on short tick marks.
7. **The y range starts where the data does.** 0 only when 0 is part of the comparison (shares, counts,
   latencies, bars); otherwise a round value just below the data. Round steps (1, 1.5, 2, 2.5, 3, 5 x
   10^k), 3 or more bands, each tall enough for the panel's name to clear the next value.
8. **Layout in inches, top down.** Title, legend row, quantity, panels and gaps are fixed distances
   measured off Epoch's exports, so every figure has the same rhythm, with 0.19 in clear at both sides
   and the top. The title spans the width between the margins at one size; a one-word last line warns,
   and the fix is to rephrase.
9. **Placement width, never cropped.** Draw at the width the figure is placed at and include it at
   natural size: `WIDTH_1COL` 5.5 in (NeurIPS, ICML, ICLR text width), `WIDTH_TEXT` 6.32 in (a
   one-column paper with narrower margins), `WIDTH_FULL` 7.6 in, `WIDTH_POST` 4.4 in for a post (a
   1600 px PNG). Never `bbox_inches='tight'`.
10. **A colour means one thing, and every colour is Google's.** Every colour is a GM2 tone
    (`tone(hue, grade)`); none is computed. Neutrals come from the GM2 grey ramp.

    | Use | Colours |
    |---|---|
    | A compared pair; a third series | `BLUE`, `LIGHT` (blue 600, 300); `GREY` |
    | An ordered set | `family_4(hue)` (grades 300, 500, 700, 900) |
    | Distinct categories: lines, points, small marks | `STRONG` (600) |
    | Distinct categories: bars | `MEDIUM` (400) |
    | Distinct categories: stacked areas, treemap cells | `SOFT` (300) |
    | Text set in a series' colour | `WORDS` (700) |

    Categories run blue, red, yellow, green, purple. The larger the inked area, the lighter the tone, as
    FiveThirtyEight and Datawrapper do. Yellow lines and words take 900, the only Google yellow at 3:1
    on white. Context behind a highlight steps down a set or goes grey, and stacked neighbours are split
    by thin white edges. Hold each series' colour across a piece; the legend names every colour.
11. **The docstring says where the numbers came from:** what the chart shows, the data source by path or
    run id, the formula for any derived quantity, the output. An example without measured data says
    `contains no measured results` in its first line.
12. **A restyle never touches data; look at the output.** Diff the plotted numbers after a styling pass,
    then render and open the file.

## Captions

A caption stands alone: what is plotted, what the axes are, how the numbers were made (rule 2), and what
to take away. The prose side is RULE-P13 of the `style` skill.

## Dependencies

`matplotlib >= 3.6`, `numpy >= 1.20`. The font ships in `fonts/`; nothing else to install.
