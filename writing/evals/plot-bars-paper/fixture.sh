#!/usr/bin/env bash
# Made-up accuracies (no measured results): four methods on three benchmarks.
set -euo pipefail
cat > results.csv <<'EOF'
method,benchmark,accuracy
Base,GSM8K,71.2
Base,MATH,34.5
Base,HumanEval,48.8
SFT,GSM8K,73.0
SFT,MATH,35.9
SFT,HumanEval,50.1
DPO,GSM8K,74.4
DPO,MATH,36.2
DPO,HumanEval,50.6
Ours,GSM8K,76.9
Ours,MATH,39.1
Ours,HumanEval,52.3
EOF
