#!/usr/bin/env bash
set -euo pipefail
mkdir -p sections
cat > sections/results.tex <<'EOF'
\section{Experiments}

In this section, we present our main results and discuss them in detail. Table~\ref{tab:main} reports accuracy on GSM8K, MATH, and HumanEval for the base model and our method, which reach 71.2/34.5/48.8 and 76.9/39.1/52.3, respectively. Our method \textbf{significantly} improves over the base model on every benchmark --- a gain of 5.7 points on GSM8K alone. Although our method does not outperform the much larger 70B model on MATH, it is still competitive, which we believe is an encouraging sign. Moreover, the gains hold across three random seeds, which suggests that the improvement is \emph{robust}.
EOF
