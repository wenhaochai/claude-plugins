# claude-plugins

Personal Claude Code plugin marketplace by [Wenhao Chai](https://wenhaochai.com).

## Plugins

| Plugin | Command | What it does |
|---|---|---|
| `todo` | `/todo` | Show actionable items from `./TODO.md`, with optional Apple Reminders sync (`/todo sync`) and today's calendar events |
| `email` | `/email` | Summarize recent unread Gmail messages (requires a Gmail MCP) |
| `wrap` | `/wrap` | Summarize the current conversation and append to `./memory/YYYY-MM-DD.md` |

## Install

```
/plugin marketplace add wenhaochai/claude-plugins
/plugin install todo@wenhaochai
/plugin install email@wenhaochai
/plugin install wrap@wenhaochai
```

Or install all at once:

```
/plugin install todo@wenhaochai email@wenhaochai wrap@wenhaochai
```

## Optional config

Some plugins read optional config from `~/.claude/plugins/<name>/config.json`:

- `todo` — `{"calendars": ["foo@example.com"]}` to include extra Google Calendars
- `email` — `{"account": "you@example.com"}` to restrict to a specific Gmail account

Both default to your primary / default account if the config file is absent.

## Conventions

- All dates are `MM/DD/YYYY`.
- `todo` and `wrap` operate on the project's working directory (`./TODO.md`, `./memory/`).
- `email` and `todo`'s calendar feature require corresponding MCP servers to be connected.

## License

MIT
