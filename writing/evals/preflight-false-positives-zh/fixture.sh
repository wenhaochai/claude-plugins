#!/usr/bin/env bash
# A NeurIPS draft whose only TODOs are decoys (commented lines, a \todo macro definition, a notes
# file). Real findings: one leftover \textcolor{red} in sections/method.tex, a "respectively"-heavy
# sections/analysis.tex, and .bib warnings (an arXiv id in a title, a missing booktitle).
set -euo pipefail
mkdir -p draft/sections draft/notes
cat > draft/main.tex <<'EOF'
\documentclass{article}
\usepackage{neurips_2026}
\usepackage{natbib,xcolor,amsmath}
\newcommand{\TODO}[1]{\textcolor{red}{TODO: #1}}
\providecommand{\FIXME}{\textcolor{red}{FIXME}}
\title{Rank Collapse in Mixture-of-Experts Routers}
\begin{document}
\maketitle
% TODO: replace title once Lin agrees
\input{sections/intro}
\input{sections/method}
\input{sections/analysis}
\bibliographystyle{plainnat}
\bibliography{refs}
\end{document}
EOF
cat > draft/sections/intro.tex <<'EOF'
\section{Introduction}
Mixture-of-experts routers assign each token to a few experts \citep{shazeer2017moe,fedus2022switch}.
We show that the router's logit matrix loses rank during training and that a one-line
normalization prevents it.
%TODO cite the DeepSeek report here
% FIXME: numbers below are from the old run
EOF
cat > draft/sections/method.tex <<'EOF'
\section{Method}
Let $W \in \mathbb{R}^{E \times d}$ be the router weight for $E$ experts. We normalize each row of
$W$ to unit norm after every optimizer step. \textcolor{red}{Lin: does this still hold with
shared experts?} The cost is one division per expert per step.
EOF
cat > draft/sections/analysis.tex <<'EOF'
\section{Analysis}
The 8-expert and 64-expert routers reach effective ranks of 7.1 and 22.4, respectively. With
normalization, the two routers reach 7.9 and 58.2, respectively, which matches the bound. Top-1
and top-2 routing lose 3.2 and 1.4 points of rank per 10k steps, respectively. The baseline and
normalized runs reach losses of 2.31 and 2.27, respectively, which is within seed noise. Load
balance and rank, which we measure separately, move together. Shared and routed experts show
ranks of 5.0 and 21.7, respectively, which is expected from their token counts.
EOF
cat > draft/refs.bib <<'EOF'
@inproceedings{shazeer2017moe,
  author    = {Shazeer, Noam and Mirhoseini, Azalia and Maziarz, Krzysztof and others},
  title     = {Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer},
  booktitle = {ICLR},
  year      = {2017}
}

@article{fedus2022switch,
  author  = {Fedus, William and Zoph, Barret and Shazeer, Noam},
  title   = {Switch Transformers: Scaling to Trillion Parameter Models (arXiv:2101.03961)},
  journal = {JMLR},
  year    = {2022}
}

@inproceedings{dai2024deepseekmoe,
  author = {Dai, Damai and others},
  title  = {DeepSeekMoE: Towards Ultimate Expert Specialization},
  year   = {2024}
}
EOF
cat > draft/notes/citations_todo.md <<'EOF'
TODO: find the DeepSeek-V3 router ablation and add it to refs.bib.
EOF
