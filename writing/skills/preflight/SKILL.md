---
name: preflight
description: "Mechanical submission preflight for a LaTeX paper directory: compile gate, page count against the venue cap, build-log scan for undefined citations and overfull boxes, leftover placeholders and \\textcolor{red} marks, correspondence-problem density, and .bib hygiene. Deterministic, no model judgment. Run before any submission, before a co-author hand-off, and after stripping red marks. Triggers: \"preflight\", \"ready to submit?\", \"check the build\", \"投稿前检查\", \"能编译吗\"."
allowed-tools: Bash(*), Read
---

# Preflight

Six checks a model gets wrong and a script gets right. Run it before the paper goes anywhere.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/preflight/preflight.py" <paper-dir> --venue iclr
```

Flags: `--venue` picks the page cap (`neurips icml iclr cvpr iccv eccv acl emnlp colm aaai tmlr arxiv`,
default `arxiv`), `--main` names the root file (default `main.tex`), `--no-compile` skips the build
when latexmk is unavailable or the PDF is already current.

| Check | What it catches |
|---|---|
| 0.1 compile | `latexmk` exit status. A failure stops the run: reviewing un-compilable source produces unreliable output. |
| 0.2 page count | Total pages against the venue cap. The cap counts body pages, so a pass still needs your eyes on where the references start. |
| 0.3 build log | Undefined citations and references fail. Overfull hboxes over 5pt fail; smaller ones and underfull boxes warn. |
| 0.4 placeholders | `TODO`, `XXX`, `FIXME`, `TBD`, `[CITATION]`, lorem, and leftover `\textcolor{red}` from the previous review round. Commented-out lines are skipped. |
| 0.5 correspondence | Density of `, which` and `respectively` per file, the two constructions that force a reader to hold a long-range correspondence. Ranked, so you fix the worst file first. |
| 0.6 bib hygiene | Entries missing author, title, year, or venue; a year in the future, which usually means a hallucinated reference; an arXiv id parked in the title field. |

Exit status is 1 when any check fails, so it chains into a larger gate.

## Reading the output

Report the checklist verbatim at the top of whatever you write next: each line is already
`[PASS]` / `[WARN]` / `[FAIL]` with the detail attached. Fix every FAIL before drafting prose about
the paper. A WARN is a judgment call: a file with twelve `respectively` is worth a rewrite pass, a
file with one is not.

The script reads the tree and the build products. It never edits the paper.
