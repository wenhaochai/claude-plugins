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

## Project entries

The `## 项目` section tracks ongoing active projects (multi-week / multi-month trackers), distinct from single-shot TODOs. Same live-metadata + history-log schema, with these extras:

### Creation

- **Verify the path on the filesystem first** (Glob / Bash). Do not guess. If the path doesn't exist, don't create the entry — ask the user to clarify.
- Peek at the project's `README.md` / main entry file (e.g. `main.tex`, `pyproject.toml`) to extract a short description and core stack.
- **First line is always `- 路径：<path relative to TODO.md's directory>`** (e.g. `../my-project/`). This sits above `- 备注：`.
- `- 备注：` holds the live one-liner: current phase + next action (not historical blurb).
- No meta annotations ("原 X 条目搬入", "见 Y 合并") — the entry is the content.

### Updates

Follow the standard Update rules (see Write mode below). For projects, `- 备注：` typically captures current branch / phase / blocker in one sentence.

**Refresh status from git**: when the user triggers `/daily:todo` or asks to "update project status", `cd` into each project's path and run `git log --oneline -8` + `git status --short` + `git branch --show-current`. Then:

1. **Rewrite `- 备注：`** to reflect the latest state + next action (derived from commits / branch / uncommitted files).
2. **Prepend a new `- MM/DD：...` history entry** with the concrete git-derived progress (key commits, branch name, uncommitted files).

Do not write status from memory — the whole point of project entries is that status tracks git.

### Read-mode behavior

- Project entries are **always shown** (persistent trackers, not date-bound). The "hide if blocked / >7 days away" filter does not apply.
- Render each as a compact one-liner: `- [ ] <name> — <备注 content>`.

---

## Read mode (no arguments)

Render the actionable items right now.

### Filter rules

- If an item has a `- 提醒：MM/DD/YYYY` more than 7 days away, hide it.
- If `- 备注：` indicates currently un-actionable ("等 X 审批", "waiting for reply", "blocked on"), hide it.
- Monthly/yearly recurring items: only show those whose next reminder is within 7 days.
- Completed items (`[x]`) are hidden.
- Items with `- 提醒：每天` / `Remind: daily` are **always** shown.

### Auto-cleanup

- Delete `[x]` items whose `- 完成：MM/DD/YYYY` is more than 7 days old.
- Before deleting, append the full content (title + 备注 + all history entries + quoted blockquotes) to `~/.claude/memory/<完成日期>.md` — using the item's **completion date**, not today, so same-day completions stay in one file. If the file exists, append separated by `---`.

### Output format

- Group by category; skip empty categories.
- End with a one-liner: `X items need attention, Y hidden as not currently actionable`.

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
- Report the insertion: path, category, title.

### Complete

- Locate by keyword match. If multi-match, ask.
- Change `- [ ]` to `- [x]`.
- **Rewrite `- 备注：`** as the final-state one-liner (what actually got done, outcome).
- **Remove** the `- 提醒：` line.
- **Add** `- 完成：MM/DD/YYYY` (today, user local timezone) below 备注.
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

If the user supplies quoted content, preserve it verbatim inside the new history entry.

If the update surfaces multiple stale `- 提醒：` lines on the item (legacy data from before this schema), consolidate: keep the most urgent still-actionable one as the live 提醒, and demote the rest into history entries phrased like `- MM/DD：原计划 X/Y 做 Z（已被 … 替代 / 已完成 / 取消）`.

Do not edit existing history entries unless the user explicitly says "改 MM/DD 那条为 X".

Report the changes (备注 rewrite + 提醒 change + new history entry) as a 3–6 line diff for the user to verify.

### General safety

- Never delete a non-`[x]` item without explicit delete intent.
- Never bulk-edit multiple items from a single natural-language instruction unless the phrasing clearly pluralizes ("把 X 和 Y 都删了").
- After any write, show a compact diff (3–6 lines) so the user can verify.

---

## Date and timezone

- All dates: `MM/DD/YYYY`.
- "Today", "now", and relative dates resolve in the user's local timezone.
