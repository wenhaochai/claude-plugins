Read `./TODO.md` (project root by default) and surface the items that need attention right now. Optionally sync with Apple Reminders and show today's calendar events.

## Apple Reminders sync (only on `/todo sync`)

By default `/todo` only reads the local `TODO.md` and renders it. **Only when the user explicitly runs `/todo sync`** perform the Apple Reminders two-way sync described below.

When syncing, only move items from `Long` → `Quick` if the blocking condition has **actually been resolved** (e.g. the user explicitly says "the package arrived"). Do not promote items based on your own judgement.

## Filter rules

- If an item has a "提醒/Remind" date that is **more than 7 days away**, hide it.
- If the item's notes indicate it is currently un-actionable (e.g. "waiting for reply", "blocked on X"), hide it.
- Monthly/yearly recurring items: only show those whose next reminder is within 7 days.
- Completed items (`[x]`) are hidden.
- Items marked "提醒：每天" / "Remind: daily" are **always** shown.

## Auto-cleanup

- Delete `[x]` items whose completion date is more than 7 days old (read the `- 完成：MM/DD/YYYY` / `- Done: MM/DD/YYYY` line under the item).

## Output format

- Group by category, skip categories with no visible items.
- End with a one-liner: `X items need attention, Y hidden as not currently actionable`.

## Today's calendar (optional)

If a Google Calendar MCP is connected, also show today's events:

- Read the user's primary calendar. To include additional calendars, the user can list them in `~/.claude/plugins/todo/config.json` under `"calendars": ["foo@example.com"]`.
- Time range: today 00:00–23:59 in the user's local timezone.
- List events in chronological order with time and title; mark all-day events separately.
- If no events, show "No events today".

If no calendar MCP is connected, skip this section silently.

## Archiving

When `[x]` items are auto-cleaned (or when the user manually deletes an item), append the full content (notes, progress log, original messages) to `./memory/YYYY-MM-DD.md` (today's date). If that file already exists, append separated by `---`.

## Apple Reminders two-way sync (only on `/todo sync`)

Use `osascript` against AppleScript to read Reminders and diff against `TODO.md`.

### `Quick` list — actionable / requires ongoing attention

Items the user can act on now, plus recurring items (daily/weekly/monthly) that need ongoing attention.

- **Reminders → TODO.md**: items in `Quick` but missing in `TODO.md` → add to `TODO.md`.
- **Reminders → TODO.md**: items completed in `Quick` but not yet `[x]` in `TODO.md` → mark `[x]`.
- **TODO.md → Reminders**: new / completed / deleted / edited items → mirror to `Quick`.

### `Long` list — long-term / currently blocked

Items in passive-waiting state or with reminder dates far out.

- **Reminders → TODO.md**: items in `Long` but missing in `TODO.md` → add to `TODO.md`.
- **TODO.md → Reminders**: new / completed / deleted / edited items → mirror to `Long`.
- When a `Long` item becomes actionable (block resolved or reminder date close), move it to `Quick`.

### Common rules

- Reminder body format: leading `[Category]` followed by the full notes block from `TODO.md`.
- **Never touch** any list other than `Quick` and `Long`.

## Date format

Use `MM/DD/YYYY` everywhere.
