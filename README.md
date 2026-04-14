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

## Install

```
/plugin marketplace add wenhaochai/claude-plugins
/plugin install daily@wenhaochai
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

MIT
