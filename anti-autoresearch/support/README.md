# anti-autoresearch support files

The 13 skills sit in `anti-autoresearch/skills/`; this directory holds what they read: `tools/`,
`references/`, `schemas/`, `eval/`. Each SKILL.md resolves `ROOT="${CLAUDE_PLUGIN_ROOT}/support"`.

Adversarial self-audit gate for paper output: `/anti-autoresearch <paper-dir>` → fix every
verdict-bearing finding → re-run until `CLEAN_GIVEN_EVIDENCE`.

**Provenance:** vendored from [wanshuiyin/Anti-Autoresearch](https://github.com/wanshuiyin/Anti-Autoresearch)
(MIT, see `LICENSE.upstream`), v0.5 taxonomy: 46 integrity patterns A–H, 13 AIS, 2 advisory.
`skills/anti-autoresearch/` is the upstream `workflows/anti-autoresearch`. `skills/reviewer-discipline/`
is local, not upstream.

**Two local patches**, both applied to every SKILL.md:

1. `$(git rev-parse --show-toplevel 2>/dev/null || pwd)` → `"${CLAUDE_PLUGIN_ROOT}"`, so the bundled
   `tools/`, `references/`, and `schemas/` resolve inside the installed plugin.
2. `"${CLAUDE_PLUGIN_ROOT}/anti-autoresearch"` → `"${CLAUDE_PLUGIN_ROOT}/support"`, from the 2026-09-16
   split that moved these skills out of the `writing` plugin into their own.
3. The `$ROOT/tests/test_adjudicator.py` call in `skills/anti-autoresearch/SKILL.md` is dropped:
   upstream references that file but has never shipped it. Restore the line if a resync brings the
   file with it.

To resync with upstream: re-copy `skills/ workflows/ tools/ references/ schemas/ eval/` from a fresh
clone, re-apply both patches with a python string replace, never `sed` with a `|` delimiter, and keep
`skills/reviewer-discipline/`, which has no upstream counterpart.

Optional cross-model reviewer: `claude mcp add codex -- codex mcp-server`.
