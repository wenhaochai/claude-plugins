# claude-plugins

Personal Claude Code plugin marketplace by [Wenhao Chai](https://wenhaochai.com).

## `writing` — publication-prep tools

Skills auto-load by context match; the only slash command is `/anti-autoresearch`.

### `style` — default English-prose standards

Auto-triggers on any writing task the user will send or publish: emails, message drafts, posts, docs, grant proposals, paper prose. 17 canonical English-prose rules apply everywhere (RULE-01..12 distilled from Strunk & White / Orwell / Pinker / Gopen & Swan, sourced from [agent-style](https://github.com/yzhao062/agent-style) under CC BY 4.0; RULE-13..17 added). 18 page-cap additions (RULE-P1..P18) plus 2 final-pass audit rules (RULE-A1..A2) apply only when the target is a page-capped conference paper.

### `plot` — matplotlib templates for paper figures

Drop-in templates for publication-quality figures: vertical / horizontal bar, horizontal boxplot with family gradient, multi-line on linear / broken / log-x / log-log axes, log-log power-law fit, IsoFLOPs-style scatter, concept diagrams. Each template is one .py file producing one subplot. Shared `style.py` sets Palatino body + STIX math (matching arxiv `mathpazo`) and a Google-brand palette softened to a paper-friendly tier. Labels ship pre-genericized (`Model A`, `Metric A`, `Task A`); replace with real names when applying.

Template dir: `writing/skills/plot/`. Copy the chosen template plus `style.py` to your figures directory, edit the data block, add a `fig.savefig(...)` call, run.

### `review` — pre-submission AI/ML paper self-review

Auto-triggers when reviewing own Overleaf drafts for top-tier ML venue submissions (NeurIPS, ICML, ICLR, etc.). Simulates reviewer feedback on clarity, novelty, experimental rigor, presentation, and standards compliance. Default-loads `style` for clarity-rule citations.

### `paper-overleaf` — Overleaf-synced LaTeX editing agent

Opus subagent for section-level paper editing: venue conventions for NeurIPS / ICML / ICLR / COLM, red-mark workflow with `\textcolor{red}`, bilingual zh/en side-by-side review, and claim / number / citation audits against the codebase.

### `anti-autoresearch` — integrity forensics for paper output

Adversarial self-audit gate: `/anti-autoresearch <paper-dir>` builds a span-anchored evidence ledger, fans out 11 auditor skills (consistency, citation, baseline, experiment, eval design, proof / derivation, presentation, AI-style impressions, adversarial case, novelty advisory), and hands every finding to a deterministic adjudicator. Loop: draft, audit, fix each verdict-bearing finding, re-run until `CLEAN_GIVEN_EVIDENCE`. Vendored from [wanshuiyin/Anti-Autoresearch](https://github.com/wanshuiyin/Anti-Autoresearch) (MIT); tools, references, schemas, and eval live under `writing/anti-autoresearch/`, see its README for the path patch.

## `kexue-fm` — offline library of kexue.fm

A SQLite snapshot of every post on [科学空间](https://kexue.fm/) (Su Jianlin's blog, 2009 to the last sync): full text as Markdown with LaTeX intact, tags, and the site's official citation. One script and one `kexue` skill on top:

```bash
python3 kexue-fm/scripts/kexue.py search Muon MuP 学习率 --since 2023-01-01
python3 kexue-fm/scripts/kexue.py show 8265
python3 kexue-fm/scripts/kexue.py sync
```

Each `search` argument is a separate query; results from all queries merge by reciprocal rank fusion. Skill and docs are in Chinese. Post content is © 苏剑林 under CC BY-NC-SA; the snapshot is for personal study and retrieval.

## Install

```
/plugin marketplace add wenhaochai/claude-plugins
/plugin install writing@wenhaochai
/plugin install kexue-fm@wenhaochai
```

## License

MIT for plugin code. `writing/skills/style/SKILL.md` redistributes rules from [agent-style](https://github.com/yzhao062/agent-style) under CC BY 4.0, attribution preserved in that file. `writing/anti-autoresearch/` carries its upstream MIT license in `LICENSE.upstream`. `kexue-fm/data/kexue.sqlite` holds third-party content under CC BY-NC-SA.
