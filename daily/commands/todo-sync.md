---
description: Two-way sync between TODO.md and Apple Reminders (Quick / Long lists).
---

Perform two-way sync between `./TODO.md` and Apple Reminders. Use `osascript` against AppleScript to read Reminders and diff against `TODO.md`.

**Only touch** the `Quick` and `Long` lists. Never modify any other list in Reminders.

When syncing, only move items from `Long` → `Quick` if the blocking condition has **actually been resolved** (e.g. the user explicitly says "the package arrived"). Do not promote items based on your own judgement.

## `Quick` list — actionable / requires ongoing attention

Items the user can act on now, plus recurring items (daily/weekly/monthly) that need ongoing attention.

- **Reminders → TODO.md**: items in `Quick` but missing in `TODO.md` → add to `TODO.md`.
- **Reminders → TODO.md**: items completed in `Quick` but not yet `[x]` in `TODO.md` → mark `[x]`.
- **TODO.md → Reminders**: new / completed / deleted / edited items → mirror to `Quick`.

## `Long` list — long-term / currently blocked

Items in passive-waiting state or with reminder dates far out.

- **Reminders → TODO.md**: items in `Long` but missing in `TODO.md` → add to `TODO.md`.
- **TODO.md → Reminders**: new / completed / deleted / edited items → mirror to `Long`.
- When a `Long` item becomes actionable (block resolved or reminder date close), move it to `Quick`.

## Common rules

- Reminder body format: leading `[Category]` followed by the full notes block from `TODO.md`.
- **Never touch** any list other than `Quick` and `Long`.

## Date format

Use `MM/DD/YYYY` everywhere.
