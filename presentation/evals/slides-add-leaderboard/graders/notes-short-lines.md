---
type: regex
pattern: '<aside>(?:(?!</aside>)[\s\S])*?(?:[^\s<]+[ \t]+){18}[^\s<]+'
match: not_contains
target: {source: file, path: deck/project/slides/leaderboard.html}
---

No line of the script runs past 18 words: the speaker reads the English in a second language.
