---
type: regex
pattern: '<aside>(?:(?:(?!</aside>)[\s\S])*?(?:78\.1|74\.0|72\.5|69\.9|70\.2|66\.8|73\.2|67\.5|63\.0|54\.8)){7}'
match: not_contains
target: {source: file, path: deck/project/slides/results.html}
---

The script says what the numbers show and does not read out the suite scores: at most six suite scores are spoken, counting the Chinese lines, so one pair said in both languages plus one more passes and a read-out of the list fails.
