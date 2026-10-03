#!/usr/bin/env bash
# Rendered frames (stand-ins) and a project page with a video placeholder.
set -euo pipefail
mkdir -p frames site
# a 1x1 PNG stands in for each 1920x1080 frame; the case writes the encode script, it does not run it
png='iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='
for i in $(seq 1 12); do
  printf '%s' "$png" | base64 -d > "frames/f_$(printf '%04d' "$i").png"
done
cat > frames/README.txt <<'EOF'
Frames from director.js: f_0001.png ... f_3720.png, 1920x1080, 60 fps, 62 s.
Only the first frames are kept in this folder.
EOF

cat > site/index.html <<'EOF'
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Greedy Loses the Long Race</title></head>
<body>
<main>
  <h1>Greedy Loses the Long Race</h1>
  <!-- VIDEO: embed the explainer here -->
  <p>A greedy agent always walks to the nearest reward. A planner looks two steps ahead before it moves.</p>
</main>
</body>
</html>
EOF
