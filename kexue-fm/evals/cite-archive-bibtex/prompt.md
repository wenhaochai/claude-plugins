---
description: Gives a bare archive link (post 11854, Aug 2026) and asks for a summary plus BibTeX. Tests show-by-id and returning the stored bibtex verbatim instead of an invented entry.
tags: [kexue]
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Bash, Skill]
---
https://kexue.fm/archives/11854 这篇我想在论文的 related work 里引用。先用三四句话告诉我它讲了什么，再给我它的 BibTeX。
