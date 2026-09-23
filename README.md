# claude-plugins

Personal Claude Code plugin marketplace by [Wenhao Chai](https://wenhaochai.com).

## `writing` — publication-prep tools

Four skills, all auto-loading by context match. One shared figure design system under
`writing/figures/`.

### `style` — default English-prose standards

Auto-triggers on any writing task the user will send or publish: emails, message drafts, posts, docs,
grant proposals, paper prose. 17 canonical English-prose rules apply everywhere. RULE-01 to RULE-12
are distilled from Strunk & White, Orwell, Pinker, and Gopen & Swan, sourced from
[agent-style](https://github.com/yzhao062/agent-style) under CC BY 4.0; RULE-13 to RULE-17 are added.
20 page-cap additions and 2 final-pass audit rules apply only to a page-capped conference paper.

### `preflight` — mechanical pre-submission checks

```bash
python3 writing/skills/preflight/preflight.py <paper-dir> --venue iclr
```

Six deterministic checks: `latexmk` compile gate, page count against the venue cap, build-log scan for
undefined citations and overfull boxes, leftover placeholders and `\textcolor{red}` marks,
correspondence-problem density per file, and `.bib` hygiene. Exit status 1 on any failure, so it chains
into a larger gate.

### `plot` — matplotlib chart templates

18 drop-in templates: grouped and highlighted bars, boxplots, curve grids, broken axes, IsoFLOPs and
labelled-frontier scatter, quadrant plots, stacked share areas, alluvial ribbons, and sparse-group
DAGs. Every one carries the same header: a left-aligned Lato Heavy title with one Lato Regular legend
row above the axes, never inside them, spaced by measurement rather than by eye. Labels ship
pre-genericized; replace them before saving.

### `concept` — matplotlib schematics

Diagrams with no data axes: node flows, boundary and contract diagrams, jigsaw treemaps. Lato type, a
fixed five-size scale, colour that encodes which side a node belongs to, and an overflow check that
raises rather than being eyeballed.

### `writing/figures/` — the shared design system

`style.py` (Google palette, venue-matched serif, the `header` / `fig_header` / `finalize_headers`
contract, measured spacing), `concept.py` (the five-size scale and the overflow check), `jigsaw.py`
(squarified treemap), and `DOCTRINE.md`, the eleven rules every figure in this plugin follows.

## `anti-autoresearch` — integrity forensics for paper output

Adversarial self-audit gate: `/anti-autoresearch <paper-dir>` builds a span-anchored evidence ledger,
fans out 11 auditor skills (consistency, citation, baseline, experiment, eval design, proof and
derivation, presentation, AI-style impressions, adversarial case, novelty advisory), and hands every
finding to a deterministic adjudicator. Loop: draft, audit, fix each verdict-bearing finding, re-run
until `CLEAN_GIVEN_EVIDENCE`. `reviewer-discipline` is the write-up side: the six CVPR reviewer errors,
nine phrasings a review must never contain, the ARR specificity rewrite, and the COLM and TMLR guards.

Vendored from [wanshuiyin/Anti-Autoresearch](https://github.com/wanshuiyin/Anti-Autoresearch) (MIT);
tools, references, schemas, and eval live under `anti-autoresearch/support/`, see its README for the
two local path patches.

## `kexue-fm` — offline library of kexue.fm

A SQLite snapshot of every post on [科学空间](https://kexue.fm/) (Su Jianlin's blog, 2009 to the last
sync): full text as Markdown with LaTeX intact, tags, and the site's official citation. One script and
one `kexue` skill on top:

```bash
python3 kexue-fm/scripts/kexue.py search Muon MuP 学习率 --since 2023-01-01
python3 kexue-fm/scripts/kexue.py show 8265
python3 kexue-fm/scripts/kexue.py sync
```

Each `search` argument is a separate query; results from all queries merge by reciprocal rank fusion.
Skill and docs are in Chinese. Post content is © 苏剑林 under CC BY-NC-SA; the snapshot is for personal
study and retrieval.

## `training-monitor` — reading a pretraining run

One text skill, no code. It restates Chunyuan Deng's ["Reading a Pretraining Run"](https://charlesdddd.github.io/blog/reading-a-pretraining-run.html) (2026)
as doctrine an agent can apply to any training stack: the nine first-screen signals, the full
metric table with cadence and priority (P0 every step, P1 every 100 steps, P2 on demand), the
formulas, the cross-rank reduction rules, a robust spike detector, the fixed triage order, and
the common mistakes. The agent inventories what its stack already logs, fills the P0 gaps first,
sets thresholds from healthy runs, and decides for itself whether a script is warranted.

## `talk-slides` — talk decks as claude.ai Slides artifacts

One skill for building, revising and auditing a talk deck in the claude.ai Slides artifact
format: a paper presentation, a survey of benchmarks, reading-group slides. It carries the
author's slide rules, distilled from one talk revised over 28 versions: noun titles, charts over
tables, little text on the slide with the detail in a spoken Chinese and English script, no
decorative visuals, official figures, and live numbers re-fetched on publish day. `deckkit.py`
holds the design and the layout builders; `build_template.py` writes a 14-slide template from them.

```bash
python3 talk-slides/skills/talk-slides/scripts/build_template.py OUT
python3 talk-slides/skills/talk-slides/scripts/lint.py DECK_DIR
python3 talk-slides/skills/talk-slides/scripts/audit_render.py RUNTIME_DIR --out shots
```

`lint.py` checks the file contract, the subset limits and the speaker-notes script.
`audit_render.py` renders every slide in the Slides runtime with headless Chrome and reports
shrunk text, overflow, margin breaks and overlapping labels, which a plain browser preview does
not show.

## Install

```
/plugin marketplace add wenhaochai/claude-plugins
/plugin install writing@wenhaochai
/plugin install anti-autoresearch@wenhaochai
/plugin install kexue-fm@wenhaochai
/plugin install training-monitor@wenhaochai
/plugin install talk-slides@wenhaochai
```

Upgrading from `writing` 1.x: the 12 integrity-forensics skills moved out of `writing` into the new
`anti-autoresearch` plugin, so install that one too to keep them. `review` and the `paper-overleaf`
agent were removed; their mechanical checks became `preflight` and their venue norms became
`reviewer-discipline`.

## License

MIT for plugin code. `writing/skills/style/SKILL.md` redistributes rules from
[agent-style](https://github.com/yzhao062/agent-style) under CC BY 4.0, attribution preserved in that
file. `anti-autoresearch/support/` carries its upstream MIT license in `LICENSE.upstream`.
`kexue-fm/data/kexue.sqlite` holds third-party content under CC BY-NC-SA.
