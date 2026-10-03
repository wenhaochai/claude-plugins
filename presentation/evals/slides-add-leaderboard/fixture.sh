#!/usr/bin/env bash
# A one-slide deck plus a leaderboard export with nine models and published 95% intervals.
set -euo pipefail
mkdir -p deck/project/slides data

cat > deck/project/deck.json <<'EOF'
{
  "v": 4,
  "createdOnFiles": {"v": 1, "at": "2026-09-28T10:00:00Z"},
  "title": "Agent Arena, October Update",
  "order": ["cover"],
  "sections": {"s0": {"description": "Title", "start": "cover"}},
  "faces": {
    "newsreader": {"family": "Newsreader", "href": "https://fonts.googleapis.com/css2?family=Newsreader:wght@400;500&display=swap"},
    "inter-tight": {"family": "Inter Tight", "href": "https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;600&display=swap"}
  },
  "designSystems": []
}
EOF

cat > deck/project/slides/cover.html <<'EOF'
<section id="cover" data-transition="fade" style="background:#15141A; color:#EDE9DE; font-family:'Inter Tight', Arial, sans-serif; padding:128px; display:flex; flex-direction:column; justify-content:space-between">
  <p style="font-size:24px; font-weight:600; letter-spacing:3px; text-transform:uppercase; color:#D0705F">Group meeting</p>
  <div style="display:flex; flex-direction:column; gap:32px">
    <h1 style="font-family:'Newsreader', Georgia, serif; font-size:120px; font-weight:500; line-height:1.05; color:#EDE9DE">Agent Arena, October Update</h1>
    <p style="font-size:36px; line-height:1.3; color:#BDB8AC; width:1300px">Where the public agent leaderboard stands</p>
  </div>
  <div style="display:flex; justify-content:space-between; border-top:1px solid #3A3842; padding:32px 0 0 0">
    <p style="font-size:28px; color:#EDE9DE">Presented by Lin</p>
    <p style="font-size:28px; color:#BDB8AC">October 2026</p>
  </div>
  <aside>Today I give a short update on the agent leaderboard.<br>
今天简单更新一下 agent 排行榜。</aside>
</section>
EOF

cat > data/agent_arena_leaderboard.csv <<'EOF'
# Agent Arena public leaderboard, exported 2026-10-01 from the leaderboard page
# score = Elo-style rating; ci_low/ci_high = bootstrap 95% confidence interval published by the arena
rank,model,score,ci_low,ci_high,votes
1,Orion-3,1312,1301,1323,18420
2,Kestrel-Pro,1298,1288,1309,15210
3,Juniper-XL,1291,1279,1302,12034
4,Basalt-2,1270,1258,1283,9877
5,Marlin-Ultra,1262,1249,1275,8840
6,Tamarack-7B,1231,1215,1246,4410
7,Quillwort,1219,1202,1236,3902
8,Fennelbrook,1203,1184,1221,2875
9,Sorrelline,1188,1166,1209,1630
EOF
