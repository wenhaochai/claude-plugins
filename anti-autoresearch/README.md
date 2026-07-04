# anti-autoresearch (plugin)

Adversarial self-audit gate for paper output: `/anti-autoresearch <paper-dir>` → fix every
verdict-bearing finding → re-run until `CLEAN_GIVEN_EVIDENCE`.

**Provenance:** vendored from [wanshuiyin/Anti-Autoresearch](https://github.com/wanshuiyin/Anti-Autoresearch)
(MIT, see `LICENSE.upstream`), v0.5 taxonomy (46 integrity patterns A–H + 13 AIS + 2 advisory).
Local patch: every `$(git rev-parse --show-toplevel 2>/dev/null || pwd)` in the SKILL.md files is
replaced with `"${CLAUDE_PLUGIN_ROOT}"` so the bundled `tools/`, `references/`, `schemas/` resolve
inside the installed plugin. `skills/anti-autoresearch/` is the upstream `workflows/anti-autoresearch`.

To resync with upstream: re-copy `skills/ workflows/ tools/ references/ schemas/ eval/` from a fresh
clone and re-apply the root-path patch (python replace, NOT sed with `|` delimiter).

Optional cross-model reviewer: `claude mcp add codex -- codex mcp-server`.
