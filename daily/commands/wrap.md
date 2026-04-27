---
description: Summarize the current conversation and persist it to memory/ for future sessions.
---

Summarize the entire current conversation and persist it so future sessions can recover context.

## Summary requirements

- Walk through the whole conversation, extract the load-bearing details.
- Organize along three axes:
  1. **What we discussed** — main topics and conclusions
  2. **What we did** — concrete actions (file edits, commands run, decisions made)
  3. **Open follow-ups** — anything unfinished or needing later attention
- Bullet-point style, terse. No need for full sentences.
- Match the conversation language by default.

## Filter rules — DO NOT record

- Pure how-to Q&A (e.g. "how do I ssh") — easily re-derivable, not worth saving.
- One-off trivial edits (renaming a config key, deleting a single TODO line) unless tied to a real decision.
- Small talk, greetings, meta about the conversation itself (e.g. "what does /wrap do").
- Anything already fully captured by code/file diffs — `git diff` is enough.
- Refused requests (e.g. "store my password"), unless the user explicitly wants the alternative recorded.

## Save location

- Append to `~/.claude/memory/YYYY-MM-DD.md` (today's date, global — not per-project).
- Create the directory if missing.
- If the file already exists, append separated by `---`.
- No frontmatter — write the content directly.
- Do **not** record open follow-ups here (those belong in `TODO.md`).

## After saving

- Show the summary to the user for confirmation.
- Suggest they can `/clear` now.

## Full archive mode

If the user's wrap request includes any of these signals, ALSO produce a full archive of the raw conversation — never instead of the summary. The summary still gets written exactly as above; full archive is added on top.

Trigger phrases (any one is enough):

- "存原文"
- "完整存档"
- "全文"
- "raw"
- "整个对话存下来"

### Steps

1. **Locate the current session JSONL.**
   - Project slug = current working directory with `/` replaced by `-`, leading `-` kept (e.g. `/Users/foo/bar/baz` → `-Users-foo-bar-baz`). Get CWD via `pwd`.
   - Pick the most recently modified `*.jsonl` under `~/.claude/projects/<slug>/`:
     `ls -t ~/.claude/projects/<slug>/*.jsonl | head -1`
   - This is the live session file Claude Code is appending to.

2. **Pick a semantic slug** based on the conversation's main topic — kebab-case, English, ~30–50 chars. Do **not** use the session-id. If `~/.claude/memory/YYYY-MM-DD-full-<slug>.{jsonl,md}` already exists for the same date and slug, append `-2`, `-3`, etc. (still no session-id fallback).

3. **Copy raw JSONL** (source of truth — keeps tool calls, system reminders, all metadata):

   ```bash
   cp <session-jsonl> ~/.claude/memory/YYYY-MM-DD-full-<slug>.jsonl
   ```

4. **Generate readable Markdown** to `~/.claude/memory/YYYY-MM-DD-full-<slug>.md`. Extract user + assistant text content in time order; for each message emit a `## [role] HH:MM` header followed by the text. Skip tool calls / tool results / system reminders / hook output — those stay in the JSONL. Recommended one-liner:

   ```bash
   python3 -c '
   import json, sys
   from datetime import datetime
   for line in open(sys.argv[1]):
       try: obj = json.loads(line)
       except Exception: continue
       msg = obj.get("message", {}) or {}
       role = msg.get("role") or obj.get("type")
       if role not in ("user", "assistant"): continue
       ts = obj.get("timestamp", "") or ""
       hhmm = ""
       try: hhmm = datetime.fromisoformat(ts.replace("Z","+00:00")).astimezone().strftime("%H:%M")
       except Exception: pass
       content = msg.get("content", "")
       if isinstance(content, list):
           text = "\n".join(c.get("text","") for c in content if isinstance(c, dict) and c.get("type")=="text")
       else:
           text = content or ""
       if not text.strip(): continue
       print(f"## [{role}] {hhmm}\n\n{text}\n")
   ' <session-jsonl> > ~/.claude/memory/YYYY-MM-DD-full-<slug>.md
   ```

5. **Cross-link from the regular summary.** At the top of the summary block you write this turn in `~/.claude/memory/YYYY-MM-DD.md` (after any project section heading the global CLAUDE.md prescribes), insert one line:

   ```
   完整归档：[jsonl](./YYYY-MM-DD-full-<slug>.jsonl) · [markdown](./YYYY-MM-DD-full-<slug>.md)
   ```

   So future reads of the daily memory can jump straight to the full transcript.

6. **Report** both archive paths to the user along with the summary.
