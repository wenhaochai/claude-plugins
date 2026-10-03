---
type: llm
focus: {source: file, path: deck/project/slides/results.html}
---

The file is one slide in an HTML subset; its <aside> holds the speaker script.

PASS if all of the following hold:
1. The slide title (the <h2>) is a short noun label for what is shown, such as "Accuracy by suite", and makes no claim; it is not a comma-joined list of clipped phrases like "Sparse routing wins, beats dense, cheaper to train".
2. The visible slide keeps the data: all five suites with both numbers (78.1/74.0, 72.5/69.9, 70.2/66.8, 73.2/67.5, 63.0/54.8) and the averages 71.4 and 66.2 still appear on the slide or in its chart labels.
3. The long paragraph is gone from the slide: at most one short sentence per block is visible.
4. The notes are a script of pairs: each English line (one sentence, at most 18 words) is followed by its Chinese translation line, with blank lines (<br><br>) between pairs.
5. The notes describe what the numbers show in words and do not read out the full list of numbers.

FAIL if any of the five does not hold, or if the file is not a single <section id="results"> with the <aside> as its last child.
