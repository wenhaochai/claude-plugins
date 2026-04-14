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

- Append to `./memory/YYYY-MM-DD.md` (today's date, project root).
- Create the directory if missing.
- If the file already exists, append separated by `---`.
- No frontmatter — write the content directly.
- Do **not** record open follow-ups here (those belong in `TODO.md`).

## After saving

- Show the summary to the user for confirmation.
- Suggest they can `/clear` now.
