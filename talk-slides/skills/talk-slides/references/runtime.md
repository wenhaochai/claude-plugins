# Slides runtime notes

The Slides runtime renders a slide from its HTML with its own layout pass. A slide that looks right in a plain browser can shift, clamp or shrink there, so every check runs in the runtime itself.

## Local audit setup

1. Read the runtime files from the deck with the Artifact tool, using a read with `paths`: `index.html`, `artifact-type/app.js` and `artifact-type/app.css`. Save them in one folder, for example `rt/`, keeping `artifact-type/` as a subfolder.
2. Put the deck beside them: `rt/project` is the deck's `project` folder or a symlink to it.
3. Copy every uploaded image the slides reference as `/_blob/<id>` to `rt/_blob/<id>`. The originals you uploaded work; so does a read of the asset by its id.
4. Run `python3 scripts/audit_render.py rt [slide ids] --out shots`. The script writes `rt/_files.json`, serves `rt` on a free local port, opens each slide from the runtime's hidden print sheet in headless Chrome, saves `shots/<id>.png`, and writes the measurements to `shots/audit.json`.
5. The script expects Chrome at the macOS default path. Pass `--chrome PATH` or set `CHROME` elsewhere.

The runtime files belong to the Slides type. Keep them out of any repository.

## Behaviors and fixes

| Symptom in the runtime | Cause | Fix |
|---|---|---|
| A row of titles or legends sits one column to the left | An empty `<div>` with only a width is dropped, and its gap with it | Pin the offset children inside a sized `position:relative` host, or paint the spacer, or use a `flex:1` spacer |
| A tick label sits lower than its tick | A negative `left` or `top` is clamped to 0 | Move the plot inside its host by half a label height; `scatter` and `curves` do this |
| Text a few percent smaller than declared, such as 23.925px | The column is overfull and the runtime scales its text down | Cut text or tighten gaps until the audit reports the declared sizes only |
| Rows taller than the estimate | `align-items:baseline` lines a 56px numeral up with 24px text and adds about 16px per row | Measure the real heights in `audit.json` and budget with them |
| ρ shows as Ρ | `text-transform:uppercase` also uppercases Greek letters | Keep Greek letters out of uppercase labels |
| Chart labels in the wrong font or clipped | Fonts never load inside an SVG | Draw marks in the SVG and pin the labels as `<p>` over it |
| The build refuses a host | More than 24 pinned children in one `div` | Split the chart into one host per row |
| Two adjacent label columns read as one line | Column texts run to the column edge | Give each column's text a right padding, as `seg_bar` does |
| The speaker notes show as one paragraph | The runtime reads `<aside>` like HTML text, so a raw newline becomes a space | Write each line break as `<br>` and two for a blank line; `deckkit.aside` does this and `lint.py` warns on raw line breaks. To see the notes as parsed, open the page, press the Speaker notes button and read the notes box; the edit view opens on the first slide, so put the slide first in a scratch copy of `deck.json` |

## Height budget

The canvas is 1920 by 1080 with 128px margins. A slide with a pinned source line uses `padding:128px 128px 160px`, which leaves 792px of content height; without one it uses 128px all round and leaves 824px.

- Header: eyebrow 34px, gap 12px, one-line title 62px, so 108px in total.
- Body: 792 − 108 − gap on a slide with a source line, which gives 644px at a 40px gap and 652px at 32px.
- Line heights: 24px text takes 34px at line-height 1.4 and 31px at 1.3; 28px takes about 39px; a numeral at line-height 1 takes its font size.
- The source line is pinned at `bottom:64px` and grows upward, so keep it to one line.

Keep 20px or more of slack below the last block. The runtime measures real glyphs, and a slide that fits by 3px in an estimate may shrink.

## Width

- Inter Tight at 24px averages about 11.5px per character, 12.5px in semibold. Newsreader at 56px averages about 24px.
- A box narrower than its longest word breaks the word in the middle. Size fixed-width label columns to the longest name you will show.
- `white-space:nowrap` keeps a name on one line but lets it run past a narrow box, and the audit reports that as overflow.

## Labels inside charts

- Before placing a curve label, compute the curve's height at the label's left and right edges and keep the label at least 10px clear of every curve.
- Size each axis caption box to its text. Neighbouring captions whose boxes overlap show up as an audit finding even when the glyphs do not touch.

## Publishing

- Read the live deck and diff it against your copy before each publish; the person may have edited slides in the page.
- Publish only the changed slide files. Send `project/deck.json` only when the order, the sections or the title change.
- When a publish is refused because the page saved in between, read the files again, redo the edit on them, and publish once more.
- Upload images as assets and reference the returned `/_blob/<id>` in `src`. Until the file exists, an `<img>` with `alt` and a size and no `src` holds its place.
