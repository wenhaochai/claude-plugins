#!/usr/bin/env bash
# A storyboard for a one-minute explainer that breaks the author's video design rules.
set -euo pipefail

cat > storyboard.md <<'EOF'
# Explainer video: "Greedy Loses the Long Race"

Source page: site/index.html (Halcyon Lab). Output: 1280x720, 30 fps, about 60 s.

## Scene 1 (0-6 s): opening card
Dark title card. Kicker "NEW RESEARCH · OCTOBER 2026" at the top, the title in the middle,
"Mira Okafor and Dev Patel · Halcyon Lab" under it, tagline "Smarter agents, shorter paths".
Hard cut to scene 2.

## Scene 2 (6-18 s): two agents, one map
Heading "Two agents" at the top left, the map figure below it.
A bullet list stays on the right for the whole scene:
- Greedy: nearest reward first
- Planner: looks two steps ahead
- Same map, same start
The camera slowly zooms into the map while the agents appear.

## Scene 3 (18-40 s): the race
Show the formula on screen: cost(path) = sum of step lengths, plan = argmin over 2-step lookahead.
The two agents race on the example map. The planner wins every one of the three races we show.
We picked map #117, where the planner's lead is the largest of all 200 maps (14 steps).
Each race plays at the same speed. The camera pans to follow the leading agent.

## Scene 4 (40-55 s): across 200 maps
Hard cut to a bar chart card with the heading "Results". Caption on top of the bars:
"Planning is the future of embodied agents."
Bars: planner wins 162, greedy wins 38.

## Scene 5 (55-60 s): end card
URL "halcyon.example/greedy" in the bottom-left corner, our logo top-left.
Closing line: "Plan ahead · win more".
EOF
