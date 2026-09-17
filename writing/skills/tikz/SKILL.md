---
name: tikz
description: "Figures drawn in LaTeX with TikZ and pgfplots: standalone teaser flows, inline box-and-arrow pipelines, and charts that typeset in the document's own font. Google palette, build recipe, and the convention of recording a figure's geometry in prose so a reader can reproduce it. Use when the figure should share the page's fonts and macros, or when the user is editing a `.tex` figure. Data charts rendered to PDF go to `plot`; matplotlib schematics go to `concept`."
---

# TikZ

A figure drawn in LaTeX typesets in the document's own font and macros, so it never drifts from the
page the way an imported PDF does. That is the reason to reach for it, and the cost is that layout is
hand-placed: every coordinate is a decision you make rather than one a layout engine makes for you.

Read `${CLAUDE_PLUGIN_ROOT}/figures/DOCTRINE.md` first. Rules 1, 5, and 7 apply unchanged: the canvas
is the text width, a colour means one thing, and geometry carries the relation.

## Which tool draws this figure

| Draw it in TikZ when | Draw it in matplotlib when |
|---|---|
| The figure is mostly type, and must match the body font exactly | The figure is mostly data |
| It uses the paper's own macros, such as a method name command | The layout depends on values you compute |
| The shapes are few and placed by hand | Panels, ticks, and legends need measuring |
| It ships inside the `.tex` and a co-author will edit it | It is regenerated whenever the data changes |

A chart with real axes drawn in pgfplots sits between the two: it typesets in the document's font,
which is worth a lot for a small chart, and it becomes unmanageable past a few hundred data points.
Generate the `.tex` from data with a script rather than hand-writing coordinate lists.

## Two shapes of source file

A **standalone** figure is its own document, built to a PDF that the paper includes. Keep it under
`figures/src/`, build it into a scratch directory, and place the result at 1:1.

An **inline** figure is a `\begin{figure}` body that the paper `\input`s, so it inherits the document's
preamble. List the packages and `\definecolor` lines it needs in a header comment, because a figure
that silently depends on the host preamble breaks the first time it is reused.

## Build recipe for a standalone figure

```sh
mkdir -p /tmp/teaser-build
pdflatex -interaction=nonstopmode -halt-on-error \
         -output-directory=/tmp/teaser-build figures/src/teaser.tex
cp /tmp/teaser-build/teaser.pdf figures/teaser.pdf
pdftoppm -scale-to 2100 -png -singlefile figures/teaser.pdf figures/teaser
```

Build into a scratch directory so the auxiliary files never land in the paper tree, keep the `.tex`
under `figures/src/`, and place the result with `width=\linewidth` and no scale factor.

## Conventions

**Write the geometry down.** A TikZ figure hides its reasoning in coordinates, so a companion README
next to the source states the numbers behind anything a reader might take as measured: the vectors an
inset draws, the ratios between them, the threshold a circle represents, the scale in cm per unit. A
figure with no measured data says `contains no measured results` in both the source header and the
caption. This is DOCTRINE rule 8 for a figure with no docstring to put it in.

**One palette block at the top.** Define the colours once with `\definecolor` and name them for their
role, `ink`, `soft`, `faint`, and one name per party. Never write a hex value inline. The values match
`figures/style.py`, so a TikZ figure and a matplotlib figure in the same paper agree.

**One tikzset block.** Every repeated appearance becomes a named style: `flow`, `note`, `box`, `label`.
A `\draw` carrying five inline options is a style that has not been named yet. `out` is reserved by
TikZ itself, so name an output style something else.

**Macros for repeated glyph groups.** A row of small marks, a stack of tokens, or a repeated node
pattern becomes a `\newcommand` driven by `\foreach`, which keeps the spacing identical across rows
and makes a change one edit rather than twenty.

**Fix the bounding box.** `\path[use as bounding box] (0,0) rectangle (w,h);` on the first line of the
picture pins the canvas, so adding an annotation near the edge shifts nothing else.

**`y=-1cm` when the figure reads downward.** Setting `[x=1cm,y=-1cm]` puts the origin at the top left
and makes every coordinate read the way the figure does.

## Compile before you ship

A TikZ figure that does not compile is invisible until the whole paper breaks. Build it standalone,
render the PNG, and look at it. The failures this catches are overlapping nodes, an arrow that points
at the wrong anchor because two boxes overlap, and a label that hyphenates inside a narrow node.
