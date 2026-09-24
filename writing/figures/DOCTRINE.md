# Figure doctrine

Eleven rules that hold for every figure in this plugin: charts from `skills/plot` and schematics from
`skills/concept`. `style.py` and `concept.py` encode most of them; the rest are decisions no module
can make for you.

## 1. The canvas is the text width, and the figure goes in at 1:1

A single-column figure is 5.5 in wide, which is `\linewidth` for the arxiv and ICLR templates. Insert
it with `width=\linewidth` and no scale factor, so a point inside the figure is a point on the page.

**Never tight-crop.** `bbox_inches='tight'` changes the canvas size, which changes the scale factor
LaTeX applies, which changes the effective font size of everything in the figure. A set of figures
saved with tight crop cannot be made typographically consistent. `concept.save()` already refuses to.

## 2. Figure text matches the body text of the venue

The page loads one serif face; the figure uses the same one, or the figure reads as a foreign object.
`apply_style(venue='arxiv')` gives Palatino through TeX Gyre Pagella, matching `mathpazo`.
`apply_style(venue='iclr')` gives Times through TeX Gyre Termes, matching `\usepackage{times}`.
matplotlib bundles neither face, so without registration both fall back to DejaVu Serif silently.

Schematics are the exception: they use Lato Heavy for titles and Lato Regular for everything else,
which is the section-title face of the arxiv template. Sans in a schematic, serif in a chart.

## 3. One header format, everywhere

Every chart carries a left-aligned Lato Heavy title and, under it, one Lato
Regular legend row above the axes. `header(ax, title, entries)` writes both,
`fig_header(fig, title, entries)` does it once for a panel grid, and
`finalize_headers(fig)` measures the real heights so the gap above the legend row
equals the gap below it, on every figure, at any font size.

Nothing goes inside the axes. A legend box sits on the data, and moving it to
dodge a curve makes two figures in one document disagree. A title never carries a
panel letter; captions say Left, Middle, Right. When a handful of points carry
the argument, `note(ax, x, y, text)` names them in place, because a direct label
beats a legend entry the reader has to match by colour.

A schematic has no axes to sit above, so it places the same headline face at the
same size at the top left of its canvas and stops there.

## 4. Every figure in one document shares one geometry

Same width, same height where the figures sit side by side, node top and bottom edges aligned across
panels, one type scale. Two figures on facing pages that differ by 0.1 in of height read as a mistake
even when the reader cannot say why. Set the numbers once in a shared module and import them.

## 5. A colour means one thing, and the label says it too

Pick what colour encodes before drawing, and hold it for the whole document. In the concept diagrams
it encodes which side a node belongs to: blue is what the agent holds, red is what is withheld from
it, grey is neither, and connectors are always grey because an arrow is a relation rather than a
party. In charts it encodes the series.

Whatever the rule is, the text labels must carry the same information on their own, because a reader
who cannot separate the hues still has to be able to read the figure.

## 6. Five type sizes, no sixth

`H1 11 / H2 8.5 / H3 7.5 / BODY 7 / META 6.5` in `concept.py`, and the chart band in `style.py`.
Three heavy levels separate by size, two regular levels separate by size and colour. Wanting a sixth
level means the figure is saying too much: cut content instead of adding a size.

## 7. Geometry carries the relation, not the legend

A containment relation is a rectangle drawn inside another rectangle at the same width and height.
A protocol difference is a one-way arrow against a loop. A funnel is segments that visibly shrink.
Reach for a legend only when geometry cannot say it, and a figure that needs a legend to explain what
its shapes mean is a figure that has not been designed yet.

A legend that stays is one short row of names, one per mark the reader must match. Definitions,
formulas and reading instructions, such as `δ: improvement over its parent` or `∝ exp(β·δ)`, go in the
caption or the text, never in the legend. Five entries of mixed prose is a legend to delete.

## 8. The docstring states what the figure claims and where the numbers came from

Every figure script opens with: what the figure shows, the data source by file path or run id, the
formula behind any derived quantity, and the output path with its width. A figure with no measured
data says so in the first line, in the words `contains no measured results`, and repeats it in the
caption. A reader should never have to guess whether a curve was fitted or drawn.

## 9. Overflow raises, it is not eyeballed

`concept.check()` raises when text leaves the canvas or runs past the panel it started in, and
`concept.save()` calls it. Changing a label or a font quietly widens text, so the check is the only
thing standing between a rewording and a figure that overlaps in the PDF. Widen the node or shorten
the label; never disable the check.

## 10. A restyle never touches data

A styling pass changes colours, legends, fonts, and spacing. It does not touch data loading, fits,
tick semantics, or panel content. After restyling a figure with computed values, diff the numbers
against the pre-restyle run.

## 11. Look at the output

Render, then open the file. Measured header spacing, raised overflow checks, and a smoke test all
catch different things, and none of them catches a figure that is technically correct and unreadable.

## Captions, notation, tables

A caption stands alone: what is plotted, what the axes are, what the reader should take away, in that
order, with a bold caption title. Group subfigures explicitly rather than trusting the reader to pair
them with the prose. Ask of every figure whether it earns its column inches, and of every panel
whether it carries one message.

These are RULE-P13, RULE-P18, and RULE-P19 of the `style` skill, which is where the prose side of the
same rules lives.
