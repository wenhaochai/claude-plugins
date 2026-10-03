---
type: llm
focus: last_message
weight: 2
---
Ground truth: the camera-ready is NOT clean. appendix/extra.tex (pulled in by \input) still contains a red mark, \textcolor{red}{Double-check the 16k number against run 0412.}, and main.log shows an overfull \hbox 12.3pt too wide in sections/body.tex, past the usual 5pt tolerance. Everything else is fine.

PASS if the answer tells the user it is not ready to send yet AND names the leftover red mark in the appendix file AND flags the overfull box as needing a fix.

FAIL if it says the paper is clean or ready, or misses either the appendix red mark or the overfull box.
