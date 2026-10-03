---
type: llm
focus: {source: file, path: deck/project/slides/leaderboard.html}
---

The file is one slide in an HTML subset; its <aside> holds the speaker script. The data has nine models with an Elo-style score and a published bootstrap 95% interval (ci_low, ci_high), exported 2026-10-01; the top five are Orion-3 1312 [1301, 1323], Kestrel-Pro 1298 [1288, 1309], Juniper-XL 1291 [1279, 1302], Basalt-2 1270 [1258, 1283], Marlin-Ultra 1262 [1249, 1275].

PASS if all of the following hold:
1. Exactly the top five models appear, in rank order, each with its score.
2. Each of the five shows its interval, drawn as a band or whisker or printed as numbers.
3. The slide title is a noun label that names the interval (for example "Agent Arena rating, 95% interval") and makes no claim such as "Orion-3 is the best".
4. A source line names the arena and the read date.
5. The notes are pairs of one English line (one sentence, at most 18 words) and its Chinese line, separated by blank lines, and they say in words what the ranking shows instead of reading every score aloud.

FAIL if any of the five does not hold.
