---
description: Spawn another remote-control Claude Code instance inside the current SSH session via detached tmux. Use when the parent CC is itself remote-controlled (cannot send TTY shortcuts) and the user wants a sibling CC URL to drive in parallel.
argument-hint: [optional tmux session name; defaults to first free `c<N>` with N≥2]
---

Spawn a sibling Claude Code instance in a **detached** `tmux` session and return its `/remote-control` URL. Everything goes through the Bash tool — the parent CC cannot send key shortcuts to the underlying TTY.

## When to use

All of the following must hold:

- User is on a remote machine (typically via SSH).
- The currently-running Claude Code is itself remote-controlled.
- User wants a *new* Claude Code session they can open at `https://claude.ai/code/session_<id>` and drive in parallel — e.g. delegate a long task while the current one keeps going.

Do **not** use this for: starting claude in the foreground (use the shell directly), spawning on a different host (this skill assumes localhost), or attaching to an already-running tmux session (use `tmux a` directly).

## Prerequisites (one-shot check)

Run this first; abort and report to the user if anything prints `MISSING:`. Installing tmux / claude or doing first-run setup is on the user.

```bash
command -v tmux >/dev/null || echo "MISSING: tmux"
command -v claude >/dev/null || echo "MISSING: claude"
[ -f "$HOME/.claude.json" ] || echo "MISSING: ~/.claude.json (run claude once interactively first)"
[ -d "$HOME/.claude" ] || echo "MISSING: ~/.claude"
```

## Step 1 — Pick a non-conflicting tmux session name

`$ARGUMENTS` may contain a desired session name. If empty, auto-pick the first free `c<N>` with N≥2:

```bash
SESSION="$ARGUMENTS"
if [ -z "$SESSION" ]; then
  for i in 2 3 4 5 6 7 8 9; do
    if ! tmux has-session -t "c$i" 2>/dev/null; then SESSION="c$i"; break; fi
  done
fi
[ -z "$SESSION" ] && { echo "ERROR: c2-c9 all taken; pass an explicit name"; exit 1; }
echo "Using session: $SESSION"
```

If `$ARGUMENTS` is given but the name is already taken, abort with a clear message — do **not** silently rename, and do **not** kill the old one (it may be a sibling the user is actively driving).

Persist `$SESSION` between bash calls by exporting it or by re-deriving it; do not assume the variable survives across separate Bash tool invocations.

## Step 2 — Start `claude` detached in tmux

```bash
tmux new -d -s "$SESSION" -x 200 -y 50 claude
sleep 5
tmux capture-pane -t "$SESSION" -p | tail -30
```

- `-x 200 -y 50` is **not optional**: narrower panes wrap the session URL across two lines and the Step 5 regex won't match.
- `sleep 5` is also **not optional** — claude needs ~5 s to render its first prompt. Shorter sleeps race the next step.

## Step 3 — Handle the trust dialog (if it appears)

If the Step 2 capture contains `Is this a project you created or one you trust?`, claude is waiting for confirmation. Send Enter (default selection = "Yes, I trust"), then re-capture:

```bash
tmux send-keys -t "$SESSION" Enter
sleep 3
tmux capture-pane -t "$SESSION" -p | tail -20
```

Verify the input prompt `❯` is visible before continuing. The trust dialog appears the first time claude is started in a working directory; subsequent spawns from the same directory skip it.

If the capture from Step 2 already shows `❯` and no trust prompt, **skip this step**.

## Step 4 — Send `/remote-control`

```bash
tmux send-keys -t "$SESSION" '/remote-control' Enter
sleep 6
tmux capture-pane -t "$SESSION" -p | tail -20
```

`sleep 6` is the slowest of the three — `/remote-control` takes 3-6 s to print the URL on first call.

## Step 5 — Extract the URL

```bash
tmux capture-pane -t "$SESSION" -p | grep -oE 'https://claude\.ai/code/session_[A-Za-z0-9]+' | head -1
```

If empty, the URL hasn't rendered yet (or got wrapped because the pane is too narrow). `sleep 4` and retry the grep once. If still empty, capture the full pane (`tmux capture-pane -t "$SESSION" -p`) and report what you see — do **not** retry indefinitely.

## Report to the user

```
✅ Spawned `<name>` → https://claude.ai/code/session_<id>
   Kill when done: tmux kill-session -t <name>
```

## Cleanup helpers

| What | Command |
| --- | --- |
| Kill this spawned instance | `tmux kill-session -t <name>` |
| Peek at live screen | `tmux capture-pane -t <name> -p` |
| Attach (if user has a TTY) | `tmux a -t <name>` |
| List all sessions | `tmux ls` |

The spawned claude is fully detached from the SSH session: dropping the SSH connection does **not** kill it.

## Common pitfalls

- **Don't shorten the `sleep`s.** The 5 s / 3 s / 6 s waits correspond to real startup phases (cold-start render, dialog dismiss, `/remote-control` URL render). Faster sleeps capture half-rendered TUI; the regex then misses and you waste a retry round.
- **Always check for the trust dialog before Step 4.** Even if the user thinks the directory was trusted before, a fresh `~/.claude/projects/<dir>` entry on a different host can re-trigger it.
- **Don't reuse a live session name.** `tmux new -d -s c2` errors if `c2` exists. Do not pass `-A` or kill the old one — it may be a sibling the user is actively using.
- **Pane width matters.** `-x 80` (the typical default) wraps the URL onto two lines and the regex misses. Always pass `-x 200 -y 50`.
- **Recursion works.** A spawned claude can call `/daily:spawn-remote` to spawn *its* sibling, and so on. The only constraint is unique session names.
- **The spawned claude inherits the parent's cwd.** If the user wants the new instance to start somewhere else, do that change yourself — `cd` first, or wrap the launch as `tmux new -d -s "$SESSION" -x 200 -y 50 -c <path> claude`.
