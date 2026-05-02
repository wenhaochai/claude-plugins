---
description: Manage TODO.md (show / add / complete / delete / update via natural language) and show today's calendar.
argument-hint: [natural language description, e.g. "加一条 买菜" / "买菜完成了" / "删掉 健身"]
---

Manage `./TODO.md` (project root by default). Supports read and write via a single command — the caller passes a natural-language description as `$ARGUMENTS`; branch on intent.

- **No arguments** → read-only rendering (see "Read mode" below).
- **With arguments** → infer intent (add / complete / delete / update) from the natural-language description and edit `./TODO.md` accordingly (see "Write mode" below).

---

## TODO.md format (authoritative)

Every item has **live metadata** (always-fresh one-liner + at most one next reminder) plus an **append-at-top history log** of dated progress entries in reverse chronological order.

Active item:

```markdown
- [ ] Item title
  - 备注：one-line summary of current state + next action
  - 提醒：MM/DD/YYYY or 每天

  - MM/DD：latest update

  - MM/DD：earlier update
```

Completed item:

```markdown
- [x] Item title
  - 备注：final-state one-liner
  - 完成：MM/DD/YYYY

  - MM/DD：history entry
```

Core rules:

- Dates use `MM/DD/YYYY`.
- Titles stay short; detail goes in `- 备注：` (live one-liner) and history entries.
- **`- 备注：` is live, not append-only.** Rewrite it on every update so it reflects "current state + next action" in a single sentence. Old context is preserved by the history log below, not by stacking context inside 备注.
- **At most one `- 提醒：` per item**, pointing to the next actionable date. When a reminder becomes moot (passed, superseded by newer info, no longer relevant), replace it with the next one — or delete it if nothing's pending. Never accumulate multiple 提醒 lines.
- **History entries (`- MM/DD：...`) go in reverse chronological order** — newest directly under the metadata lines, older ones below, separated by blank lines. Never overwrite or reorder existing entries.
- Preserve quoted content (emails, Slack messages, replies) with `>` blockquotes inside the relevant history entry.
- **No emphasis noise**: avoid `**bold**`, `~~strikethrough~~`, italics. Plain prose only.
- Do not use a separate `- 状态：...` field — status folds into `- 备注：`.
- Group items under `## <category>` headers (e.g. `财务/报销`, `工作/沟通`, `生活/杂务`, `每月固定`, `每年固定`). Pick the best fit; if none obvious, create a new one or put under `## 杂项`.
- If `TODO.md` does not exist, create it with a minimal header and the relevant category.

---

## Activation status (active / inactive)

Each item is implicitly **active** unless explicitly marked inactive. Active items render on dashboards and in read mode; inactive ones stay in `TODO.md` (history preserved) but are hidden until reactivated.

### Schema

- **Active** (default) — no marker.
- **Inactive** — append `- 激活：否（<reason>）` as the last metadata line (after 备注 / 提醒 / 状态, before the blank line preceding history). Reason vocabulary:
  - `远期` — reminder is far out (~3+ weeks) and nothing actionable now
  - `等对方` — user side done, waiting on counterpart. Apply only when the user explicitly says so ("X 不激活" / "等对方就别激活了" etc.); never auto-set just because counterpart hasn't replied. Default for any "ball is on the other side" item is active.
  - `已用` — recurring item already used for the current cycle (e.g. annual credit consumed)
  - `用户标记` — explicitly set by the user, regardless of automatic logic

### Decision priority (high → low)

1. **User override beats everything.** "X 不激活" / "X 激活" → set as instructed, reason `用户标记`.
2. Otherwise apply `远期` / `已用` in that order. (`等对方` is never auto-applied — only via explicit user instruction.)
3. Otherwise active.

### Transitions

- **Add** — apply decision rules at creation; write the `- 激活：` line only if inactive.
- **Update** — if the update flips activation (counterpart replied → ball back on user; reminder approaches → actionable; far-future date → near), toggle the marker in the same edit (delete the line to activate, add it to deactivate). Don't keep stale activation state.
- **Complete / delete** — moot; drop the `- 激活：` line if present.

### Auto-activation (time-driven pre-flight)

Run this scan **on every invocation**, before applying read-mode filters or write-mode edits — so newly-near items surface naturally without the user having to touch them.

For each item with `- 激活：否（远期）`, look at the same item's `- 提醒：MM/DD/YYYY`. If the reminder is within 7 days of today's local date (today + 0..7), **delete the `- 激活：否（远期）` line in place**. "远期" literally means "the date is far"; once the date is near the reason no longer holds, and the item should resurface through the normal read filter.

Other inactive reasons (`等对方` / `已用` / `用户标记`) are not time-driven and stay untouched. Items without a `- 提醒：` line are also untouched (no anchor to compare against).

If the pre-flight flipped any items, prepend one line to the report so the user sees what just surfaced:

```
auto-activated (远期 → 临近): <title 1> (提醒 MM/DD), <title 2> (提醒 MM/DD)
```

If nothing flipped, say nothing.

---

## Read mode (no arguments)

Render the actionable items right now.

### Filter rules

- **Items with `- 激活：否（…）` are hidden** regardless of reminder or 备注 content. Activation is the durable explicit signal; the rules below remain dynamic.
- If an item has a `- 提醒：MM/DD/YYYY` more than 7 days away, hide it.
- If `- 备注：` indicates currently un-actionable ("等 X 审批", "waiting for reply", "blocked on"), hide it.
- Monthly/yearly recurring items: only show those whose next reminder is within 7 days.
- Completed items (`[x]`) are hidden.
- Items with `- 提醒：每天` / `Remind: daily` are **always** shown (overrides the 7-day rule, but not the inactive rule above).

### Auto-cleanup

- Delete `[x]` items whose `- 完成：MM/DD/YYYY` is more than 7 days old.
- Before deleting, append the full content (title + 备注 + all history entries + quoted blockquotes) to `~/.claude/memory/<完成日期>.md` — using the item's **completion date**, not today, so same-day completions stay in one file. If the file exists, append separated by `---`.

### Output format

- Group by category; skip empty categories.
- End with a one-liner: `X items need attention, Y hidden as not currently actionable, Z marked inactive`.

### Today's calendar (optional)

If a Google Calendar MCP is connected, also show today's events:

- Read the user's primary calendar. To include additional calendars, the user can list them in `~/.claude/plugins/todo/config.json` under `"calendars": ["foo@example.com"]`.
- Time range: today 00:00–23:59 in the user's local timezone.
- List events in chronological order with time and title; mark all-day events separately.
- If no events, show "No events today".

If no calendar MCP is connected, skip this section silently.

---

## Write mode (arguments present)

The argument is a free-form natural-language description. Infer intent; if ambiguous, ask the user before editing.

### Intent detection

| Intent | Typical phrasing |
|---|---|
| **add** | "加一条 …", "新增 …", "记一下 …", "add …", "remember to …" |
| **complete** | "… 做完了", "… 完成了", "搞定 …", "done with …", "finished …" |
| **delete** | "删掉 …", "不要 … 了", "remove …", "drop …" |
| **update** | "更新 …", "… 改成 …", "… 加个备注 …", "update …", "note on …" |

If the phrasing does not clearly match, or the target item is ambiguous (multiple candidates), ask before acting.

### Add

- Generate a short title.
- Write `- 备注：` as a one-liner reflecting what the user just said (current state + next action).
- If the user gave a date or "每天", add `- 提醒：MM/DD/YYYY` or `- 提醒：每天`. Otherwise omit.
- Pick the best existing category; create a new one only if nothing fits.
- Apply activation rules (see "Activation status" above): if the item lands inactive (远期 / 等对方 / 已用 / explicit user override), append `- 激活：否（<reason>）` as the last metadata line.
- Report the insertion: path, category, title.

### Complete

- Locate by keyword match. If multi-match, ask.
- Change `- [ ]` to `- [x]`.
- **Rewrite `- 备注：`** as the final-state one-liner (what actually got done, outcome).
- **Remove** the `- 提醒：` line.
- **Add** `- 完成：MM/DD/YYYY` (today, user local timezone) below 备注.
- **Drop** the `- 激活：否（…）` line if present (moot once completed).
- **Prepend** a `- MM/DD：...` history entry capturing how it was completed. Preserve any quoted content with `>` blockquotes.
- Report the match + change as a 3–6 line diff.

### Delete

- Locate by the same matching rules. Never delete a non-`[x]` item without explicit delete intent.
- Archive the full item (title + metadata + all history, unmodified) to `~/.claude/memory/<完成日期>.md` — using the item's 完成 date, not today. If no 完成 line (edge case), use today. If the file has content, separate with `---`.
- Remove the item from `TODO.md`.
- Report what was removed and where it was archived.

### Update

The most frequent operation. Four steps every time:

1. **Locate the item** — keyword match against title, then notes. If multi-match, ask.
2. **Rewrite `- 备注：`** — overwrite this line so it reflects the new current state + next action in a single sentence. Don't keep the old phrasing; the old context lives in history, not in 备注.
3. **Adjust `- 提醒：`** — if the existing reminder is still the next actionable thing, leave it. Otherwise replace it with the new next reminder, or delete the line if nothing's pending. **Never end up with more than one 提醒 line.**
4. **Prepend a new `- MM/DD：...` history entry** right under the metadata lines, above older history, separated by a blank line. This entry captures what happened today (what the user just told you). Preserve any quoted email/message content with `>` blockquotes indented inside the entry.
5. **Re-evaluate activation** — if the update flips the rule (counterpart replied → ball on user / reminder approaches → actionable / `远期` → 临近), toggle the `- 激活：否（…）` line accordingly. Don't leave stale activation state.

If the user supplies quoted content, preserve it verbatim inside the new history entry.

If the update surfaces multiple stale `- 提醒：` lines on the item (legacy data from before this schema), consolidate: keep the most urgent still-actionable one as the live 提醒, and demote the rest into history entries phrased like `- MM/DD：原计划 X/Y 做 Z（已被 … 替代 / 已完成 / 取消）`.

Do not edit existing history entries unless the user explicitly says "改 MM/DD 那条为 X".

Report the changes (备注 rewrite + 提醒 change + new history entry) as a 3–6 line diff for the user to verify.

### Duplicate detection (merge prompt)

Before **add** finalizes — and any time the user is reviewing existing items — scan `TODO.md` for entries that look like the same underlying task. Signals:

- Titles reduce to the same object + same verb (e.g. two entries that both amount to "follow up with X on Y")
- `- 备注：` / history of the existing item points at the same goal, counterpart, or blocking event as what's being added
- Same `## <category>` and overlapping reminder timeframe

When a likely duplicate is found, **do not silently add or edit**. Stop and ask the user, showing both candidates' titles + 备注 in 2–4 lines:

> "<existing title>" 和 "<new/other title>" 看着是同一件事，要 merge 吗？

If the user confirms merge:

- Keep the entry with the richer history as the base.
- Fold the other entry's unique 备注 fragments and any history entries into the base (preserve original dates on history entries).
- Pick the more urgent / specific reminder; drop the other.
- Remove the redundant entry.
- Report the merge as a 3–6 line diff.

If the user declines, proceed with the original intent unchanged.

This check is cheap — when in doubt, ask. Two near-duplicates silently coexisting is a worse outcome than one extra confirmation.

### General safety

- Never delete a non-`[x]` item without explicit delete intent.
- Never bulk-edit multiple items from a single natural-language instruction unless the phrasing clearly pluralizes ("把 X 和 Y 都删了").
- After any write, show a compact diff (3–6 lines) so the user can verify.

---

## Date and timezone

- All dates: `MM/DD/YYYY`.
- "Today", "now", and relative dates resolve in the user's local timezone.
