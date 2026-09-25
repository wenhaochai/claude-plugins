---
name: talk-slides
description: "Build, revise and audit a talk deck as a claude.ai Slides artifact: a paper presentation, a benchmark survey, reading-group or group-meeting slides. Carries the author's rules for the slides and for the spoken script in the notes, layout builders with a template, a static lint and a render audit in the Slides runtime. Use when the user asks for slides, a deck, a talk or a paper presentation, or says 做 slides, 讲论文, 组会汇报, 写讲稿, 改一下这页, 审计 slides."
---

# Talk slides

The Slides artifact type's own instructions cover the file format and the Artifact calls. This skill adds the author's rules, the layout builders and two checks.

## Workflow

1. Agree on the parts first, one idea per slide. Put open choices to the user as short multiple-choice questions, and cite only the sources the user names.
2. Take every number from a primary source, keep the raw files next to the deck and recompute what you plot. Re-fetch live leaderboards on the day you publish and put the read date in the source line.
3. `python3 scripts/build_template.py OUT` writes one example slide per layout. Build slides with the builders in `scripts/deckkit.py` and replace every bracketed string and example number.
4. Before each publish, run `python3 scripts/lint.py DECK_DIR` and `python3 scripts/audit_render.py RUNTIME_DIR`; the audit's docstring says how to set up RUNTIME_DIR. Look at every screenshot and check each chart against its source.
5. Read the live deck before publishing so edits made in the page survive, then send only the changed files.
6. Report in a few Chinese lines: the version, the link and what changed on which slide.

## Slides

- Titles, slide and chart alike, are noun labels for what is shown and make no claim; none is a comma-joined list of clipped phrases. A title the user gives stays as given. The eyebrow names the part.
- The slide holds labels, numbers and at most one short sentence per block; the rest goes into the notes. Wording stays plain, without the "X, not Y" pattern, em dashes or the word campaign.
- Type is restrained and the same on every slide. The serif sets only titles (56, weight 500), the cover and end (120) and standalone big numbers (56, regular). Everything else is the sans: 36 for the one lead sentence of a paper slide, 28 for body text, table cells and panel headings, 24 for eyebrows, column headers, labels, captions and sources. Semibold marks headings only: the eyebrow, panel headings, column and group headers. Values, labels and sentences stay regular; emphasis is the accent color, and nothing is italic. An animation's canvas text keeps the same sizes and weights. The lint flags type off this scale.
- Data goes in charts, and so do concepts and mechanisms such as how a score is built: a chart, a pipeline or a worked example beats rows of labels and sentences. Each headline number sits beside the figure that produced it. A source's official figure is used as is.
- Every mark carries data. Leave out decorative icons, big numerals with no quantity behind them, invented examples, side facts such as cost or release counts, one model's numbers shown alone, and categories with fuzzy or unclear edges.
- Signed values are drawn as magnitudes with the two directions labelled at the ends; the source's sign convention goes in the notes.
- A paper takes three slides: its first page with the question, one method figure, one comparison figure.
- One slide per method, index or example. The first slide of a new topic says what it is and how it works, with one real example.
- An index slide shows its composition and principles; strengths and weaknesses go in the notes.
- An animation the user asks for is one continuous scene in an `<x-embed>`: a canvas drawn as a function of time, each phase as long as the note lines said over it. Click builds only reveal parts of a still slide.
- A leaderboard shows the top five with the uncertainty the source publishes, and its title names the interval.
- The cover states title, author and date. The agenda lists the parts, and the summary gives one point per part and a closing line.

## Speaker notes

The notes are the script the speaker reads aloud, sentence by sentence: each English line is followed by its Chinese line, and a blank line separates the pairs.

- The speaker reads the English in a second language: one sentence per line, at most 18 words, common words.
- Leave out names the speaker may not know how to say. Say "the author" or "one model", and keep only the names the audience needs, such as the leaders on a leaderboard.
- About a minute per slide: first what the slide shows, then one strength and one problem, in the author's words when the author gave them.
- The script does not read the slide's numbers out. It says in words what they show, and keeps a number only when that number is the point, said as printed.
- A slide with builds marks each click in the notes: `[click] ` starts the English line said as that build appears, one mark per build order, so the script and the builds keep the same timeline. The lint counts them.

## Runtime

- A raw newline in `<aside>` becomes a space. `deckkit.aside` writes each line break as `<br>`.
- An empty `<div>` with only a width is dropped together with its gap. Offset with pinned children inside a sized `position:relative` host.
- `audit_render.py` reports the rest: shrunk text, overflow, text outside the margins and overlaps.
- The runtime creates an `<x-embed>` iframe when its slide is shown and drops it when the slide is left, so an animation starts over on each visit; hold its first frame about a second for the slide transition. The embed stays under 16 KB, its script has no `&` and no `<` before a letter, and print shows a placeholder, so check the animation's frames on a page of their own. The lint does not read inside an embed.
