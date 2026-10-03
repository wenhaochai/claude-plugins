#!/usr/bin/env bash
# Made-up scores (no measured results): each agent's score at every iteration it ran. Scores go
# down as well as up, and agent B skips iteration 5.
set -euo pipefail
cat > scores.csv <<'EOF'
agent,iteration,score
Agent A,0,0.412
Agent A,1,0.455
Agent A,2,0.431
Agent A,3,0.502
Agent A,4,0.497
Agent A,5,0.518
Agent A,6,0.509
Agent A,7,0.533
Agent A,8,0.521
Agent A,9,0.540
Agent A,10,0.538
Agent B,0,0.398
Agent B,1,0.402
Agent B,2,0.447
Agent B,3,0.429
Agent B,4,0.471
Agent B,6,0.512
Agent B,7,0.496
Agent B,8,0.549
Agent B,9,0.531
Agent B,10,0.562
EOF
