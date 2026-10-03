---
type: llm
focus: {source: file, path: video/director.js}
---

The script should draw the frame at time t of a roughly one-minute video about the page "Greedy Loses the Long Race" (Halcyon Lab). The page has a kicker "NEW RESEARCH · OCTOBER 2026", a byline with two author names and a date, a grid map with a greedy and a planner agent, and the takeaway "Looking two steps ahead beats grabbing the nearest reward on 81% of maps."

PASS if at least five of these six hold:
1. The frame is a pure function of a time or frame-index argument, laid out for 60 fps (for example a frame count of about 3600 or t = i / 60), with no real-time animation loop driving the content.
2. The opening frame is a cover: the title over the map (the source's key picture). The opening shows no kicker, no author names, no date line and no tagline.
3. The Halcyon Lab mark (its logo and name) is drawn small in the bottom-right corner on every frame, and no other corner carries text such as a URL.
4. No whole-frame camera move: no time-dependent scale or translate applied to the entire canvas to zoom or pan; motion comes from the objects.
5. On-screen copy is quoted from the page (title, agent names, the 24 vs 31 steps, the takeaway verbatim at the end) and adds no invented summary or slogan lines; no formulas on screen.
6. Captions appear one at a time next to the action and leave before the next one enters; there is no persistent bullet list or text column.

FAIL if two or more do not hold.
