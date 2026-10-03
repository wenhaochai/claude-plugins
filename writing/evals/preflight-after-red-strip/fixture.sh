#!/usr/bin/env bash
# A camera-ready the user believes is clean: main.tex and the body are, but an \input'd appendix
# still holds one \textcolor{red}, and the last Overleaf log has a 12.3pt overfull hbox.
set -euo pipefail
mkdir -p cr/sections cr/appendix
cat > cr/main.tex <<'EOF'
\documentclass{article}
\usepackage{icml2026}
\usepackage{natbib,xcolor,amsmath,graphicx}
\title{Token Dropping for Long-Context Pretraining}
\begin{document}
\maketitle
\input{sections/body}
\bibliographystyle{icml2026}
\bibliography{refs}
\appendix
\input{appendix/extra}
\end{document}
EOF
cat > cr/sections/body.tex <<'EOF'
\section{Introduction}
Long-context pretraining spends most of its compute on tokens the loss barely uses
\citep{press2022alibi}. We drop the lowest-gradient half of tokens after the first epoch and
match the full-token loss at 64k context with 41\% less compute.
\section{Results}
At 64k context the dropped run reaches a validation loss of 2.184 against 2.181 for the full run.
EOF
cat > cr/appendix/extra.tex <<'EOF'
\section{Additional Results}
Table~\ref{tab:ctx} lists the loss at 8k, 16k, 32k and 64k context. The gap stays under 0.004 at
every length. \textcolor{red}{Double-check the 16k number against run 0412.} Token selection adds
1.3\% wall-clock overhead.
EOF
cat > cr/refs.bib <<'EOF'
@inproceedings{press2022alibi,
  author    = {Press, Ofir and Smith, Noah A. and Lewis, Mike},
  title     = {Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation},
  booktitle = {ICLR},
  year      = {2022}
}
EOF
cat > cr/main.log <<'EOF'
This is pdfTeX, Version 3.141592653-2.6-1.40.25 (TeX Live 2023) (preloaded format=pdflatex 2023.4.10)  3 OCT 2026 09:02
entering extended mode
**main.tex
(./main.tex
LaTeX2e <2022-11-01> patch level 1
(./sections/body.tex
Overfull \hbox (12.3pt too wide) in paragraph at lines 3--5
[]\OT1/ptm/m/n/10 Long-context pretraining spends most of its compute on tokens the loss barely uses

Underfull \hbox (badness 1810) in paragraph at lines 6--7
[]\OT1/ptm/m/n/10 At 64k context the dropped run reaches

) (./main.bbl) (./appendix/extra.tex) [1] [2] [3]
Output written on main.pdf (3 pages, 148220 bytes).
EOF
