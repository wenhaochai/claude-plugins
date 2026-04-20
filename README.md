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

## `paper` — academic paper writing style

Ships a skill (`paper-style`) that auto-triggers when editing `.tex` files or reviewing paper drafts. 17 rules: 12 canonical (Strunk & White / Orwell / Pinker / Gopen & Swan, sourced from [agent-style](https://github.com/yzhao062/agent-style) under CC BY 4.0) plus 5 additions for page-capped conference papers (no em-dashes or prose parens, no overview paragraphs, minimal `\emph`/`\textbf`, researcher voice, space economy under page caps).

No slash command. The skill loads whenever the writing context matches.

## Install

```
/plugin marketplace add wenhaochai/claude-plugins
/plugin install daily@wenhaochai
/plugin install paper@wenhaochai
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

MIT for plugin code. The `paper` plugin's `skills/paper-style/SKILL.md` contains rules redistributed from [agent-style](https://github.com/yzhao062/agent-style) under CC BY 4.0; attribution is preserved in that file.
