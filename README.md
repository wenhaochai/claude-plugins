# claude-plugins

Personal Claude Code plugin marketplace by [Wenhao Chai](https://wenhaochai.com).

## `daily` — personal daily tools

Single plugin bundling the commands I use every day.

| Command | What it does |
|---|---|
| `/daily:todo` | Show actionable items from `./TODO.md`; add / complete / delete / update items via natural language (e.g. `/daily:todo 加一条 修车`) |
| `/daily:todo-sync` | Two-way sync between `./TODO.md` and Apple Reminders (`Quick` / `Long` lists) |
| `/daily:email` | Summarize recent unread Gmail messages, filtering out promotions / security alerts / noise (requires a Gmail MCP) |
| `/daily:wrap` | Summarize the current conversation and append to `./memory/YYYY-MM-DD.md` |

## `writing` — publication-prep tools

Two skills bundled together. Both auto-load by context match; no slash commands.

### `writing-style` — default English-prose standards

Auto-triggers on any writing task the user will send or publish — emails, message drafts, posts, docs, grant proposals, paper prose. 13 canonical rules (Strunk & White / Orwell / Pinker / Gopen & Swan, sourced from [agent-style](https://github.com/yzhao062/agent-style) under CC BY 4.0) apply everywhere. 6 additional rules (no em-dashes or prose parens, no overview paragraphs, minimal `\emph`/`\textbf`, researcher voice, space economy, no blank lines inside `\paragraph{}`, equation symbol audit) apply only when the target is a page-capped conference paper.

### `plot` — matplotlib templates for paper figures

Drop-in templates for publication-quality figures: vertical / horizontal bar, horizontal boxplot with family gradient, multi-line on linear / broken / log-x / log-log axes, log-log power-law fit, IsoFLOPs-style scatter. Each template is one .py file producing one subplot. Shared `style.py` sets Palatino body + STIX math (matching arxiv `mathpazo`) and a Google-brand palette softened to a paper-friendly tier (`brand → medium → paper → soft → mute`, switchable in one line). Labels ship pre-genericized (`Model A`, `Metric A`, `Task A`) to keep the templates portable; replace with real names when applying.

Template dir: `~/.claude/plugins/marketplaces/wenhaochai/writing/skills/plot/`. Copy the chosen template plus `style.py` to your figures directory, edit the data block, add a `fig.savefig(...)` call, run.

## Install

```
/plugin marketplace add wenhaochai/claude-plugins
/plugin install daily@wenhaochai
/plugin install writing@wenhaochai
```

## Optional config

Config lives at `~/.claude/plugins/daily/config.json`:

```json
{
  "calendars": ["foo@example.com"],
  "email_account": "you@example.com"
}
```

- `calendars` — extra Google Calendars to include in `/daily:todo`'s today view (primary is always included)
- `email_account` — restrict `/daily:email` to a specific Gmail account (defaults to the primary)

Both are optional.

## Conventions

- All dates are `MM/DD/YYYY`.
- `/daily:todo` and `/daily:wrap` operate on the project's working directory (`./TODO.md`, `./memory/`).
- `/daily:email` and `/daily:todo`'s calendar feature require corresponding MCP servers to be connected.

## License

MIT for plugin code. The `writing` plugin's `skills/writing-style/SKILL.md` contains rules redistributed from [agent-style](https://github.com/yzhao062/agent-style) under CC BY 4.0; attribution is preserved in that file.
