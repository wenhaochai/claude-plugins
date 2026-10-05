---
type: regex
pattern: '^(?=(?:(?!<aside>)[\s\S])*78\.1)(?=(?:(?!<aside>)[\s\S])*74\.0)(?=(?:(?!<aside>)[\s\S])*72\.5)(?=(?:(?!<aside>)[\s\S])*69\.9)(?=(?:(?!<aside>)[\s\S])*70\.2)(?=(?:(?!<aside>)[\s\S])*66\.8)(?=(?:(?!<aside>)[\s\S])*73\.2)(?=(?:(?!<aside>)[\s\S])*67\.5)(?=(?:(?!<aside>)[\s\S])*63\.0)(?=(?:(?!<aside>)[\s\S])*54\.8)(?=(?:(?!<aside>)[\s\S])*71\.4)(?=(?:(?!<aside>)[\s\S])*66\.2)'
match: contains
target: {source: file, path: deck/project/slides/results.html}
---

The visible slide, before <aside>, keeps all ten suite numbers and both averages.
