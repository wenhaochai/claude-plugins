# claude-plugins

Personal Claude Code plugin marketplace by [Wenhao Chai](https://wenhaochai.com).

## `writing` — publication-prep tools

Three skills, all auto-loading by context match.

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

### `plot` — one chart style for posts and papers

`style.py` and one worked example. The look follows Epoch AI's charts: Instrument Sans (bundled, SIL
OFL), a light grid in both directions, only the baseline axis, values sitting just above their grid
lines, the quantity above each column, panel names inside the panels, the Google palette, and a layout
set in inches so every figure has the same rhythm. `SKILL.md` holds the twelve rules, starting with
"minimal first": no labels, notes, or reference lines until the owner asks for them.

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

## `presentation` — talk decks and explainer videos

Two skills. `talk-slides` builds, revises and audits a talk deck in the claude.ai Slides artifact
format: the author's rules for the slides and the spoken script, layout builders with a template, a
static lint, and a render audit in the Slides runtime. `video` makes a short explainer video of a
page from its own animations and data: the author's design rules for motion pieces, a director
workflow, and a frame sink that collects the frames for ffmpeg.

```bash
python3 presentation/skills/talk-slides/scripts/build_template.py OUT
python3 presentation/skills/talk-slides/scripts/lint.py DECK_DIR
python3 presentation/skills/talk-slides/scripts/audit_render.py RUNTIME_DIR --out shots
python3 presentation/skills/video/scripts/frame_sink.py FRAMES_DIR DIRECTOR_DIR
```

## Install

```
/plugin marketplace add wenhaochai/claude-plugins
/plugin install writing@wenhaochai
/plugin install anti-autoresearch@wenhaochai
/plugin install kexue-fm@wenhaochai
/plugin install training-monitor@wenhaochai
/plugin install presentation@wenhaochai
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
