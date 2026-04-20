---
description: Manage TODO.md (show / add / complete / delete / update via natural language) and show today's calendar.
argument-hint: [natural language description, e.g. "加一条 买菜" / "买菜完成了" / "删掉 健身"]
---

Manage `./TODO.md` (project root by default). Supports read and write via a single command — the caller passes a natural-language description as `$ARGUMENTS`; branch on intent.

- **No arguments** → read-only rendering (see "Read mode" below).
- **With arguments** → infer intent (add / complete / delete / update) from the natural-language description and edit `./TODO.md` accordingly (see "Write mode" below).

---

## TODO.md format (authoritative)

Every item follows this shape:

```markdown
- [ ] Item title
  - 备注：short note
  - 提醒：MM/DD/YYYY or 每天
  - 完成：MM/DD/YYYY (only when completed)
```

Rules:

- Dates use `MM/DD/YYYY`.
- Keep the title short; put detail in notes.
- On update, **append** a dated note (`- MM/DD: ...`). Do not overwrite existing notes.
- Preserve original quoted content (emails, Slack messages, replies) using `>` blockquotes.
- Use `- 状态：...` to mark current progress (e.g. `等待回复` / `已完成`).
- Group items under `## <category>` headers (e.g. `财务/报销`, `工作/沟通`, `生活/杂务`, `每月固定`, `每年固定`). Pick the best fit; if none obvious, create a new one or put under a `## 杂项` section.
- If `TODO.md` does not exist, create it with a minimal header and the relevant category.

---

## Project entries

The `## 项目` section tracks ongoing active projects (multi-week / multi-month trackers), distinct from single-shot TODOs. Entries follow the same checkbox schema with these extra rules:

### Creation

- **Verify the path on the filesystem first** (Glob / Bash). Do not guess. If the path doesn't exist, don't create the entry — ask the user to clarify.
- Peek at the project's `README.md` / main entry file (e.g. `main.tex`, `pyproject.toml`) to extract a one-line description and core stack.
- **Required first note**: `- 路径：<path relative to TODO.md's directory>` (e.g. `../my-project/`, `../paper-repo/`).
- Remaining notes: short description + core stack. **No meta annotations** ("原 X 条目搬入", "见 Y 合并", etc.) — the entry itself is the content, not a changelog of how it was built.

### Updates

Same rules as regular TODOs: append dated notes (`- MM/DD：...`), never overwrite, preserve quoted content with `>` blockquotes, use `- 状态：...` for current progress.

**Refresh status from git**: when the user triggers `/daily:todo` or asks to "update project status", `cd` into each project's path and run `git log --oneline -8` + `git status --short` + `git branch --show-current`. Extract the latest progress from commit messages / branch name / uncommitted files and append as today's `- MM/DD：...` note. Do not write status from memory — the whole point of project entries is that status tracks git.

### Read-mode behavior

- Project entries are **always shown** (persistent trackers, not date-bound). The "hide if blocked / >7 days away" filter does not apply to the `## 项目` section.
- Render each as a compact one-liner: `- [ ] <name> — <状态 or next step>`.

---

## Read mode (no arguments)

Render the actionable items right now.

### Filter rules

- If an item has a "提醒/Remind" date that is **more than 7 days away**, hide it.
- If the item's notes indicate it is currently un-actionable (e.g. "waiting for reply", "blocked on X"), hide it.
- Monthly/yearly recurring items: only show those whose next reminder is within 7 days.
- Completed items (`[x]`) are hidden.
- Items marked "提醒：每天" / "Remind: daily" are **always** shown.

### Auto-cleanup

- Delete `[x]` items whose completion date is more than 7 days old (read the `- 完成：MM/DD/YYYY` / `- Done: MM/DD/YYYY` line under the item).
- Before deleting, append the full content (notes, progress log, quoted messages) to `./memory/YYYY-MM-DD.md` (today's date). If that file already exists, append separated by `---`.

### Output format

- Group by category; skip categories with no visible items.
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

Match against these patterns (Chinese or English):

| Intent | Typical phrasing |
|---|---|
| **add** | "加一条 …", "新增 …", "记一下 …", "add …", "remember to …" |
| **complete** | "… 做完了", "… 完成了", "搞定 …", "done with …", "finished …" |
| **delete** | "删掉 …", "不要 … 了", "remove …", "drop …" |
| **update** | "更新 …", "… 改成 …", "… 加个备注 …", "update …", "note on …" |

If the phrasing does not clearly match any, or the target item is ambiguous (multiple possible matches), ask a clarifying question instead of guessing.

### Add

- Generate a short title; put supplied detail in `- 备注：...`.
- If the user gave a date ("下周一提醒我", "5/1 之前"), convert to `MM/DD/YYYY` in the user's local timezone and write `- 提醒：MM/DD/YYYY`.
- If the user said "每天" / "daily", write `- 提醒：每天`.
- Pick the best category header; create a new one only if no existing fits.
- Report the insertion: path, category, title.

### Complete

- Locate the item by matching keywords against titles (and, if needed, against notes). Pick the best single match; if multiple plausible, ask.
- Change `- [ ]` to `- [x]`.
- Append `- 完成：MM/DD/YYYY` (today's date, user local timezone).
- Report the match + change.

### Delete

- Locate by the same matching rules as complete.
- Before deleting, append the full item (title + all notes, unmodified) to `./memory/YYYY-MM-DD.md`, separated by `---` if the file already has content.
- Remove the item from `TODO.md`.
- Report what was removed and where it was archived.

### Update

- Locate the item.
- **Append** a new note line; do not edit existing notes unless the user explicitly says "改 X 为 Y".
- New notes use the dated prefix if they are progress updates: `- MM/DD：...`.
- If the user supplied quoted content (email excerpt, message), preserve it with `>` blockquotes.
- Report the appended note.

### General safety

- Never delete a non-`[x]` item without explicit delete intent.
- Never bulk-edit multiple items from a single natural-language instruction unless the user's phrasing clearly pluralizes ("把 X 和 Y 都删了").
- After any write, show a compact diff (3–6 lines) so the user can verify.

---

## Date and timezone

- All dates: `MM/DD/YYYY`.
- "Today", "now", and relative dates resolve in the user's local timezone.
