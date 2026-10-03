#!/usr/bin/env bash
# A three-slide deck with planted rule violations, for a read-only audit.
set -euo pipefail
mkdir -p deck/project/slides

cat > deck/project/deck.json <<'EOF'
{
  "v": 4,
  "createdOnFiles": {"v": 1, "at": "2026-09-28T10:00:00Z"},
  "title": "Agent Benchmarks Survey",
  "order": ["intro", "method", "leaderboard"],
  "sections": {"s0": {"description": "Survey", "start": "intro"}},
  "faces": {},
  "designSystems": []
}
EOF

# intro: decorative icons, the word campaign, a claim title
cat > deck/project/slides/intro.html <<'EOF'
<section id="intro" data-transition="fade" style="background:#F6F3EC; color:#15141A; font-family:'Inter Tight', Arial, sans-serif; padding:128px; display:flex; flex-direction:column; gap:40px">
  <div style="display:flex; flex-direction:column; gap:12px">
    <p style="font-size:24px; font-weight:600; letter-spacing:3px; text-transform:uppercase; color:#7A1A1A">Survey</p>
    <h2 style="font-family:'Newsreader', Georgia, serif; font-size:56px; font-weight:500; line-height:1.1">Agent benchmarks are broken and need fixing</h2>
  </div>
  <div style="display:flex; gap:48px">
    <div style="width:480px; display:flex; flex-direction:column; gap:16px"><p style="font-size:120px">🚀</p><p style="font-size:28px">Our evaluation campaign covered 14 suites.</p></div>
    <div style="width:480px; display:flex; flex-direction:column; gap:16px"><p style="font-size:120px">🧠</p><p style="font-size:28px">Most suites score with a model judge.</p></div>
  </div>
  <aside>This slide introduces the survey.<br>
这一页介绍这个综述。</aside>
</section>
EOF

# method: svg <text> labels, two click builds but one [click] mark, notes not in EN/ZH pairs
cat > deck/project/slides/method.html <<'EOF'
<section id="method" data-transition="fade" style="background:#F6F3EC; color:#15141A; font-family:'Inter Tight', Arial, sans-serif; padding:128px; display:flex; flex-direction:column; gap:40px">
  <div style="display:flex; flex-direction:column; gap:12px">
    <p style="font-size:24px; font-weight:600; letter-spacing:3px; text-transform:uppercase; color:#7A1A1A">Method</p>
    <h2 style="font-family:'Newsreader', Georgia, serif; font-size:56px; font-weight:500; line-height:1.1">Scoring pipeline</h2>
  </div>
  <svg width="1600" height="300" viewBox="0 0 1600 300">
    <rect x="0" y="100" width="400" height="100" fill="#E7E2D6"/><text x="40" y="160" font-size="28">Task prompt</text>
    <rect x="600" y="100" width="400" height="100" fill="#E7E2D6"/><text x="640" y="160" font-size="28">Agent run</text>
    <rect x="1200" y="100" width="400" height="100" fill="#E7E2D6"/><text x="1240" y="160" font-size="28">Judge score</text>
  </svg>
  <p data-build-in="fade 1" style="font-size:28px">The judge reads the final answer only.</p>
  <p data-build-in="fade 2" style="font-size:28px">Ties are broken by run length.</p>
  <aside>[click] The judge reads only the final answer, so intermediate steps never affect the score that is reported in the paper tables.<br>
The second point is that ties are broken by run length.<br>
<br>
评委只看最终答案。</aside>
</section>
EOF

# leaderboard: eight rows, no uncertainty, claim title
cat > deck/project/slides/leaderboard.html <<'EOF'
<section id="leaderboard" data-transition="fade" style="background:#F6F3EC; color:#15141A; font-family:'Inter Tight', Arial, sans-serif; padding:128px; display:flex; flex-direction:column; gap:40px">
  <div style="display:flex; flex-direction:column; gap:12px">
    <p style="font-size:24px; font-weight:600; letter-spacing:3px; text-transform:uppercase; color:#7A1A1A">Leaderboard</p>
    <h2 style="font-family:'Newsreader', Georgia, serif; font-size:56px; font-weight:500; line-height:1.1">Orion-3 is the best agent</h2>
  </div>
  <div style="display:flex; flex-direction:column; gap:8px">
    <p style="font-size:28px">1. Orion-3 &nbsp; 61.2</p>
    <p style="font-size:28px">2. Kestrel &nbsp; 59.8</p>
    <p style="font-size:28px">3. Juniper-XL &nbsp; 58.9</p>
    <p style="font-size:28px">4. Basalt &nbsp; 55.0</p>
    <p style="font-size:28px">5. Marlin-2 &nbsp; 54.1</p>
    <p style="font-size:28px">6. Tamarack &nbsp; 50.3</p>
    <p style="font-size:28px">7. Quill &nbsp; 48.7</p>
    <p style="font-size:28px">8. Fennel &nbsp; 47.2</p>
  </div>
  <aside>Orion-3 leads with 61.2, then Kestrel at 59.8, Juniper-XL at 58.9, Basalt at 55.0 and Marlin-2 at 54.1.<br>
<br>
Orion-3 以 61.2 领先。</aside>
</section>
EOF
