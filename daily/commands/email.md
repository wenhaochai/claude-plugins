Show a summary of recent unread Gmail messages.

Requires a Gmail MCP server to be connected. Operates on the user's default Gmail account. To restrict to a specific account, the user can set `"account": "you@example.com"` in `~/.claude/plugins/email/config.json`.

## Query rules

- Use the Gmail MCP `search_threads` tool with query `is:unread`.
- Pull at most 20 most recent unread threads; show at most 10 after filtering.
- For each surviving thread, fetch the body and produce a one-sentence summary.

## Filter rules

Skip these categories — do not display:

- Promotions / ads (travel deals, merchant promos, loyalty offers)
- Security/login notifications (Google security alert, Slack new-device sign-in, etc.)
- Facilities / parking / construction notices
- Mailing-list blasts (unless the content is directly relevant to the user)
- Other clearly no-action-needed notification mail

## Output format

- Sort newest first.
- Each line: `sender · time · subject — one-sentence summary`.
- Footer: `X unread total (showing Y most recent)`.
- If nothing remains after filtering, show "No unread mail".
