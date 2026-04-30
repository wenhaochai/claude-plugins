"""Template 30: log-log power-law fit — scatter + linear fit line.

Use when: showing a clean power-law relationship `y = a · C^b`. Renders both
the closed-form line (for projection) and sample data points (for fit
provenance). Math label puts the exponent in the legend.
"""
import numpy as np
import matplotlib.pyplot as plt
from style import apply_style, paper, G_BLUE

apply_style()

color = paper(G_BLUE)

# Underlying law: log10(y) = log10(40) + 0.47 * (log10(C) - 18.5)
C_line = np.logspace(18.5, 25, 60)
y_line = 10 ** (np.log10(40) + 0.47 * (np.log10(C_line) - 18.5))

C_pts = np.logspace(18.7, 21, 6)
y_pts = 10 ** (np.log10(40) + 0.47 * (np.log10(C_pts) - 18.5))

fig, ax = plt.subplots(figsize=(4.0, 3.0), constrained_layout=True)

ax.plot(C_line, y_line, color=color, linewidth=2.0,
        label=r'Modality A: $C^{0.47}$')
ax.scatter(C_pts, y_pts, s=70, color=color,
           edgecolor='white', linewidth=1.0, zorder=3)

ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Compute (FLOPs)')
ax.set_ylabel('Optimal Parameters (M)')
ax.set_title(r'$N_{\mathrm{opt}}$: Modality A')
ax.legend(loc='upper left')
ax.grid(which='both', linestyle='--', alpha=0.4)
