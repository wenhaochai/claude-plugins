#!/usr/bin/env bash
# An ICLR draft with four seeded problems: a live TODO (intro.tex), a leftover \textcolor{red}
# (experiments.tex), a citation key missing from the .bib (reported in main.log), and a .bib
# entry dated 2031. Commented TODOs and the \todo macro definition are decoys the check must skip.
set -euo pipefail
mkdir -p paper/sections
cat > paper/main.tex <<'EOF'
\documentclass{article}
\usepackage{iclr2025_conference,times}
\usepackage{natbib,xcolor,amsmath,booktabs}
\newcommand{\todo}[1]{\textcolor{red}{TODO: #1}}
\title{Sparse Rollouts for Cheap Reasoning}
\begin{document}
\maketitle
\input{sections/intro}
\input{sections/method}
\input{sections/experiments}
\bibliographystyle{iclr2025_conference}
\bibliography{refs}
\end{document}
EOF
cat > paper/sections/intro.tex <<'EOF'
\section{Introduction}
Reasoning models spend most of their inference budget on rollouts that agree with each other
\citep{wang2023selfconsistency}. Sampling fewer rollouts saves compute but loses accuracy when the
problem is hard \citep{snell2024scaling}. We ask which rollouts can be skipped without changing the
final answer. Our method keeps 31\% of rollouts and matches full self-consistency on four benchmarks;
TODO add the AIME number once the rerun finishes. Agentic pipelines face the same trade-off
\citep{liu2024agents}.
% TODO: tighten this paragraph before camera-ready
EOF
cat > paper/sections/method.tex <<'EOF'
\section{Method}
Let $x$ be a problem and $y_1, \dots, y_k$ be $k$ sampled rollouts. We stop sampling once the
leading answer holds a majority that the remaining budget cannot overturn \citep{chen2031omni}.
% XXX old derivation removed
EOF
cat > paper/sections/experiments.tex <<'EOF'
\section{Experiments}
We evaluate on GSM8K \citep{cobbe2021gsm8k}, MATH \citep{hendrycks2021math}, and two held-out sets.
Sparse rollouts reach 91.4 on GSM8K with 31\% of the samples. \textcolor{red}{Rerun with the new
seed before submission.} The saving grows with the sample budget.
EOF
cat > paper/refs.bib <<'EOF'
@inproceedings{wang2023selfconsistency,
  author    = {Wang, Xuezhi and Wei, Jason and Schuurmans, Dale and Le, Quoc and Chi, Ed and Narang, Sharan and Chowdhery, Aakanksha and Zhou, Denny},
  title     = {Self-Consistency Improves Chain of Thought Reasoning in Language Models},
  booktitle = {ICLR},
  year      = {2023}
}

@article{snell2024scaling,
  author  = {Snell, Charlie and Lee, Jaehoon and Xu, Kelvin and Kumar, Aviral},
  title   = {Scaling LLM Test-Time Compute Optimally Can Be More Effective than Scaling Model Parameters},
  journal = {arXiv preprint},
  year    = {2024}
}

@article{cobbe2021gsm8k,
  author  = {Cobbe, Karl and Kosaraju, Vineet and Bavarian, Mohammad and others},
  title   = {Training Verifiers to Solve Math Word Problems},
  journal = {arXiv preprint},
  year    = {2021}
}

@inproceedings{hendrycks2021math,
  author    = {Hendrycks, Dan and Burns, Collin and Kadavath, Saurav and others},
  title     = {Measuring Mathematical Problem Solving With the MATH Dataset},
  booktitle = {NeurIPS},
  year      = {2021}
}

@inproceedings{chen2031omni,
  author    = {Chen, Wei and Zhao, Lin},
  title     = {Omni-Stopping: Early Exit for Sampled Reasoning},
  booktitle = {ICML},
  year      = {2031}
}
EOF
cat > paper/main.log <<'EOF'
This is pdfTeX, Version 3.141592653-2.6-1.40.25 (TeX Live 2023) (preloaded format=pdflatex 2023.4.10)  2 OCT 2026 21:14
entering extended mode
**main.tex
(./main.tex
LaTeX2e <2022-11-01> patch level 1
(./sections/intro.tex

LaTeX Warning: Citation `liu2024agents' on page 1 undefined on input line 7.

) (./sections/method.tex) (./sections/experiments.tex) (./main.bbl)

LaTeX Warning: There were undefined references.

 )
Output written on main.pdf (4 pages, 211873 bytes).
EOF
