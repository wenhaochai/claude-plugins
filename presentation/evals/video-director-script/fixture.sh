#!/usr/bin/env bash
# A small project page with its own canvas animation and data, the source for an explainer video.
set -euo pipefail
mkdir -p site video

cat > site/data.json <<'EOF'
{
  "title": "Greedy Loses the Long Race",
  "takeaway": "Looking two steps ahead beats grabbing the nearest reward on 81% of maps.",
  "maps": 200,
  "planner_wins": 162,
  "example_map": {
    "grid": [12, 8],
    "rewards": [[2, 1, 1], [3, 1, 1], [9, 6, 5], [10, 6, 5]],
    "greedy_path": [[0, 0], [2, 1], [3, 1], [5, 3], [9, 6], [10, 6]],
    "planner_path": [[0, 0], [4, 3], [9, 6], [10, 6], [3, 1], [2, 1]],
    "greedy_steps": 31,
    "planner_steps": 24,
    "mean_greedy_steps": 30.6,
    "mean_planner_steps": 24.9
  }
}
EOF

cat > site/index.html <<'EOF'
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Greedy Loses the Long Race · Halcyon Lab</title>
<style>
  :root { --ink: #1B1B1F; --paper: #FAF8F2; --accent: #C2410C; --muted: #6B6B73; }
  body { margin: 0; background: var(--paper); color: var(--ink); font-family: 'Source Sans 3', sans-serif; }
  header { display: flex; align-items: center; gap: 12px; padding: 16px 32px; }
  header svg { width: 28px; height: 28px; }
  .kicker { color: var(--accent); letter-spacing: 2px; font-weight: 600; }
  h1 { font-family: 'Fraunces', serif; font-size: 56px; font-weight: 500; }
  canvas { width: 960px; height: 540px; display: block; }
</style>
</head>
<body>
<header>
  <svg viewBox="0 0 28 28"><circle cx="14" cy="14" r="12" fill="#C2410C"/><path d="M8 18 L14 8 L20 18 Z" fill="#FAF8F2"/></svg>
  <span>Halcyon Lab</span>
</header>
<main>
  <p class="kicker">NEW RESEARCH · OCTOBER 2026</p>
  <h1>Greedy Loses the Long Race</h1>
  <p class="byline">Mira Okafor and Dev Patel · 2 October 2026</p>

  <h2>1. Two agents, one map</h2>
  <p>A greedy agent always walks to the nearest reward. A planner looks two steps ahead before it moves.</p>
  <canvas id="race" width="1920" height="1080"></canvas>

  <h2>2. The race</h2>
  <p>On the example map the greedy agent grabs the two close rewards first and then has to cross the whole map. The planner takes the far pair first and finishes in 24 steps instead of 31.</p>

  <h2>3. Across 200 maps</h2>
  <p>Looking two steps ahead beats grabbing the nearest reward on 81% of maps.</p>
</main>
<script>
// The page's own animation: both agents walk their paths on the example map, in real time.
fetch('data.json').then(r => r.json()).then(d => {
  const c = document.getElementById('race'), ctx = c.getContext('2d');
  const m = d.example_map, cell = 120, ox = 240, oy = 60;
  const P = (p) => [ox + p[0] * cell + cell / 2, oy + p[1] * cell + cell / 2];
  function along(path, u) {            // position along a path, u in [0, 1]
    const seg = (path.length - 1) * u, i = Math.min(Math.floor(seg), path.length - 2), f = seg - i;
    const a = P(path[i]), b = P(path[i + 1]);
    return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f];
  }
  function draw(now) {
    const u = (now / 6000) % 1;
    ctx.fillStyle = '#FAF8F2'; ctx.fillRect(0, 0, c.width, c.height);
    ctx.strokeStyle = '#E4E1D8';
    for (let x = 0; x <= m.grid[0]; x++) { ctx.beginPath(); ctx.moveTo(ox + x * cell, oy); ctx.lineTo(ox + x * cell, oy + m.grid[1] * cell); ctx.stroke(); }
    for (let y = 0; y <= m.grid[1]; y++) { ctx.beginPath(); ctx.moveTo(ox, oy + y * cell); ctx.lineTo(ox + m.grid[0] * cell, oy + y * cell); ctx.stroke(); }
    ctx.fillStyle = '#C2410C';
    m.rewards.forEach(r => { const [x, y] = P(r); ctx.beginPath(); ctx.arc(x, y, 18, 0, 7); ctx.fill(); });
    [['#6B6B73', m.greedy_path], ['#1B1B1F', m.planner_path]].forEach(([col, path]) => {
      const [x, y] = along(path, u); ctx.fillStyle = col; ctx.beginPath(); ctx.arc(x, y, 26, 0, 7); ctx.fill();
    });
    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
});
</script>
</body>
</html>
EOF
