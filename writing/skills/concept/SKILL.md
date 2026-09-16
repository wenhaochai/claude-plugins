---
name: concept
description: "Schematic figures drawn in matplotlib with no data axes: pipeline and node-flow diagrams, boundary or contract diagrams showing what crosses and what is blocked, jigsaw treemaps of a dataset's composition, teaser triptychs, and timelines. Lato type, a fixed five-size scale, colour that says which side a node belongs to, and an overflow check that raises. Use for a teaser or method figure that explains a mechanism. Charts with real data axes go to `plot`; figures drawn in LaTeX go to `tikz`."
---

# Concept

Schematics rather than charts: no axes, no data series, no fitted curves. They use `concept.py`
instead of `apply_style()`, and `52_*` also uses `jigsaw.py`.

Read `${CLAUDE_PLUGIN_ROOT}/figures/DOCTRINE.md` first. Rules 4, 5, 6, and 8 do most of the work here:
colour means which side a node belongs to, five type sizes and no sixth, geometry carries the relation,
and overflow raises rather than being eyeballed.

## What is different from a chart

- **Faces.** Lato Heavy for the headline and titles, Lato Regular for everything else, the two faces of
  the arxiv template's section titles. `concept.py` registers them from TeX Live, `~/texmf` or the
  system tree, and falls back to DejaVu Sans. Five sizes only: `H1 11 / H2 8.5 / H3 7.5 / BODY 7 /
  META 6.5`.
- **Colour says whose side.** `BLUE_FILL` is the agent's side, `RED_FILL` is what is withheld from it,
  `PALE` is neither, and connectors are always grey open-V arrows because an arrow is a relation rather
  than a party. A node title sits in a tinted band carrying the panel letter, so no text floats above
  the blocks.
- **One gap.** `height_for(content_top)` and `headline_y(height)` seat the headline `TITLE_GAP` above
  the first block; `half_for(size)` gives a text line's half-height so a legend or heading row stacks
  with the same gap. Never hand-tune a vertical offset.
- **Overflow raises.** Every template ends with `C.check(fig)`, which raises when text leaves the
  canvas or runs past the panel it starts in. Widen a node or shorten a label. `C.save(fig, stem)`
  runs the check and writes `stem.pdf`, `.svg`, and `.png` without tight cropping.

## Templates

| File | Type | Use when |
|---|---|---|
| `50_concept_node_flow.py` | Titled nodes joined by arrows, one row | An artifact is taken apart into the pieces a task needs; any 3 to 4 stage pipeline |
| `51_concept_boundary.py` | Two parties, arrows that cross or stop at a boundary | A contract or sandbox: what passes through, what is blocked or withheld |
| `52_concept_jigsaw_treemap.py` | Two jigsaw treemaps sharing one key | Composition of two related benchmarks or datasets by category, sized by count |

`jigsaw.py` lays out a two-level squarified treemap, areas then domains, as jigsaw pieces: knobs go
only on seams longer than `MIN_SEAM`, radii shrink with piece size, and a label that does not fit falls
back through wrapped, inline, rotated, and name-only forms, printing a warning on the last.

## Quick start

1. Copy `${CLAUDE_PLUGIN_ROOT}/figures/style.py`, `concept.py`, and the chosen template into your
   figures directory. `52_*` also needs `jigsaw.py`.
2. Replace the node labels and the composition data.
3. Run it. `C.save(fig, stem)` writes all three formats and raises on overflow.

## Dependencies

`matplotlib >= 3.6`, `numpy >= 1.20`, and TeX Live's `lato` package for the real faces. `concept.py`
falls back to DejaVu Sans when Lato is absent, which changes the metrics, so check the output before
shipping a figure rendered without it.
