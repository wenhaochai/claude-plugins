#!/usr/bin/env bash
# Made-up loss curves (no measured results): three model sizes, loss against training compute.
set -euo pipefail
cat > runs.csv <<'EOF'
size,compute_flops,loss
125M,1e17,4.10
125M,3e17,3.71
125M,1e18,3.45
125M,3e18,3.31
125M,1e19,3.24
350M,3e17,3.82
350M,1e18,3.40
350M,3e18,3.12
350M,1e19,2.97
350M,3e19,2.89
1.3B,1e18,3.55
1.3B,3e18,3.08
1.3B,1e19,2.79
1.3B,3e19,2.63
1.3B,1e20,2.55
EOF
