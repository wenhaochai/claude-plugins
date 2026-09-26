---
name: plot
description: "One matplotlib style for charts in posts and papers, after Epoch AI's charts: Instrument Sans, a light grid both ways, only the baseline axis, values sitting on their grid lines, the quantity above each column, panel names inside the panels, Google palette, layout set in inches. style.py plus one worked example. Use when the user wants a chart for a post or a paper. Skip for exploratory notebook plots."
---

# Plot

Two files: `style.py` (with `fonts/`) and `example.py`, a 2x2 grid of best-so-far step charts that uses
every helper. Copy both, plus `fonts/`, next to your script, and start from the example.

```python
from style import *
apply_style()
fig, axes = canvas(rows, cols, width=WIDTH_POST, panel_height=1.35, title=None,
                   legend=[('Model A', BLUE), ('Model B', LIGHT)], quantity='Throughput (MB/s)')
ax.plot(...)                      # or ax.step / ax.bar
room(ax)                          # x room: the y values on the left, space past the last grid line
nice_y(ax, lo, hi)                # the y range, round steps, the values on their grid lines
panel_label(ax, 'Setting A')      # the panel's name inside it, on a white ground
save(fig, HERE / 'name')          # name.pdf + name.png (1600 px), raises on text off the canvas
```

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
5. **One face, three sizes.** Instrument Sans (SIL OFL, bundled), the closest free face to Epoch's
   Messina Sans: title 10.5 pt medium, text 7 pt, tick values 6.3 pt.
6. **Light grid, one axis, nothing touching.** Grid both ways on numeric axes, only the baseline axis,
   no tick marks. Values sit just above their grid lines at the left edge; the quantity sits above each
   column; panel names sit inside, top left, on white. Values are lifted off their lines, the x range
   runs past the last grid line, and headroom above the data holds the name.
7. **The y range starts where the data does.** 0 only when 0 is part of the comparison (shares, counts,
   latencies, bars); otherwise a round value just below the data. Round steps (1, 1.5, 2, 2.5, 3, 5 x
   10^k), 3 or more bands, each tall enough for the panel's name to clear the next value.
8. **Layout in inches, top down.** Title, legend row, quantity, panels and gaps are fixed distances, so
   every figure has the same rhythm. The title spans the full width at one size; a one-word last line
   warns, and the fix is to rephrase.
9. **Placement width, never cropped.** Papers: `WIDTH_1COL` 5.5 in or `WIDTH_FULL` 7.6 in, placed at
   1:1 with `width=\linewidth`. Posts: `WIDTH_POST` 4.4 in, a 1600 px PNG. Never `bbox_inches='tight'`.
10. **A colour means one thing.** A compared pair takes one hue in two tones (`BLUE`, `LIGHT`), a third
    series `GREY`, an ordered set `family_4`, more than that distinct Google hues. Hold each series'
    colour across a piece; the legend names every colour.
11. **The docstring says where the numbers came from:** what the chart shows, the data source by path or
    run id, the formula for any derived quantity, the output. An example without measured data says
    `contains no measured results` in its first line.
12. **A restyle never touches data; look at the output.** Diff the plotted numbers after a styling pass,
    then render and open the file.

## Captions

A caption stands alone: what is plotted, what the axes are, how the numbers were made (rule 2), and what
to take away. The prose side of these rules is RULE-P13, P18 and P19 of the `style` skill.

## Dependencies

`matplotlib >= 3.6`, `numpy >= 1.20`. The font ships in `fonts/`; nothing else to install.
