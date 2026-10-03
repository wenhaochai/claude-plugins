---
name: plot
description: "One matplotlib style for charts in posts and papers, after Epoch AI's charts: Instrument Sans at Epoch's measured sizes, margins and gaps; a light grid both ways and only the baseline axis; the quantity above each column and panel names inside; Google's GM2 tones, toned by mark size; layout set in inches; a 4:5 card for social posts. style.py plus two worked examples. Use when the user wants a chart for a post or a paper. Skip for exploratory notebook plots."
---

# Plot

`style.py` (with `fonts/`) and two examples: `example.py`, a 2x2 grid of best-so-far step charts, and
`example_card.py`, Epoch's 4:5 social card (a log-log line with a scenario band, labelled points and
ranges). Copy `style.py`, `fonts/` and the closer example next to your script,
and start from the example.

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
| 16:9 cover | `canvas(width=WIDTH_WIDE, aspect=ASPECT_WIDE, ...)`: panels fill what the header leaves, a 1600 x 900 PNG; covers and artistic images only (see rule 9) |
| Logo markers | `logo(ax, x, y, path)`: an organisation's logo on a white disc at the point (see rule 10) |
| 4:5 card | `canvas(card=True, ...)`: 3.8 in at 4:5 on grey, a 1600 x 2000 PNG; one chart for a social post (see rule 9) |
| Point labels | `callout(ax, (dx, dy), target, [name, value], arrow=False, points=True, relpos=...)`: the label offset in points, a bare curved leader from where `relpos` says on its box to 4 pt short of the point; offsets clear any band |
| Log axes | `ax.set_xscale('log')`, ticks at 1, 3, 10, then `y_values(ax, ticks, fmt)` and `room(ax)`, which widens in log space |

## Rules

1. **Start minimal, add on request.** The first version has a title, one legend row, the series, and
   the axes. No value labels, callouts, end-of-line numbers, notes, reference or baseline lines, or
   shading until the owner asks, one at a time.
2. **The chart shows; the caption explains.** On the chart: the quantity and unit (`Throughput (MB/s)`),
   series names, each panel's identity. In the caption: the statistic (fastest of 5 runs), transforms
   (best so far), the workload, exclusions, caveats, and for a cost axis how the cost was counted (list
   prices; cached input at its discount or not). "Best MB/s so far, TinyLlama" is a caption written
   on an axis.
3. **The words are the owner's or the data's.** The title names what is plotted and never states a
   conclusion: `Vals Index cost-accuracy frontier`, not `Six models set the Vals Index cost-accuracy
   frontier`; `Throughput by setting`, not `Model A is fastest`. No count of winners, no verb of
   outcome, no comparative: what to take away goes in the caption. It is a plain noun phrase, the
   caption's bold lead: `The judge boundary`, never a roundabout sentence such as `What crosses the
   boundary and what stops at it` (the owner: "not how a person writes"). The wording is the owner's; until
   there is one, no title, or a draft that is called a draft. Axes use the data's own numbering
   (iterations 2 to 10, schemes 1 to 76, gaps kept). Renumber or relabel only on the owner's decision,
   and say so in the caption.
4. **The chart type follows the data.** A best-so-far chart is a step chart: the running maximum of
   what the run kept, never going down, changing at integer ticks, with a tick and grid line at every
   step so each corner sits on one. A Pareto frontier is the same running maximum taken over cost:
   sort by cost, step up at each optimal point, and run flat past the last one. Bars start at 0. A
   categorical axis has no grid lines. A quantity spanning orders of magnitude (compute, tokens,
   parameters) goes on a log axis with ticks at powers of ten; loss against compute is log-log, the
   scaling-law convention. When the claim rests on where runs end (each run's final loss), the
   trajectories are context: draw them faint (alpha about 0.15; the owner found 0.3 too strong) and mark each run's last point with a
   dot, legend swatch `'dot'`; the owner asked for this on learning curves whose endpoints were the
   comparison. When those endpoints run along an ordered variable (depth, size), draw a fitted curve
   through them, not straight segments (the owner), over their own range only, the fitted form in the
   docstring and caption (for loss against compute, L = E + A·C^-α); its own legend entry: that curve is
   the result. The curve describes the points, it is not a scaling claim: fit E freely and check the
   residual signs before showing it. Forcing an outside asymptote onto a form the points do not follow
   (residuals + at both ends, − in the middle) gives a line that misses them; the owner tried an
   anchored E, rejected the result and went back to the free fit. The endpoint dots all take that curve's one colour: a colour per dot repeats what the
   x position already says, so the ramp stays on the faint trajectories only (the owner: changing dot
   colours carry no information), and the legend names that line, not its
   members (the owner: "final loss by layer" is the entry; listing L1, L6 beside it adds nothing). A
   reference run then appears at the same granularity and only where it is matched: its own final
   point, nothing more. The owner tried the reference's final points across sizes joined into a line,
   then cut it back to the one same-size point. After dropping points, re-derive both ranges from what
   is left (rule 7). When many such curves converge at their ends, frame the endpoints: set the range
   from the spread of the final points with a little context above, and draw trajectories for every
   other member while keeping every final point (the owner: five curves read apart, eleven over a
   full-range axis "糊在一起", blurred together). Derive the view from the endpoints, never type it in
   per figure: x from the smallest final point's value / 4 to the largest × 2 on a log axis, y from just
   below the lowest final point (reference included) to about 15% above the highest; the early part of
   every trajectory is cut, which is the point ("we are serving the ends", the owner). Leave no tick
   value just under the top edge, where the panel name sits. Dots are solid fills with no white ring;
   the owner found the halo ugly.
5. **One face at Epoch's sizes.** Instrument Sans (SIL OFL, bundled) is the closest free face to Epoch's
   Messina Sans. The sizes were measured off Epoch's 2400 px exports scaled to 6.32 in, matched on the
   lowercase and on where titles break: title 12.2 pt semibold, subtitle 9.3, every other word 7.35,
   tick values 7. Weight tells the roles apart: the quantity and axis names medium, the rest regular.
   Charts that Epoch sets on its narrower web canvas take a title near 9.2 pt and ticks at text size.
   On a paper page with 10 pt body text, set the title near 10.5 pt (`title_pt=10.5`): 12.2 reads
   larger than a section heading there and 9.2 smaller than the body (the owner, 2026-10-03).
6. **Light grid, one axis, nothing touching.** Grid both ways on numeric axes, only the baseline axis,
   no tick marks: values sit just above their grid lines at the left edge, the quantity sits above
   each column, and panel names sit inside, top left, on white. Values are lifted off their lines, the
   x range runs past the last grid line, and headroom above the data holds the name. `ticks='left'` is
   Epoch's export form: values left of the panel on short tick marks.
7. **The y range starts where the data does.** 0 only when 0 is part of the comparison (shares, counts,
   latencies, bars); otherwise a round value just below the data. Round steps (1, 1.5, 2, 2.5, 3, 5 x
   10^k), 3 or more bands, each tall enough for the panel's name to clear the next value.
8. **Layout in inches, top down.** Title, legend row, quantity, panels and gaps are fixed distances
   measured off Epoch's exports, so every figure has the same rhythm. A standalone image (a post, a
   card, a slide) keeps 0.19 in clear at both sides and the top, since nothing else frames it. A paper
   figure has no white border: the page and the caption frame it, so `canvas(side=0)` puts the panels
   against both side edges and `save(fig, stem, flush=True)` cuts the top and bottom to the ink (the
   owner, 2026-10-03). The title spans the width between the margins at one size; a one-word last
   line warns, and the fix is to rephrase.
9. **Placement width, never cropped.** Draw at the width the figure is placed at and include it at
   natural size: `WIDTH_1COL` 5.5 in (NeurIPS, ICML, ICLR text width), `WIDTH_TEXT` 6.32 in (a
   one-column paper with narrower margins), `WIDTH_FULL` 7.6 in, `WIDTH_POST` 4.4 in for a post (a
   1600 px PNG). Never `bbox_inches='tight'`. A chart to be looked at as an image (a post, a chat, a
   slide, an animation) is `WIDTH_POST` with the web-canvas settings of rule 5, its height following
   its panels, unless the owner names a paper. Never force a data chart to 16:9: the owner tried it on
   a scatter and a 16:9 panel came out too short, the points crowded and the labels collided. 16:9
   (`canvas(width=WIDTH_WIDE, aspect=ASPECT_WIDE)`, 1600 x 900) is for a cover or a more artistic
   image, where the picture matters more than reading values. A chart posted as an image on its own
   (X, LinkedIn) can take the card: `canvas(card=True)` is Epoch's 1200 x 1500 export measured off
   the source, every size the web canvas's at 3.8 in, 0.30 in clear on all four sides, the legend
   wrapping into rows. The card is the chart alone: Epoch's footnote, sources and logo footer go in
   the post's text (the owner).
   Words or logos that read too small mean the canvas is too wide: narrow the canvas, never enlarge one
   kind of text on its own, so every size keeps its ratio to the others. At `WIDTH_POST` two columns of
   panels leave under 2 in each: category labels over about ten characters collide there, so stack the
   panels in one column instead.
10. **A colour means one thing, and every colour is Google's.** Every colour is a GM2 tone
    (`tone(hue, grade)`); none is computed. Neutrals come from the GM2 grey ramp.

    | Use | Colours |
    |---|---|
    | A compared pair; a third series | `BLUE`, `LIGHT` (blue 600, 300); `GREY` |
    | An ordered set, up to four series that stay apart | `family_4(hue)` (grades 300, 500, 700, 900) |
    | An ordered set of five or six whose lines cross, each read on its own | `STRONG` in order, then `GREY_900` |
    | A long ordered set where the order is the message (depth, size, step) | one hue ramped from grade 200 to 900; no legend entry per member |
    | Distinct categories: lines, points, small marks | `STRONG` (600) |
    | Distinct categories: bars | `MEDIUM` (400) |
    | Distinct categories: stacked areas, treemap cells | `SOFT` (300) |
    | Text set in a series' colour | `WORDS` (700) |

    Categories run blue, red, yellow, green, purple. GM2 cyan and pink are there for a pair that should
    stay off that order, as on the card (cyan 700 for open models, pink 600 for closed). The larger the inked area, the lighter the tone, as
    FiveThirtyEight and Datawrapper do. Yellow lines and words take 900, the only Google yellow at 3:1
    on white. Context behind a highlight steps down a set or goes grey, and stacked neighbours are split
    by thin white edges. Hold each series' colour across a piece; the legend names every colour.
    Shades of one hue only separate series that never touch: six blue grades for six layers whose
    curves overlap read as one band (the owner could not tell them apart), so order goes into the
    legend and the hues change. Past six the hues turn into noise instead (the owner, on eleven layers):
    when the reader needs the trend across the set rather than any one member, ramp one hue light to
    dark (`LinearSegmentedColormap` between `tone(hue, 200)` and `tone(hue, 900)`, the one place a tone
    is interpolated). The legend names what the reader compares (the line joining the members' final
    points, the reference), never each member. Never write series names on the chart instead (rule
    1): the owner rejected name labels at curve ends as clutter, twice.

    A line style means something too. A baseline run is a series like the others: solid, told apart
    by its colour (grey). Dashes mark a different kind of quantity (an extrapolation, a projection, a
    bound), never "this one is the baseline".

    Logos are the one exception to GM2. The few points a chart is about (the Pareto-optimal models,
    the method a post introduces) may be drawn as their organisation's logo at the data point with
    `logo()`: a white disc ringed in the series' colour hides the lines behind it, the logo is sized by
    its visible ink, and the name sits beside it. Every other point stays a dot, drawn above the discs
    so a close neighbour is never hidden. Logos come from vector sources (lobehub
    `@lobehub/icons-static-png`, simple-icons filled with its brand hex), never cropped from a
    screenshot.
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
